# Autor: Dr inż. Piotr Syga
# Źródło: https://syga.kft.pwr.edu.pl/courses/siiiw/TSTSP.py
import random
import math


n_cities = 100
n_dimensions = 7
max_iterations = math.ceil(1.1*(n_cities**2))
turns_improved = 0
improve_thresh=2*math.floor(math.sqrt(max_iterations))
tabu_list = []
tabu_tenure = n_cities



def distance(city1, city2):
    return math.sqrt(sum([(city1[i]-city2[i])**2 for i in range(n_dimensions)]))

cities = [[random.randint(0, 100) for j in range(n_dimensions)] for i in range(n_cities)]
distances = [[distance(cities[i], cities[j]) for j in range(n_cities)] for i in range(n_cities)]

total=0
for i in range(n_cities):
        for j in range(n_cities):
            total += distances[i][j]

aspiration_criteria = (total/(n_cities**2))*2.2

current_solution = list(range(n_cities))
random.shuffle(current_solution)
best_solution = current_solution[:]
best_solution_cost = sum([distances[current_solution[i]][current_solution[(i+1)%n_cities]] for i in range(n_cities)])

for iteration in range(max_iterations):
    if turns_improved>improve_thresh:
        break
    best_neighbor = None
    best_neighbor_cost = float('inf')
    coordA, coordB = 0, 0
    for i in range(n_cities):
        for j in range(i+1, n_cities):
            neighbor = current_solution[:]
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
            neighbor_cost = sum([distances[neighbor[i]][neighbor[(i+1)%n_cities]] for i in range(n_cities)])
            if (i,j) not in tabu_list or neighbor_cost < aspiration_criteria:
                if neighbor_cost < best_neighbor_cost:
                    best_neighbor = neighbor[:]
                    best_neighbor_cost = neighbor_cost
                    coordA, coordB = i,j
        tabu_list.append((coordA, coordB))    
    if best_neighbor is not None:
        current_solution = best_neighbor[:]
        tabu_list.append((coordA, coordB))

        if len(tabu_list) > tabu_tenure:
            tabu_list.pop(0)
        if best_neighbor_cost < best_solution_cost:
            best_solution = best_neighbor[:]
            best_solution_cost = best_neighbor_cost
            turns_improved=0
        else:
            turns_improved=turns_improved+1 

    print("Iteration {}: Best solution cost = {}".format(iteration, best_solution_cost))

print("Best solution: {}".format(best_solution))
print("Best solution cost: {}".format(best_solution_cost))