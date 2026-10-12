# Tasking-Driven Sentinel-2 Imagery Pipeline

Automatically turn an ArcGIS Portal "tasking" layer into analysis-ready Sentinel-2 imagery. Each tasking record describes an area of interest (AOI), a start date, a cloud-cover limit and the outputs required. The pipeline reads those records, searches an imagery catalog, builds a lazy, Dask-backed image stack per AOI, filters out cloudy scenes and exports true-colour GeoTIFFs.

## How it works

```
ArcGIS Portal tasking layer
        │
        ▼
 fetch_taskings()     → one row per AOI request
        │
        ▼
 create_catalog()     → single catalog search covering ALL taskings
        │
        │
        │                    
        ▼
 for each tasking:
   Stack.create_stack()    
   filter_cloud_cover()    
   TrueColourPlot          
```

Key design points:

- **One catalog query, many AOIs.** The catalog is built once from the combined extent and earliest start date of all taskings, then each AOI is cut from it, rather than querying per tasking.
- **Lazy, parallel processing.** Stacks are chunked (`CHUNK_SIZE_MIB`) and computed on a local [Dask](https://www.dask.org/) cluster (4 workers x 2 threads, 4 GiB each by default). The Dask dashboard link is printed on startup so you can monitor progress.
- **Tasking-controlled behaviour.** Cloud filtering and true-colour export are switched per record from the ArcGIS layer, so analysts can change what gets produced without touching code.

## Tasking layer schema

The feature layer at `TASKING_LAYER_URL` must expose these fields:

| Field | Description |
|---|---|
| `AOI_Name` | Name for the AOI; used to identify the stack and outputs |
| `min_x`, `min_y`, `max_x`, `max_y` | Bounding box of the AOI |
| `Start_Date` | Earliest acquisition date to consider |
| `Max_Cloud_Cover` | Cloud-cover threshold. A value of `1` skips cloud filtering |
| `True_Colour` | `1` to generate and save a true-colour GeoTIFF for the AOI |

## Bands

Each stack loads the following Sentinel-2 assets:

| Asset | Purpose |
|---|---|
| `B02` | Blue |
| `B03` | Green |
| `B04` | Red |
| `SCL` | Scene classification layer (used for cloud filtering) |

## Requirements

- Python 3.9+
- Access to an ArcGIS Portal with an application registered for client-credentials authentication
- Packages (see `requirements.txt`), including `dask[distributed]` plus the geospatial and catalog libraries used in `src/`


## Configuration

Settings live in `config.py`:

| Setting | Description |
|---|---|
| `PORTAL_URL` | URL of your ArcGIS Portal |
| `ARCGIS_PORTAL_CLIENT_ID` | OAuth client ID for your Portal app |
| `ARCGIS_PORTAL_CLIENT_SECRET` | OAuth client secret for your Portal app |
| `TASKING_LAYER_URL` | REST URL of the tasking feature layer |
| `CHUNK_SIZE_MIB` | Target Dask chunk size in MiB |

**Do not commit credentials.** Load the client ID and secret from environment variables or a `.env` file that is listed in `.gitignore`.

## Usage

```bash
python main.py
```

On startup the script launches a local Dask cluster and prints the dashboard URL. It then processes each tasking in turn and closes the cluster when finished.

### Tuning the Dask cluster

The cluster is defined in `main.py`:

```python
cluster = LocalCluster(n_workers=4, threads_per_worker=2, memory_limit="4GiB")
```

Adjust these values to match your machine. If workers run out of memory, reduce `CHUNK_SIZE_MIB` or the worker count.

## Output

For each tasking with `True_Colour = 1`, a true-colour GeoTIFF is written for that AOI. Output location and naming are handled by `TrueColourPlot.save_geotiff()`.

## Extending

- **New products:** add a flag field to the tasking layer (for example `NDVI`), then add a matching class in `src/raster.py` and a branch in the main loop.
- **Different bands:** change the `assets` list passed to `Stack`.

## Contributing

Issues and pull requests are welcome. Please open an issue first to discuss any substantial change.