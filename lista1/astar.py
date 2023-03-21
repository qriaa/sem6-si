# Autor: Dr inż. Piotr Syga
# Źródło: https://syga.kft.pwr.edu.pl/courses/siiiw/astar.py
import heapq
import math

def astar(start, goal, neighbors_fn, heuristic_fn):
    front = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while front:
        _, current = heapq.heappop(front)
        
        if current == goal:
            break
        
        for neighbor in neighbors_fn(current):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic_fn(goal, neighbor)
                heapq.heappush(front, (priority, neighbor))
                came_from[neighbor] = current
    
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    
    return path, cost_so_far[goal]


def manhattan_distance(a, b):
    return sum([abs(x-y) for x,y in zip(a,b)])

def euclidean_distance(a, b):
   return math.sqrt(sum([(x - y) ** 2 for x, y in zip(a, b)]))

def towncenter_distance(a, b):
    return euclidean_distance(a, (0, 0, 0, 0, 0, 0, 0))+euclidean_distance((0, 0, 0, 0, 0, 0, 0), b)

def unidimensional_distance(a,b):
    return max([abs(x-y) for x,y in zip(a,b)])

def cosine_distance(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x ** 2 for x in a))
    magnitude_b = math.sqrt(sum(x ** 2 for x in b))
    return 1 - (dot_product / (magnitude_a * magnitude_b))

def chebyshev_distance(a, b):
    return max(abs(x - y) for x, y in zip(a, b))

if __name__ == '__main__':
   
    graph = {
    (0, 0, 0, 0, 0, 0, 0): [(1, 1, 1, 1, 1, 1, 1), (1, 2, 3, 4, 5, 6, 7), (4, 5, 6, 7, 8, 9, 10),(5, 6, 7, 8, 6, 5, 1)],
    (1, 2, 3, 4, 5, 6, 7): [(2, 3, 4, 5, 6, 7, 8), (1, 1, 1, 1, 1, 1, 1), (5, 2, 1, 4, 1, 3, 1)],
    (2, 3, 4, 5, 6, 7, 8): [(3, 4, 5, 6, 7, 8, 9), (2, 4, 2, 1, 4, 1, 8), (1, 2, 3, 4, 5, 6, 7),(5, 6, 7, 8, 6, 5, 1),(6, 6, 10, 2, 2, 5, 10), (9, 3, 2, 7, 0, 0, 1), (9, 9, 2, 0, 2, 1, 9)],
    (3, 4, 5, 6, 7, 8, 9): [(4, 5, 6, 7, 8, 9, 10)],
    (4, 5, 6, 7, 8, 9, 10): [],
    (1, 1, 1, 1, 1, 1, 1): [(2, 2, 2, 2, 2, 2, 2), (5, 2, 1, 4, 1, 3, 1), (6, 6, 10, 2, 2, 5, 10), (10, 10, 10, 10, 10, 10, 10)],
    (2, 2, 2, 2, 2, 2, 2): [],
    (5, 2, 1, 4, 1, 3, 1): [(2, 2, 2, 2, 2, 2, 2), (2, 0, 2, 0, 2, 0, 2), (2, 4, 2, 1, 4, 1, 8), (3, 4, 5, 6, 7, 8, 9), (9, 9, 2, 0, 2, 1, 9)],
    (2, 0, 2, 0, 2, 0, 2): [],
    (2, 2, 2, 2, 2, 2, 2): [(2, 3, 4, 5, 6, 7, 8), (2, 2, 2, 2, 2, 2, 2), (4, 5, 6, 7, 8, 9, 10), (5, 6, 7, 8, 6, 5, 1), (10, 10, 10, 10, 10, 10, 10)],
    (3, 3, 2, 0, 1, 0, 1): [(1, 2, 3, 4, 5, 6, 7), (2, 2, 2, 2, 2, 2, 2), (2, 3, 4, 5, 6, 7, 8), (5, 2, 1, 4, 1, 3, 1), (2, 0, 2, 0, 2, 0, 2), (6, 6, 10, 2, 2, 5, 10), (2, 2, 2, 2, 2, 2, 2)],
    (5, 6, 7, 8, 6, 5, 1): [(2, 0, 2, 0, 2, 0, 2), (3, 4, 5, 6, 7, 8, 9)],
    (6, 6, 10, 2, 2, 5, 10): [(2, 0, 2, 0, 2, 0, 2), (1, 1, 1, 1, 1, 1, 1)],
    (2, 4, 2, 1, 4, 1, 8): [(1, 2, 3, 4, 5, 6, 7), (5, 2, 1, 4, 1, 3, 1), (2, 0, 2, 0, 2, 0, 2)],
    (9, 3, 2, 7, 0, 0, 1): [(5, 2, 1, 4, 1, 3, 1), (10, 10, 10, 10, 10, 10, 10)],
    (9, 9, 2, 0, 2, 1, 9): [(2, 0, 2, 0, 2, 0, 2), (10, 10, 10, 10, 10, 10, 10)], 
    (10, 10, 10, 10, 10, 10, 10): [(2, 0, 2, 0, 2, 0, 2), (3, 4, 5, 6, 7, 8, 9)]
}
    
    start = (1, 2, 3, 4, 5, 6, 7)
    goal = (10, 10, 10, 10, 10, 10, 10)
    
    path, cost = astar(start, goal, lambda node: graph[node], lambda a, b: manhattan_distance(a, b))
    print(f"Path using Manhattan distance heuristic: {path}")
    print(f"Cost using Manhattan distance heuristic: {cost}")

    path, cost = astar(start, goal, lambda node: graph[node], lambda a, b: euclidean_distance(a, b))
    print(f"Path using Euclid's distance heuristic: {path}")
    print(f"Cost using Euclid's distance heuristic: {cost}")

    path, cost = astar(start, goal, lambda node: graph[node], lambda a, b: towncenter_distance(a, b))
    print(f"Path using Towncenter distance heuristic: {path}")
    print(f"Cost using Towncenter distance heuristic: {cost}")

    path, cost = astar(start, goal, lambda node: graph[node], lambda a, b: unidimensional_distance(a, b))
    print(f"Path using unidimensional distance heuristic: {path}")
    print(f"Cost using unidimensional distance heuristic: {cost}")

    path, cost = astar(start, goal, lambda node: graph[node], lambda a, b: cosine_distance(a, b))
    print(f"Path using cosine distance heuristic: {path}")
    print(f"Cost using cosine distance heuristic: {cost}")    

    path, cost = astar(start, goal, lambda node: graph[node], lambda a, b: chebyshev_distance(a, b))
    print(f"Path using Chebyshev distance heuristic: {path}")
    print(f"Cost using Chebyshev distance heuristic: {cost}")    