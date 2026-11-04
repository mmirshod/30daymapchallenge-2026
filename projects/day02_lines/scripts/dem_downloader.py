
from pathlib import Path
from urllib.request import urlretrieve
import math

BASE_URL = "https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com"
DEM_DIR = Path("data/raw/dem")
DEM_DIR.mkdir(parents=True, exist_ok=True)

extents = {
    "zomin": (67.15908691727962, 39.47051116712185, 69.60004669902848, 40.302517508770585),
    "pop": (69.7145217576645, 40.70670953593998, 71.98998739308314, 41.48230684525561),
}

tiles = set()
for xmin, ymin, xmax, ymax in extents.values():
    for lat in range(math.floor(ymin), math.ceil(ymax)):
        for lon in range(math.floor(xmin), math.ceil(xmax)):
            tiles.add((lat, lon))

for lat, lon in sorted(tiles):
    name = f"Copernicus_DSM_COG_10_N{lat:02d}_00_E{lon:03d}_00_DEM"
    output = DEM_DIR / f"{name}.tif"

    if output.exists() and output.stat().st_size > 0:
        print("Exists:", name)
        continue

    url = f"{BASE_URL}/{name}/{name}.tif"
    print("Downloading:", name)

    try:
        urlretrieve(url, output)
    except Exception as e:
        output.unlink(missing_ok=True)
        print("Failed:", name, e)

print("Finished")
  