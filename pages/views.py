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
import os
from azure.core.credentials import AzureNamedKeyCredential
from azure.data.tables import TableServiceClient
from azure.storage.blob import BlobClient
from azure.data.tables import TableClient
from datetime import timedelta
from azure.storage.blob import BlobClient, generate_blob_sas, BlobSasPermissions
from urllib.request import urlopen


@api_view(['GET'])
def index(request):
    return_data = {
        "error_code" : "0",
        "info" : "success",
    }
    return Response(return_data)

@api_view(["POST"])
def prediction(request):
    account_name = ''
    account_key = ''
    connection_string = ''
    try:
        credential = AzureNamedKeyCredential(account_name, account_key)
        service = TableServiceClient(endpoint="https://vladimirstoragethesis.table.core.windows.net/", credential=credential)
        string = request.data
        string = "".join(string.values())
        scores_list = []
        HST = PagesConfig.HST
        time = str(datetime.datetime.now())
        id = str(uuid.uuid4())
        if base64.b64encode(base64.b64decode(string)).decode("utf-8") == string:
            data_for_validation = base64.b64decode(string)
            data_for_validation = data_for_validation.decode("utf-8")
            fullname = os.path.join('./csvs/', id+".decoded.csv")
            with open(fullname, 'w') as out:
                out.write(data_for_validation)
            data_stream = stream.iter_csv(
                fullname,
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

            table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
            #table_name = "scoreresults"
            #table_client = table_service_client.create_table(table_name=table_name)
            
            blob = BlobClient.from_connection_string(conn_str=connection_string, container_name="imagestorage", blob_name=id)
            blob.upload_blob(string)

            blob = BlobClient.from_connection_string(conn_str=connection_string, container_name="fullscoreliststorage", blob_name=id)
            blob.upload_blob(str(scores_list))

            base64string = 'https://vladimirstoragethesis.blob.core.windows.net/imagestorage/' + id
            full_score_list = 'https://vladimirstoragethesis.blob.core.windows.net/fullscoreliststorage/' + id
            my_entity = {
                u'PartitionKey':time,
                u'RowKey': id,
                u'Average_Score': average_score,
                u'Base64': base64string,
                u'Full_Score_list': full_score_list
            }
            table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
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
    path = Path('./csvs')

    def sort_files():
        dir_name = Path('./csvs')
    # Get list of all files only in the given directory
        list_of_files = filter(lambda x: os.path.isfile(os.path.join(dir_name, x)),
                           os.listdir(dir_name))
    # Sort list of files based on last modification time in ascending order
        list_of_files = sorted(list_of_files,
                           key=lambda x: os.path.getmtime(os.path.join(dir_name, x)),reverse=True
                           )
        lastfile= list_of_files[-100:]
        return lastfile
    last100 = sort_files()
    for file in path.glob('*.csv'):
        if file.name in last100:
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
            scores_list.clear() 
    pathtosaveimage = os.path.join('./currentimage/', date+".visualized.png")
    plt.savefig(pathtosaveimage)
    image_data = open(pathtosaveimage, "rb").read()
    #with open("visualized.png", "rb") as image_file:
        #encoded_string = base64.b64encode(image_file.read())

    
            #table_name = "scoreresults"
            #table_client = table_service_client.create_table(table_name=table_name)
    blob = BlobClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=vladimirstoragethesis;AccountKey=XdyCazpFWpyUs+iuKkS2yD4GZ+8GaAram/ltSwv2C8uG/hi7dvVKcFE9F3uGaqcbB7tAYWdUgIgY+AStxuPnQQ==;EndpointSuffix=core.windows.net", container_name="visualizationimages", blob_name=date+".visualized.png")
    with open(pathtosaveimage, "rb") as data:
        blob.upload_blob(data)

    destination = os.path.join('./archive', date+".visualized.png")
    os.replace(pathtosaveimage, destination)

    
    
 
    return HttpResponse(image_data, content_type="image/png")  


