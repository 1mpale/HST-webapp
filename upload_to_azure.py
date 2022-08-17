from azure.storage.blob import BlobClient

blob = BlobClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=vladimirstoragethesis;AccountKey=XdyCazpFWpyUs+iuKkS2yD4GZ+8GaAram/ltSwv2C8uG/hi7dvVKcFE9F3uGaqcbB7tAYWdUgIgY+AStxuPnQQ==;EndpointSuffix=core.windows.net", 
            container_name="config", blob_name="HST_full.sav")

with open("./HST_latest.sav", "rb") as data:
    blob.upload_blob(data, overwrite=True)