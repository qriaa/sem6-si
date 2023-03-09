import pandas as pd
import numpy as np
import pathlib

csvPath =  pathlib.Path(__file__).parent.resolve()

data = pd.read_csv(csvPath / "connection_graph.csv")

print(data.columns)
print(data.get("start_stop"))

def getStopLines(stop):
    data.loc[data['start_stop'] == stop]
    #data.where(data.get)
    ...

def getLineGraph(number):
    ...

def checkConnected(start, end):
    ...