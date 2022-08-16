from azure.storage.blob import BlobClient

blob = BlobClient.from_connection_string(conn_str="CONNECTION STRING", 
            container_name="CONTAINER NAME", blob_name="BLOB NAME")

with open("BLOB NAME", "rb") as data:
    blob.upload_blob(data, overwrite=True)