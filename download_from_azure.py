from azure.storage.blob import BlobClient

blobconfig = BlobClient(account_url="https://STORAGE NAME.blob.core.windows.net",
                  container_name="CONTAINER NAME",
                  blob_name="BLOB NAME",
                  credential="ACCESS KEY")

with open("config.json", "wb") as f:
    data = blobconfig.download_blob()
    data.readinto(f)

blobmodel = BlobClient(account_url="https://STORAGE NAME.blob.core.windows.net",
                  container_name="CONTAINER NAME",
                  blob_name="BLOB NAME",
                  credential="ACESS KEY")

with open("BLOB NAME", "wb") as f:
    data = blobmodel.download_blob()
    data.readinto(f)

