import collections
from glob import glob
try:
    from collections import abc
    collections.MutableMapping = abc.MutableMapping
except:
    pass

from pathlib import Path
import pandas as pd
from river import stream
import pickle
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import json
import os

def visualization(filepath, model):
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_zlabel("x_composite_3")
    scores_list = []
    mydir = Path(filepath)
    for file in  glob.glob('*.heapsnapshot.csv'):
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
            score = model.score_one(x)
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
        ax.scatter(X_reduce[:, 0], X_reduce[:, 1], zs=X_reduce[:, 2], s=4, lw=1, label="inliers",c="green")
        ax.scatter(X_reduce[outlier_index,0],X_reduce[outlier_index,1], X_reduce[outlier_index,2],
            lw=2, s=60, marker="x", c="red", label="outliers")
        plt.draw
        scores_list.clear() 

def read_json(file):
    try:
        print('Reading from input')
        with open(file, 'r') as f:
            return json.load(f)
    finally:
        print('Done reading')

config_dict = read_json("config.json")

path_to_visualize = config_dict["dir_for_visualization"]

path = os.getcwd()

HST_model_path = path + "/HST_full.sav"

HST_model = pickle.load(open(HST_model_path, 'rb'))

visualization(path_to_visualize, HST_model)