from azure.storage.blob import BlobClient

blobconfig = BlobClient(account_url="https://vladimirstoragethesis.blob.core.windows.net",
                  container_name="config",
                  blob_name="config.json",
                  credential="")

with open("config.json", "wb") as f:
    data = blobconfig.download_blob()
    data.readinto(f)

blobmodel = BlobClient(account_url="https://vladimirstoragethesis.blob.core.windows.net",
                  container_name="config",
                  blob_name="HST_full.sav",
                  credential="")

with open("HST_full.sav", "wb") as f:
    data = blobmodel.download_blob()
    data.readinto(f)

