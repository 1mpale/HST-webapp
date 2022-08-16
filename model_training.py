import collections
try:
    from collections import abc
    collections.MutableMapping = abc.MutableMapping
except:
    pass

from pathlib import Path
from river import anomaly
from river import compose
from river import preprocessing
import numbers
from river import stream
import os
import pickle
import json
import os

def build_model(n_tress=25, height=10, window_size=250):
    features_pipeline = compose.TransformerUnion(
        compose.Select('type'),
        compose.Select('name'),
        compose.Select('id'),
        compose.Select('self_size'),
        compose.Select('edge_count'),
        compose.Select('trace_node_id'),
        compose.Select('detachedness'),
    )
    categorical_features = compose.Pipeline(
        compose.SelectType(str),
        preprocessing.OneHotEncoder()
    )
    numerical_features = compose.Pipeline(
        compose.SelectType(numbers.Number),
        preprocessing.MinMaxScaler()
    )
    model = compose.Pipeline(features_pipeline,
                numerical_features + categorical_features,
                anomaly.HalfSpaceTrees(n_trees=n_tress, height=height, window_size=window_size))
    return model

def train_model_callback(filepath, model):
    mydir = Path(filepath)
    for file in mydir.glob('*.heapsnapshot.csv'):
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
            model = model.learn_one(x=x)
    return model

def read_json(file):
    try:
        print('Reading from input')
        with open(file, 'r') as f:
            return json.load(f)
    finally:
        print('Done reading')

config_dict = read_json("config.json")

path_to_train = config_dict["dir_for_training"]

path = os.getcwd()

HST_model_path = path + "/HST_full.sav"

HST_model = pickle.load(open(HST_model_path, 'rb'))

HST_updated = train_model_callback(path_to_train, HST_model)

def save_model(saveas, trained_model):
    pickle.dump(trained_model, open(saveas, 'wb'))

save_model('HST_latest.sav', HST_updated)



