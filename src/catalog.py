from pyproj import Transformer
import planetary_computer
import pystac_client
        
def create_catalog(min_x = float, min_y = float, max_x = float, max_y = float, min_date = str):
    stac_client = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )
    
    transformer = Transformer.from_crs("EPSG:2193", "EPSG:4326", always_xy=True)
    min_x_wgs84, min_y_wgs84 = transformer.transform(min_x, min_y)
    max_x_wgs84, max_y_wgs84 = transformer.transform(max_x, max_y)
    
    catalog = stac_client.search(
        collections=["sentinel-2-l2a"],
        bbox=[min_x_wgs84, min_y_wgs84, max_x_wgs84, max_y_wgs84],
        datetime=f"{min_date}/2025-12-12"
    )

    return catalog