import pandas
import numpy as np
import requests
import itertools
import json
import os
import argparse

parser = argparse.ArgumentParser(description="Przeliczanie cen biletów")
parser.add_argument('-f', action='store_true')

args = parser.parse_args()

distances = {}

if not os.path.isfile('distances.json') or args.f:
    print("No distances, loading...")
    cities = ['Warsaw', 'Berlin', 'Frankfurt', 'Katowice', 'Paris', 'London', 'Chicago', 'New York', 'Tokio', 'Rome']

    def getDistance(cityA, cityB):
        r = requests.get(f'https://www.dystans.org/route.json?stops={cityA}|{cityB}')
        result = r.json()
        return result['distance']

    for cityA, cityB in itertools.combinations(cities, 2):
        distance = getDistance(cityA, cityB)
        distances[f'{cityA} {cityB}'] = distance
        distances[f'{cityB} {cityA}'] = distance

    with open('distances.json', 'w') as f:
        json.dump(distances, f)
else:
    with open('distances.json', 'r') as f:
        distances = json.load(f)

print('distances loaded')
print(distances)


loty = pandas.read_csv("loty.csv")

price_per_km = 0.3
class_multiplier = [1, 1.2, 1.5]

for index, row in loty.iterrows():
    cityA = row['cityA']
    cityB = row['cityB']
    if cityA == cityB:
        loty = loty.drop(index=index)

distance_column = np.zeros(len(loty.index), dtype=np.int64)
price_column = np.zeros(len(loty.index), dtype=float)

for idx, (_, row) in enumerate(loty.iterrows()):
    cityA = row['cityA']
    cityB = row['cityB']
    class_num = row['class']
    distance = distances[f'{cityA} {cityB}']
    distance_column[idx] = distance
    price = float(round(distance * price_per_km * class_multiplier[class_num], 2))
    price_column[idx] = price

loty.insert(len(loty.columns), 'distance', distance_column)
loty.insert(len(loty.columns), 'price', price_column)
loty.to_csv('loty_przeliczone.csv', index=False)