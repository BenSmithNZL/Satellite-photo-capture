from arcgis.features import FeatureLayer
from arcgis.geometry import Geometry
from arcgis.gis import GIS
import pandas as pd

def fetch_taskings(portal_url, client_id, client_secret, layer_url):
    print("Fetching taskings...")
    gis = GIS(
        portal_url,
        client_id=client_id,
        client_secret= client_secret
    )

    layer = FeatureLayer(layer_url)
    features = layer.query(where="1=1", out_fields="*", return_geometry=True, out_sr='2193')
    df = features.sdf
    extents = [Geometry(feature).extent for feature in df.SHAPE]

    df['min_x'] = [extent[0] for extent in extents]
    df['min_y'] = [extent[1] for extent in extents]
    df['max_x'] = [extent[2] for extent in extents]
    df['max_y'] = [extent[3] for extent in extents]
    
    print(f"Successfully fetched {len(df)} taskings.")

    return df