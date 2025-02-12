import osmnx as ox
import json
from geopy.distance import geodesic
import networkx as nx

# Funzione per calcolare la distanza tra due punti usando geodesic
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

# Funzione per ottenere il nodo più vicino alle coordinate passate in input nel grafo
def get_closest_node(lat, lon, graph):
    lat = float(lat)
    lon = float(lon)
    # Trova il nodo più vicino nel grafo a partire dalle coordinate
    closest_node = ox.distance.nearest_nodes(graph, lon, lat)
    return closest_node

# Funzione per trovare il miglior percorso tra due nodi utilizzando A*
def find_best_path(bari_graph, source, target):
    return nx.astar_path(bari_graph, source, target, weight='length')

# Funzione per calcolare la distanza totale di un percorso
def calculate_path_distance(bari_graph, path):
    return sum(bari_graph[x][y][0]['length'] for x, y in zip(path[:-1], path[1:]))

# Scarica la mappa di Bari con le strade percorribili da auto, moto e biciclette
place_name = "Bari, Italy"
graph = ox.graph_from_place(place_name, network_type='drive')

# Gli archi vengono etichettati con la distanza dei nodi che collegano
for u, v, data in graph.edges(data=True):
    u_lat, u_lon = graph.nodes[u]['y'], graph.nodes[u]['x']
    v_lat, v_lon = graph.nodes[v]['y'], graph.nodes[v]['x']
    distance = calculate_distance(u_lat, u_lon, v_lat, v_lon)
    data['length'] = distance

# Etichetta ogni nodo con le sue coordinate geografiche
for node, data in graph.nodes(data=True):
    data['coordinates'] = (data['y'], data['x'])  # Aggiungi coordinate lat/lon al nodo

# Carica il file JSON con gli ordini
with open('assigned_riders.json', 'r') as f:
    orders = json.load(f)

# Processa gli ordini
for order in orders:
    rider_start_lat = order["RiderLat"]
    rider_start_lon = order["RiderLon"]
    restaurant_lat = order["RistoranteLat"]
    restaurant_lon = order["RistoranteLon"]
    destination_lat = order["DestinazioneLat"]
    destination_lon = order["DestinazioneLon"]

    # Trova il nodo più vicino a ciascuna posizione usando le coordinate
    rider_node = get_closest_node(rider_start_lat, rider_start_lon, graph)
    restaurant_node = get_closest_node(restaurant_lat, restaurant_lon, graph)
    destination_node = get_closest_node(destination_lat, destination_lon, graph)

    # Trova il percorso migliore da A (rider) a B (ristorante), poi da B a C (destinazione)
    path_ab = find_best_path(graph, rider_node, restaurant_node)
    path_bc = find_best_path(graph, restaurant_node, destination_node)
    complete_path = path_ab + path_bc[1:]

    # Calcola le distanze dei percorsi
    distance_ab = calculate_path_distance(graph, path_ab)
    distance_bc = calculate_path_distance(graph, path_bc)
    total_distance = distance_ab + distance_bc

    # Stampa i risultati
    print(f"Order ID: {order['OrderID']}")
    print(f"Path from Rider to Restaurant ({distance_ab:.2f} km): {path_ab}")
    print(f"Path from Restaurant to Destination ({distance_bc:.2f} km): {path_bc}")
    print(f"Total Distance: {total_distance:.2f} km")
