from abc import ABC, abstractmethod
from src.stack import Stack
import xarray as xr
import xrspatial.multispectral as ms
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import os 
import rioxarray

class Plot(ABC):
    def __init__(self, stack = Stack, min_x=float, min_y=float, max_x=float, max_y=float):
        self.stack = stack.stack
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.aggregates = []
        self.plots = []
        self.spectral_index = None 
    
    @abstractmethod
    def create_aggregates():
        pass
    
    def create_plot(self):
        
        self.create_aggregates()
        
        self.plots = []  # list to store plots

        print(f"Creating plots...")
        for i, img in enumerate(self.aggregates):
            if i % 5 == 0:
                print(f"{i}/{len(self.aggregates)}")
            
            img = img.copy()  # avoid view issues
            ax = img.plot.imshow(add_colorbar=False, extent=[self.min_x, self.min_y, self.max_x, self.max_y], origin="upper")   
            ax.axes.set_axis_off()                           
            self.plots.append(ax)                       
            plt.close()
    
    def show_plot(self, img_idx, show_title = True):
        ax = self.plots[img_idx].axes

        if show_title:
            ax.set_title(f"{self.get_capture_date(img_idx)}")
        
        return self.plots[img_idx].get_figure()
    
    
    def save_geotiff(self):
        current_wd = os.getcwd()
        directory = Path(f"{current_wd}/assets/{self.stack.aoi_name}/{self.spectral_index}")
        
        print(f"Saving rasters to {directory}...")
        
        if directory.exists():
            for file in directory.iterdir():
                if file.is_file():
                    file.unlink()
        else:
            directory.mkdir(parents=True)
            
        for idx, plot in enumerate(self.plots):
            arr = plot.get_array().data
            arr = arr.transpose(2, 0, 1)
        
            da = xr.DataArray(
                arr,
                dims=("band", "y", "x"),
                coords={"y": self.stack.y.values, "x": self.stack.x.values}
            )
            
            da = da.rio.write_crs("EPSG:2193")
            da.rio.to_raster(f"{directory}/{self.get_capture_date(idx)}.tif")
            
        print("Saved rasters.")
        
    def get_capture_date(self, img_idx):
        date_captured_utc = pd.to_datetime(self.stack.coords["time"].values[img_idx], utc=True)
        date_captured_nzt = str(date_captured_utc.tz_convert("Pacific/Auckland").strftime("%Y-%m-%d"))
        return date_captured_nzt

    
class TrueColourPlot(Plot):
    def __init__(self, stack = Stack, min_x=float, min_y=float, max_x=float, max_y=float):
        super().__init__(stack, min_x, min_y, max_x, max_y)
        self.spectral_index = 'True_Colour'
        
    def create_aggregates(self):
        self.aggregates = [ms.true_color(x.sel(band="Band 4 - Red - 10m"), x.sel(band="Band 3 - Green - 10m"), x.sel(band="Band 2 - Blue - 10m")) for x in self.stack]
        print("Created aggregates.")
