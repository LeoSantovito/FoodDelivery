from pyswip import Prolog
import json

prolog = Prolog()

# Caricamento della knowledge base da Prolog
prolog.consult("fatti.pl")
prolog.consult("regole.pl")


# Funzione per ottenere tutti gli ordini dal file Prolog
def get_orders():
    orders = []
    for solution in prolog.query("ordine(OrderID, RistoranteLat, RistoranteLon, DestinazioneLat, DestinazioneLon, _, _)"):
        orders.append({
            "OrderID": solution["OrderID"],
            "RistoranteLat": solution["RistoranteLat"],
            "RistoranteLon": solution["RistoranteLon"],
            "DestinazioneLat": solution["DestinazioneLat"],
            "DestinazioneLon": solution["DestinazioneLon"]
        })
    return orders


# Funzione per ottenere tutte le informazioni sui rider
def get_riders():
    riders = []
    for solution in prolog.query("rider(RiderID, RiderName, Lat, Lon, Mezzo)"):
        riders.append({
            "RiderID": solution["RiderID"],
            "RiderName": solution["RiderName"],
            "Lat": solution["Lat"],
            "Lon": solution["Lon"],
            "Mezzo": solution["Mezzo"],
        })
    return riders


# Funzione per ottenere la distanza tra un rider e un ordine
def get_distance_from_rider_to_order(rider_id, order_id):
    for solution in prolog.query(f"distanza({rider_id}, {order_id}, Distanza)"):
        return solution["Distanza"]
    return None


# Funzione per ottenere il mezzo migliore per un ordine
def get_best_transport_mode(order_id):
    for solution in prolog.query(f"meglio_mezzo({order_id}, Mezzo)"):

        return solution["Mezzo"]
    return "non specificato"


# Funzione per ottenere il traffico per un ordine
def get_traffic_info(order_id):
    for solution in prolog.query(f"traffico({order_id}, Traffico)"):

        return solution["Traffico"]
    return "non specificato"


# Funzione per ottenere il miglior rider per un ordine
def get_best_rider_for_order(order_id):
    for solution in prolog.query(f"miglior_rider({order_id}, RiderID)"):

        return solution["RiderID"]
    return None  # Nessun rider disponibile

# Funzione principale per assegnare i rider agli ordini
def assign_riders():
    orders = get_orders()
    riders = get_riders()

    assigned_riders = []

    # Assegna il miglior rider per ogni ordine
    for order in orders:
        order_id = order["OrderID"]
        best_rider = get_best_rider_for_order(order_id)

        if best_rider:
            # Ottieni informazioni aggiuntive sul rider
            rider_info = next((rider for rider in riders if rider["RiderID"] == best_rider), None)
            if rider_info:
                rider_name = rider_info["RiderName"]
                rider_mezzo = rider_info["Mezzo"]
                rider_lat = rider_info["Lat"]
                rider_lon = rider_info["Lon"]

                # Ottieni il mezzo migliore per l'ordine
                best_mezzo = get_best_transport_mode(order_id)
                traffico = get_traffic_info(order_id)

                # Ottieni la distanza tra il rider e l'ordine
                distance = get_distance_from_rider_to_order(best_rider, order_id)

                # Aggiungi il rider all'elenco degli assegnati con tutte le informazioni richieste
                assigned_riders.append({
                    "OrderID": order_id,
                    "RiderID": best_rider,
                    "RiderName": rider_name,
                    "Mezzo": rider_mezzo,
                    "BestTransportMode": best_mezzo,
                    "Traffic": traffico,
                    "Distance": distance,
                    "RiderLat": rider_lat,
                    "RiderLon": rider_lon,
                    "RistoranteLat": order["RistoranteLat"],
                    "RistoranteLon": order["RistoranteLon"],
                    "DestinazioneLat": order["DestinazioneLat"],
                    "DestinazioneLon": order["DestinazioneLon"]
                })

                # Marca il rider come assegnato
                mark_rider_assigned(best_rider)
                print(f"Ordine {order_id} -> Rider {best_rider} ({rider_name}) assegnato con mezzo {rider_mezzo}")
        else:
            print(f"Nessun rider disponibile per l'ordine {order_id}")

    # Scrive i rider assegnati e le consegne programmate in un file JSON
    write_assigned_riders_to_json(assigned_riders)

# Funzione per segnare un rider come assegnato
def mark_rider_assigned(rider_id):
    prolog.assertz(f"rider_assigned({rider_id})")

# Funzione per scrivere i rider assegnati con i rispettivi ordini su un file JSON
def write_assigned_riders_to_json(assigned_riders):
    with open("assigned_riders.json", "w") as f:
        json.dump(assigned_riders, f, indent=4)
    print("\nConsegne da effettuare salvate nel file 'assigned_riders.json'.")

# Esegui il programma
if __name__ == "__main__":
    assign_riders()
