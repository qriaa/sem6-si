# Autor: Dr inż. Piotr Syga
# Źródło: https://syga.kft.pwr.edu.pl/courses/siiiw/dijkstra.py
import heapq
class Graph:
    def __init__(self, edges):
        self.edges = edges
        self.graph_dict = {}
        for start, end, weight in self.edges:
            if start in self.graph_dict:
                self.graph_dict[start].append((end, weight))
            else:
                self.graph_dict[start] = [(end, weight)]
            if end in self.graph_dict:
                self.graph_dict[end].append((start, weight))
            else:
                self.graph_dict[end] = [(start, weight)]

def dijkstra(graph_dict, start):
    distances = {node: float('inf') for node in graph_dict}
    distances[start] = 0
    pq = [(0, start)]
    prev_nodes = {node: None for node in graph_dict}
    while pq:
        curr_dist, curr_node = heapq.heappop(pq)
        # dijkstra curr_node == goal_node
        if curr_dist > distances[curr_node]:
            continue
        for neighbor, weight in graph_dict[curr_node]:
            new_dist = curr_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                prev_nodes[neighbor] = curr_node
                heapq.heappush(pq, (new_dist, neighbor))
    return distances, prev_nodes

def shortest_path(graph_dict, start, goal):
    distances, prev_nodes = dijkstra(graph_dict, start)
    path = []
    curr_node = goal
    while curr_node is not None:
        path.append(curr_node)
        curr_node = prev_nodes[curr_node]
    path.reverse()
    return distances[goal], path

def manhattan_dist(graph_dict, node, goal):
    distance, path = shortest_path(graph_dict, node, goal)
    return distance, path

edges = [
        ('A', 'B', 2), ('A', 'C', 4), ('B', 'D', 3), ('C', 'D', 1),
        ('C', 'E', 7), ('D', 'F', 5), ('E', 'F', 4), ('E', 'G', 2),
        ('F', 'H', 1), ('G', 'H', 2)
]
gg = Graph(edges)
distance, path = manhattan_dist(gg.graph_dict, 'A', 'H')
print("Shortest distance:", distance)
print("Shortest path:", path) 