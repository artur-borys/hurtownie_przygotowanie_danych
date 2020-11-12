import pandas
import numpy as np
import requests
import itertools
import json
import os
import argparse
import random
import datetime
import shutil

parser = argparse.ArgumentParser(description="Przeliczanie cen biletów")
parser.add_argument('-f', action='store_true')

args = parser.parse_args()

distances = {}
cities = ['Warsaw', 'Berlin', 'Frankfurt', 'Katowice', 'Paris', 'London', 'Chicago', 'New York', 'Tokio', 'Rome']

if not os.path.isfile('distances.json') or args.f:
    print("No distances, loading...")

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

os.makedirs('prepared', exist_ok=True)

flights_data = []

def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)

d1 = datetime.datetime.strptime('2018-01-01', '%Y-%m-%d')
d2 = datetime.datetime.strptime('2019-12-31', '%Y-%m-%d')

for i in range(2000):
    cityA = random.choice(cities)
    cityB = random.choice(cities)
    airplane_id = random.randint(1, 10)
    while cityA == cityB:
        cityB = random.choice(cities)
    distance = distances[f'{cityA} {cityB}']
    dt = random_date(d1, d2)
    date_str = dt.strftime('%Y-%m-%d')
    flights_data.append([airplane_id, cityA, cityB, date_str, distance])

flights = pandas.DataFrame(flights_data, columns=['airplane_id', 'cityA', 'cityB', 'flight_dt', 'distance'])
print("Unikalnych dat: ", flights.flight_dt.nunique())

price_per_km = 0.3
class_multiplier = [1, 1.2, 1.5]

flights.insert(0, 'flight_id', np.arange(1, len(flights) + 1))
flights.to_csv('prepared/flights.csv', index=False)

tickets_data = []

clients = pandas.read_csv('clients.csv')

clients.insert(0, 'client_id', np.arange(1, len(clients) + 1))
clients.to_csv('prepared/clients.csv', index=False)

for i in range(100000):
    client_id = random.randint(1, len(clients))
    flight_id = random.randint(1, len(flights) - 1)
    
    class_number = random.randint(0, 2)
    luggage_weight = round(random.uniform(0, 40), 2)
    distance = flights.iloc[int(flight_id) - 1, len(flights.columns) - 1]
    price = float(round(price_per_km * distance * class_multiplier[class_number], 2))
    tickets_data.append([client_id, flight_id, class_number, luggage_weight, price])


tickets = pandas.DataFrame(tickets_data, columns=['client_id', 'flight_id', 'class', 'luggage_weight', 'price'])

tickets = tickets.drop_duplicates(['client_id', 'flight_id'])
tickets.insert(0, 'ticket_id', np.arange(1, len(tickets) + 1))
tickets.to_csv('prepared/tickets.csv', index=False)
print('Częstość lotu w biletach\n')
print(tickets['flight_id'].value_counts())
print('Częstość klientów')
print(tickets['client_id'].value_counts())

shutil.copyfile('airplanes.csv', 'prepared/airplanes.csv')