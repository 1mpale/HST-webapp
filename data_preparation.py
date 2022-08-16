import numpy as np
import csv
from pathlib import Path
import re
import json

listOfNodeTypes = ["hidden","array","string","object","code","closure","regexp","number","native","synthetic","concatenated string","sliced string","symbol","bigint"]
headerList = ["type","name","id","self_size","edge_count","trace_node_id","detachedness"]

def data_preparation(filepath):
    mydir = Path(filepath)
    for file in mydir.glob('*.heapsnapshot'):
        with open (file) as filedeep:
            array = []
            count1 = 0 
            count2 = 0 
            for line in filedeep:
                ls = line.split(",")
                while('' in ls) :
                    ls.remove('')
                ls = [s.replace("\n", "") for s in ls]
                if not (re.search('[a-zA-Z]', line)):
                    if (len(ls))==7:
                        count1 = count1 + 1
                        array.append(ls)

            for x in array[1:count1]:
                
                for type in range (len(listOfNodeTypes)):
                    if x[0] == str(type):
                        x[0] = listOfNodeTypes[type]
            for i in range (1, count1):
                for j in range (1, len(array[i])):
                    if(len(array[i][j]) != 0):
                        newint = int(array[i][j])
                        array[i][j] = newint

            del array[0]
    

        finalarray = np.array(array,dtype=object,)
        print(finalarray)
    
        with open (f"{file.name}.csv", 'w', newline='') as file1:
            dw = csv.DictWriter(file1, delimiter=',', 
                            fieldnames=headerList)
            dw.writeheader()
            mywriter = csv.writer(file1, delimiter=',')
            mywriter.writerows(finalarray)

def read_json(file):
    try:
        print('Reading from input')
        with open(file, 'r') as f:
            return json.load(f)
    finally:
        print('Done reading')

config_dict = read_json("config.json")

path_to_prepare = config_dict["dir_for_data_peparation"]

data_preparation(path_to_prepare)