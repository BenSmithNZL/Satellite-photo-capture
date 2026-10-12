import stackstac
import numpy as np
from math import sqrt
from dask.distributed import Client

def asset_finder():
    pass

class Stack():
    def __init__(self, catalog=None, aoi_name=str, chunk_size_mib=float, assets=list[str], min_x=float, min_y=float, max_x=float, max_y=float):
        
        self.items = {}
        for item in catalog.items():
            dt = item.datetime    
            self.items[dt] = item

        self.items = list(self.items.values())
        self.aoi_name = aoi_name
        self.chunk_size_mib = chunk_size_mib
        self.assets = assets
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.FLOAT64_ELEMENT_SIZE = 8
        
    def get_chunk_size(self, chunk_size_mib, time, num_bands):
        chunk_size_bytes = chunk_size_mib * 1024 ** 2 
        return round(sqrt(chunk_size_bytes / (time * num_bands * self.FLOAT64_ELEMENT_SIZE)), 0) 
        
    def create_stack(self):
        print(f"Creating stack of {self.aoi_name} tasking...")
        
        self.stack = (
            stackstac.stack(
                self.items,
                epsg=2193,
                resolution=1,
                chunksize=round(sqrt((self.chunk_size_mib * 1024 ** 2 ) / self.FLOAT64_ELEMENT_SIZE)), # Somehow, usually gets correct chunk size
                assets=self.assets,  
                bounds = [self.min_x, self.min_y, self.max_x, self.max_y]
            )
            .where(lambda x: x > 0, other=np.nan)
            .assign_coords(band=lambda x: x.title.rename("band"))
            .assign_attrs(aoi_name=self.aoi_name)
        )
        
        print("Stack created.")

     
    def filter_cloud_cover(self, max_cloud_cover = float):
        scl = self.stack.sel(band="Scene classfication map (SCL)")
        cloud_fraction = scl.isin([8, 9, 10]).mean(dim=("x", "y"))
        cloud_free_times = cloud_fraction.where(cloud_fraction <= max_cloud_cover)
        cloud_free_times = cloud_free_times.dropna("time").time.values
        self.stack = self.stack.sel(time=cloud_free_times)
        
        #Rechunking
        chunk_size = self.get_chunk_size(self.chunk_size_mib, 1, 4)
        self.stack = self.stack.chunk({"time": 1, "band":-1,  "x": chunk_size, "y": chunk_size})


                