# Autor algorytmu Dijkstry oraz A* przed modyfikacją:
#   Dr inż. Piotr Syga
# Źródła:
#   https://syga.kft.pwr.edu.pl/courses/siiiw/dijkstra.py
#   https://syga.kft.pwr.edu.pl/courses/siiiw/astar.py

import pathlib
import csv
import math
import sys
from datetime import *
from timeit import default_timer as timer

parentDirPath = pathlib.Path(__file__).parent.resolve()

csvPath = parentDirPath / "connection_graph.csv"
data = list()

# ,Unnamed: 0,company,line,departure_time,arrival_time,start_stop,end_stop,start_stop_lat,start_stop_lon,end_stop_lat,end_stop_lon
# Load data into list of lists
print('Converting data into initial list...')
with open(csvPath) as file:
    reader = csv.reader(file, delimiter=',')
    next(reader)
    for row in reader:
        row[4] = datetime.strptime(row[4], '%H:%M:%S').time()
        row[5] = datetime.strptime(row[5], '%H:%M:%S').time()
        row[8] = float(row[8]) 
        row[9] = float(row[9])
        row[10] = float(row[10])
        row[11] = float(row[11])
        data.append(row[2::])
# company, line, departure_time, arrival_time, start_stop, end_stop, start_stop_lat, start_stop_lon, end_stop_lat, end_stop_lon

# Convert data to dictionary
print('Converting initial parse into graph dictionary (might take a bit)...')
stops = set()
for row in data:
    stops.add(row[4])

mainGraph = dict()
for key in stops:
    value = list()
    filteredForKey = filter(lambda dataRow: dataRow[4] == key , data)
    for row in filteredForKey:
        row = row.copy()
        row.pop(4)
        value.append(row)
    mainGraph[key] = value

# mainGraph:
#   Key: start_stop;
#   Value: list of: company, line, departure_time, arrival_time, end_stop, start_stop_lat, start_stop_lon, end_stop_lat, end_stop_lon

def getTimeSeconds(time):
    return timedelta(hours=time.hour, minutes=time.minute, seconds=time.second).total_seconds()

def addSecondsToTime(time, seconds):
    temp_date = datetime(1,1,1, time.hour, time.minute, time.second)
    temp_date += timedelta(seconds=seconds)
    return temp_date.time()


# Zad. 1

# Dijkstra, A*
# Autor: Dr inż. Piotr Syga
# Źródło: https://syga.kft.pwr.edu.pl/courses/siiiw/dijkstra.py
# Kod został zmodyfikowany w celu dopasowania danych oraz wycinka rzeczywistości do algorytmu
# np. nie można wsiąść do tramwaju przed tym jak przyjedzie na przystanek
# oraz nie można cofać się w czasie.
# Oprócz tego został dodany warunek, który kończy algorytm Dijkstry po znalezieniu celu.
import heapq

def dijkstra(graph_dict, start, goal, current_time):
    distances = {}
    prev_nodes = {}
    arrival_times = {}
    mainGraphEntries = {}
    for node in graph_dict.keys():
        distances[node] = float('inf')
        prev_nodes[node] = None
        arrival_times[node] = None
        mainGraphEntries[node] = None
    distances[start] = 0
    arrival_times[start] = current_time

    pq = [(0, start)]

    while pq:
        curr_dist, curr_node = heapq.heappop(pq)
        if curr_node == goal:
            break

        if curr_dist > distances[curr_node]:
            continue
        for row in graph_dict[curr_node]:
            neighbor = row[4]
            weight = getTimeSeconds(row[3]) - getTimeSeconds(arrival_times[curr_node])
            if weight < 0 or getTimeSeconds(arrival_times[curr_node]) > getTimeSeconds(row[2]):
                continue
            
            new_dist = curr_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                prev_nodes[neighbor] = curr_node
                arrival_times[neighbor] = addSecondsToTime(arrival_times[curr_node], weight)
                mainGraphEntries[neighbor] = row
                heapq.heappush(pq, (new_dist, neighbor))

    path = []
    resultEntries = []
    curr_node = goal
    while curr_node is not None:
            path.append(curr_node)
            resultEntries.append(mainGraphEntries[curr_node])
            curr_node = prev_nodes[curr_node]
    path.reverse()
    resultEntries.reverse()

    return distances[goal], path, resultEntries

def manhattan_distance(a, b):
    return sum([abs(x-y) for x,y in zip(a,b)])

def euclidean_distance(a, b):
   return math.sqrt(sum([(x - y) ** 2 for x, y in zip(a, b)]))

