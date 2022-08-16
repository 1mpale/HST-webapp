from azure.storage.blob import BlobClient

blobconfig = BlobClient(account_url="https://vladimirstoragethesis.blob.core.windows.net",
                  container_name="config",
                  blob_name="config.json",
                  credential="XdyCazpFWpyUs+iuKkS2yD4GZ+8GaAram/ltSwv2C8uG/hi7dvVKcFE9F3uGaqcbB7tAYWdUgIgY+AStxuPnQQ==")

with open("config.json", "wb") as f:
    data = blobconfig.download_blob()
    data.readinto(f)

blobmodel = BlobClient(account_url="https://vladimirstoragethesis.blob.core.windows.net",
                  container_name="config",
                  blob_name="HST_full.sav",
                  credential="XdyCazpFWpyUs+iuKkS2yD4GZ+8GaAram/ltSwv2C8uG/hi7dvVKcFE9F3uGaqcbB7tAYWdUgIgY+AStxuPnQQ==")

with open("HST_full.sav", "wb") as f:
    data = blobmodel.download_blob()
    data.readinto(f)

