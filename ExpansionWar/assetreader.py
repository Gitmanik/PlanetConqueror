import io
import zipfile
import logging

logger = logging.getLogger(__name__)

class AssetReader:
    def __init__(self, zip_path):
        self.assets = {}
        with zipfile.ZipFile(zip_path, 'r') as z:
            for asset_name in z.namelist():
                if asset_name.endswith('/'):
                    continue
                self.assets['/' + asset_name] = z.read(asset_name)

    def list_assets(self):
        return list(self.assets.keys())

    def read_asset(self, asset_name):
        if asset_name.startswith("/"):
            asset_name = asset_name[1:]
        asset_name = "/" + asset_name
        if asset_name not in self.assets:
            raise KeyError(f"Asset '{asset_name}' not found in assets file ")

        return io.BytesIO(self.assets[asset_name])

    def find(self, subdirectory):
        if subdirectory.startswith("/"):
            subdirectory = subdirectory[1:]
        subdirectory = "/" + subdirectory
        if not subdirectory.endswith("/"):
            subdirectory = subdirectory + "/"

        return [k[len(subdirectory):] for k,_ in self.assets.items() if k.startswith(subdirectory) and "/" not in k[len(subdirectory):]]

    def __getitem__(self, asset_name):
        return self.read_asset(asset_name)

    def __contains__(self, asset_name):
        return asset_name in self.assets
