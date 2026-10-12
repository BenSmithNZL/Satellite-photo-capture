from config import ARCGIS_PORTAL_CLIENT_ID, ARCGIS_PORTAL_CLIENT_SECRET, CHUNK_SIZE_MIB, PORTAL_URL, TASKING_LAYER_URL
from dask.distributed import Client, LocalCluster
from src.catalog import create_catalog
from src.raster import TrueColourPlot
from src.stack import Stack
from src.taskings import fetch_taskings


def main():
    
    # Re/start Dask client
    cluster = LocalCluster(n_workers=4, threads_per_worker=2, memory_limit="4GiB")
    client = Client(cluster)
    print(f"Dask dashboard: {client.dashboard_link}")
    
    # Get all taskings from ArcGIS Portal
    taskings = fetch_taskings(
        portal_url = PORTAL_URL, 
        client_id = ARCGIS_PORTAL_CLIENT_ID, 
        client_secret = ARCGIS_PORTAL_CLIENT_SECRET, 
        layer_url = TASKING_LAYER_URL
    )
    
    ### Create item catalog from all taskings
    catalog = create_catalog(
        min_x = min(taskings['min_x']), 
        min_y = min(taskings['min_y']),
        max_x = max(taskings['max_x']), 
        max_y = max(taskings['max_y']), 
        min_date = str(min(taskings['Start_Date']).date())
    )

    for index, tasking in taskings.iterrows():
        ### Create stack 
        stack = Stack(
            catalog=catalog, 
            aoi_name=tasking['AOI_Name'], 
            chunk_size_mib=CHUNK_SIZE_MIB, 
            assets=["B02", "B03", "B04", "SCL"], 
            min_x=tasking['min_x'], 
            min_y=tasking['min_y'], 
            max_x=tasking['max_x'], 
            max_y=tasking['max_y']
        )
        
        stack.create_stack()
        
        ### Filter out images with too much cloud cover.
        if tasking["Max_Cloud_Cover"] != 1:
            stack.filter_cloud_cover(tasking["Max_Cloud_Cover"])
    
        ### Save images to .tiffs
        if tasking["True_Colour"] == 1:
            plot = TrueColourPlot(stack)
            plot.create_plot()
            plot.save_geotiff()
            
    
    # Close Dask client
    client.close()
    cluster.close()

if __name__ == "__main__":
    main()