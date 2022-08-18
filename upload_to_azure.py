from azure.storage.blob import BlobClient

blob = BlobClient.from_connection_string(conn_str="", 
            container_name="config", blob_name="HST_full.sav")

with open("./HST_latest.sav", "rb") as data:
    blob.upload_blob(data, overwrite=True)