import csv
from geopy.distance import geodesic


# Funzione per il calcolo delle distanze in linea d'aria tra ordini e riders
def calcola_distanze(ordini, riders):
    distanze = {}
    for ordine in ordini:
        ristorante_latlon = (ordine['ristorante_lat'], ordine['ristorante_lon'])

        for rider in riders:
            rider_latlon = (rider['rider_lat'], rider['rider_lon'])
            # Calcola la distanza in linea d'aria (in km)
            distanza = geodesic(ristorante_latlon, rider_latlon).km
            distanze[(rider['rider_id'], ordine['ordine_id'])] = distanza

    return distanze


# Funzione per caricare dati su ordini e riders dai rispettivi file csv
def carica_dati(file_ordini, file_riders):
    ordini = []
    riders = []

    # Caricamento dei dati degli ordini
    with open(file_ordini, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ordini.append({
                'ordine_id': int(row['ordine_id']),
                'ristorante_lat': float(row['ristorante_lat']),
                'ristorante_lon': float(row['ristorante_lon']),
                'destinazione_lat': float(row['destinazione_lat']),
                'destinazione_lon': float(row['destinazione_lon']),
                'traffico': row['traffico'],
                'tempo_preparazione': int(row['tempo_preparazione'])
            })

    # Caricamento dei dati dei rider
    with open(file_riders, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            riders.append({
                'rider_id': int(row['rider_id']),
                'nome': row['nome'],
                'rider_lat': float(row['rider_lat']),
                'rider_lon': float(row['rider_lon']),
                'mezzo_trasporto': row['mezzo_trasporto']
            })

    return ordini, riders


# Funzione per le generazione dei fatti Prolog
def scrivi_dati_in_prolog(ordini, riders, distanze):
    with open("fatti.pl", "w") as f:
        f.write(":- dynamic rider_assigned/1.\n")
        f.write(":- discontiguous ordine/7.\n")
        f.write(":- discontiguous traffico/2.\n")

        # Scrivere ordini
        for ordine in ordini:
            f.write(
                f"ordine({ordine['ordine_id']}, {ordine['ristorante_lat']}, {ordine['ristorante_lon']}, {ordine['destinazione_lat']},{ordine['destinazione_lon']}, '{ordine['traffico']}', {ordine['tempo_preparazione']}).\n")

            # Scrivere traffico
            traffico = ordine['traffico'].lower()
            f.write(f"traffico({ordine['ordine_id']}, {traffico}).\n")

        # Scrivere rider
        for rider in riders:
            f.write(
                f"rider({rider['rider_id']}, '{rider['nome']}', {rider['rider_lat']}, {rider['rider_lon']}, '{rider['mezzo_trasporto']}').\n")

        # Scrivere distanze
        for distanza in distanze:
            rider_id, ordine_id = distanza
            f.write(f"distanza({rider_id}, {ordine_id}, {distanze[distanza]}).\n")


# Esegui il flusso di calcolo e passaggio a Prolog
def main():
    # Caricamento ordini e rider da file CSV
    ordini, riders = carica_dati('ordini.csv', 'riders.csv')

    # Calcolo distanze tra ordini e riders
    distanze = calcola_distanze(ordini, riders)

    # Scrittura dati in Prolog
    scrivi_dati_in_prolog(ordini, riders, distanze)

    print("Dati scritti in Prolog.\n\n")


if __name__ == "__main__":
    main()