def astarTime(graph_dict, start, goal, current_time, heuristic_fn):
    distances = {}
    prev_nodes = {}
    arrival_times = {}
    mainGraphEntries = {}
    for node in graph_dict.keys():
        distances[node] = float('inf')
        prev_nodes[node] = None
        arrival_times[node] = None
        mainGraphEntries[node] = None
    distances[start] = 0
    arrival_times[start] = current_time

    pq = [(0, start)]

    while pq:
        curr_dist, curr_node = heapq.heappop(pq)
        if curr_node == goal:
            break

        if curr_dist > distances[curr_node]:
            continue
        for row in graph_dict[curr_node]:
            neighbor = row[4]
            # Verify whether going back in time or entering a line before it arrives
            secondsOfTravel = getTimeSeconds(row[3]) - getTimeSeconds(arrival_times[curr_node])
            if secondsOfTravel < 0 or getTimeSeconds(arrival_times[curr_node]) > getTimeSeconds(row[2]):
                continue
            
            weight = secondsOfTravel

            weight += heuristic_fn((row[5], row[6]),(row[7], row[8]))*25000 #!!!!

            new_dist = curr_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                prev_nodes[neighbor] = curr_node
                arrival_times[neighbor] = row[3]
                mainGraphEntries[neighbor] = row
                heapq.heappush(pq, (new_dist, neighbor))

    path = []
    resultEntries = []
    curr_node = goal
    while curr_node is not None:
            path.append(curr_node)
            resultEntries.append(mainGraphEntries[curr_node])
            curr_node = prev_nodes[curr_node]
    path.reverse()
    resultEntries.reverse()

    return distances[goal], path, resultEntries

def astarTransfer(graph_dict, start, goal, current_time, heuristic_fn):
    distances = {}
    prev_nodes = {}
    prev_lines = {}
    arrival_times = {}
    mainGraphEntries = {}
    for node in graph_dict.keys():
        distances[node] = float('inf')
        prev_nodes[node] = None
        arrival_times[node] = None
        mainGraphEntries[node] = None
        prev_lines[node] = None
    distances[start] = 0
    arrival_times[start] = current_time

    pq = [(0, start)]

    while pq:
        curr_dist, curr_node = heapq.heappop(pq)
        if curr_node == goal:
            break

        if curr_dist > distances[curr_node]:
            continue
        for row in graph_dict[curr_node]:
            neighbor = row[4]
            # Verify whether going back in time or entering a line before it arrives
            secondsOfTravel = getTimeSeconds(row[3]) - getTimeSeconds(arrival_times[curr_node])
            if secondsOfTravel < 0 or getTimeSeconds(arrival_times[curr_node]) > getTimeSeconds(row[2]):
                continue

            if prev_lines[curr_node] == None:
                weight = 100
            elif prev_lines[curr_node] != row[1]:
                weight = 100
            else:
                weight = 0

            weight += heuristic_fn((row[5], row[6]),(row[7], row[8]))*1500 #!!!!

            new_dist = curr_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                prev_nodes[neighbor] = curr_node
                prev_lines[neighbor] = row[1]
                arrival_times[neighbor] = row[3]
                mainGraphEntries[neighbor] = row
                heapq.heappush(pq, (new_dist, neighbor))

    path = []
    resultEntries = []
    curr_node = goal
    while curr_node is not None:
            path.append(curr_node)
            resultEntries.append(mainGraphEntries[curr_node])
            curr_node = prev_nodes[curr_node]
    path.reverse()
    resultEntries.reverse()

    return distances[goal], path, resultEntries


def presentResult(result, startTimeArg, executionTime):
    weightTraveled = result[0]
    path = result[1]
    graphEntries = result[2]
    graphEntries.pop(0)
    print(f"Time of arrival at {path[0]} stop: {startTimeArg}")
    prevLine = None
    firstStop = True
    for i in range(0, len(path)-1):
        if prevLine != graphEntries[i][1]:
            if not firstStop:
                print(f"Left line {prevLine} on {path[i]} stop at time {graphEntries[i-1][3]}")
            prevLine = graphEntries[i][1]
            print(f"Entered line {graphEntries[i][1]} on {path[i]} stop at time: {graphEntries[i][2]}")
        firstStop = False
    print(f"Last stop - {path[len(path)-1]} leaving line {graphEntries[len(graphEntries)-1][1]} at time {graphEntries[len(graphEntries)-1][3]}")
    sys.stderr.write(f"Total commute weight: {weightTraveled}\n")
    sys.stderr.write(f"Code execution time: {executionTime}\n")


while True:
    startArg = input("Input start stop: ")
    endArg = input("Input end stop: ")
    optModeArg = input("Input A* mode of operation ('t' - optimize time, 'p' - optimize transfers): ")
    hr = int(input("Input hour of arrival at start stop: "))
    min = int(input("Input minute of arrival at start stop: "))
    startTimeArg = time(hour=hr, minute=min)



    print()
    print("Calculating Dijkstra - time...")
    start = timer()
    result = dijkstra(mainGraph, startArg, endArg, startTimeArg)
    end = timer()

    presentResult(result, startTimeArg, end - start)
    print()


    print(f"Calculating A* - {'time' if optModeArg == 't' else 'transfers'} with euclidean heuristic...")
    
    if optModeArg == 't':
        start = timer()
        result = astarTime(mainGraph, startArg, endArg, startTimeArg, euclidean_distance)
        end = timer()
    else:
        start = timer()
        result = astarTransfer(mainGraph, startArg, endArg, startTimeArg, euclidean_distance)
        end = timer()

    presentResult(result, startTimeArg, end - start)
    print()