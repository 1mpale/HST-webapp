import collections
try:
    from collections import abc
    collections.MutableMapping = abc.MutableMapping
except:
    pass

from rest_framework.decorators import api_view
from rest_framework.response import Response
import base64
from.apps import PagesConfig
from river import stream
import datetime
import uuid
from pathlib import Path
import pandas as pd
from river import stream
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from django.http import HttpResponse
import matplotlib
from azure.storage.blob import ContainerClient
import yaml
import os
from azure.core.credentials import AzureNamedKeyCredential
from azure.data.tables import TableServiceClient
from azure.storage.blob import BlobClient


@api_view(['GET'])
def index(request):
    return_data = {
        "error_code" : "0",
        "info" : "success",
    }
    return Response(return_data)

@api_view(["POST"])
def prediction(request):
    try:
        credential = AzureNamedKeyCredential("vladimirstoragethesis", "XdyCazpFWpyUs+iuKkS2yD4GZ+8GaAram/ltSwv2C8uG/hi7dvVKcFE9F3uGaqcbB7tAYWdUgIgY+AStxuPnQQ==")
        service = TableServiceClient(endpoint="https://vladimirstoragethesis.table.core.windows.net/", credential=credential)
        string = request.data
        string = "".join(string.values())
        scores_list = []
        HST = PagesConfig.HST
        if base64.b64encode(base64.b64decode(string)).decode("utf-8") == string:
            data_for_validation = base64.b64decode(string)
            data_for_validation = data_for_validation.decode("utf-8")
            with open('decoded.csv', 'w') as out:
                out.write(data_for_validation)
            data_stream = stream.iter_csv(
                'decoded.csv',
                converters={
                    'name': int,
                    'id': int,
                    'self_size': int,
                    'edge_count': int,
                    'trace_node_id': int,
                    'detachedness': int,
                }
            )
            for x, y  in data_stream:
                score = HST.score_one(x)
                scores_list.append(score)    
            length_of_list = len(scores_list)
            summ_of_scores = sum(scores_list)
            average_score = summ_of_scores/length_of_list

            table_service_client = TableServiceClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=vladimirstoragethesis;AccountKey=XdyCazpFWpyUs+iuKkS2yD4GZ+8GaAram/ltSwv2C8uG/hi7dvVKcFE9F3uGaqcbB7tAYWdUgIgY+AStxuPnQQ==;EndpointSuffix=core.windows.net")
            #table_name = "scoreresults"
            #table_client = table_service_client.create_table(table_name=table_name)

            time = str(datetime.datetime.now())
            id = str(uuid.uuid4())
            
            blob = BlobClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=vladimirstoragethesis;AccountKey=XdyCazpFWpyUs+iuKkS2yD4GZ+8GaAram/ltSwv2C8uG/hi7dvVKcFE9F3uGaqcbB7tAYWdUgIgY+AStxuPnQQ==;EndpointSuffix=core.windows.net", container_name="imagestorage", blob_name=id)
            blob.upload_blob(string)

            base64string = 'https://myaccount.blob.core.windows.net/imagestorage/' + 'id'
            
            my_entity = {
                u'PartitionKey':id,
                u'RowKey': time,
                u'Average_Score': average_score,
                u'Base64': base64string
            }
            table_service_client = TableServiceClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=vladimirstoragethesis;AccountKey=XdyCazpFWpyUs+iuKkS2yD4GZ+8GaAram/ltSwv2C8uG/hi7dvVKcFE9F3uGaqcbB7tAYWdUgIgY+AStxuPnQQ==;EndpointSuffix=core.windows.net")
            table_client = table_service_client.get_table_client(table_name="scoreresults")
            table_client.create_entity(entity=my_entity)




        model_prediction = {
            'info': 'success',
            'average score': average_score,
            'timestamp': datetime.datetime.now(),
            'id': uuid.uuid4(),
            'Base64': string
        }

    except ValueError:
        model_prediction = {
            'error_code' : '406 Not Acceptable'
        }

    return Response(model_prediction)


@api_view(["GET"])
def visualization(request):
    matplotlib.pyplot.switch_backend('Agg') 
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_zlabel("x_composite_3")
    scores_list = []
    HST = PagesConfig.HST 
    path = Path(os.getcwd())
    for file in path.glob('*.csv'):
        data_stream = stream.iter_csv(
            file,
            converters={
                'name': int,
                'id': int,
                'self_size': int,
                'edge_count': int,
                'trace_node_id': int,
                'detachedness': int,
            }
        )
        for x, y in data_stream:
            score = HST.score_one(x)
            scores_list.append(score)
        df = pd.read_csv(file)
        df['anomaly_score'] = scores_list
        outliers=df.loc[df['anomaly_score']>0.99]
        outlier_index=list(outliers.index)
        pca = PCA(n_components=3)  # Reduce to k=3 dimensions
        scaler = StandardScaler()
        to_model_columns=df.columns[1:6]
        X = scaler.fit_transform(df[to_model_columns])
        X_reduce = pca.fit_transform(X)
        # Plot the compressed data points
        ax.scatter(X_reduce[:, 0], X_reduce[:, 1], zs=X_reduce[:, 2], s=4, lw=1, label="inliers",c="green")
        # Plot x's for the ground truth outliers
        ax.scatter(X_reduce[outlier_index,0],X_reduce[outlier_index,1], X_reduce[outlier_index,2],
            lw=2, s=60, marker="x", c="red", label="outliers")
        plt.draw
        date = str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        plt.savefig(date+".visualized.png")
        scores_list.clear() 

    image_data = open(date+".visualized.png", "rb").read()
    #with open("visualized.png", "rb") as image_file:
        #encoded_string = base64.b64encode(image_file.read())

    def load_config():
        path = os.getcwd()
        dir_root = os.path.join(path, r"uploadconfig.yaml")
        with open(dir_root, "r") as yamlfile:
            return yaml.load(yamlfile, Loader=yaml.FullLoader)
    config = load_config()    

    def get_files(dir):
        with os.scandir(dir) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith('png'):
                    yield entry   

    pictures = get_files(config["source_folder"])
    
    def upload(files, connection_string, container_name):
        container_client = ContainerClient.from_connection_string(connection_string, container_name)    
        for file in files:
            blob_client = container_client.get_blob_client(file.name)
            with open(file.path,"rb") as data:
                blob_client.upload_blob(data)
                path = os.getcwd()
                archive = os.path.join(path, r"archive")
                destination = os.path.join(archive, file.name)
                os.replace(file.path, destination)
    upload(pictures, config["azure_storage_connectionstring"], config["image_container_name"])
    
 
    return HttpResponse(image_data, content_type="image/png")  


