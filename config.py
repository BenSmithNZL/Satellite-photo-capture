import os
from dotenv import load_dotenv

load_dotenv()

# from env
ARCGIS_PORTAL_CLIENT_ID = os.getenv("ARCGIS_PORTAL_CLIENT_ID")
ARCGIS_PORTAL_CLIENT_SECRET = os.getenv("ARCGIS_PORTAL_CLIENT_SECRET")

# static constants
PORTAL_URL = "https://maps.stdc.govt.nz/portal"
TASKING_LAYER_URL = "https://maps.stdc.govt.nz/server/rest/services/Aerial_Imagery/Satellite_image_taskings/FeatureServer/0"
CHUNK_SIZE_MIB = 250