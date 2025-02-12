% Se il traffico è alto, il mezzo migliore è la bici
meglio_mezzo(OrdineID, bici) :-
    traffico(OrdineID, alto).

% Se il traffico è basso, il mezzo migliore è auto
meglio_mezzo(OrdineID, auto) :-
    traffico(OrdineID, basso).

% Se il traffico è medio, il mezzo migliore è moto
meglio_mezzo(OrdineID, moto) :-
    traffico(OrdineID, medio).

% Se la destinazione è lontana, meglio usare moto o auto
meglio_mezzo_per_destinazione_lontana(OrdineID, auto) :-
    destinazione(OrdineID, Destinazione),
    distanza(Destinazione, Lontananza),
    Lontananza > 3.  % Soglia arbitraria di 7 km per definire una destinazione lontana

meglio_mezzo_per_destinazione_lontana(OrdineID, moto) :-
    destinazione(OrdineID, Destinazione),
    distanza(Destinazione, Lontananza),
    Lontananza > 2.  % Soglia arbitraria di 5 km

% Se la destinazione è vicina, meglio usare la bici
meglio_mezzo_per_destinazione_vicina(OrdineID, bici) :-
    destinazione(OrdineID, Destinazione),
    distanza(Destinazione, Lontananza),
    Lontananza =< 2.  % Soglia arbitraria di 3 km per definire una destinazione vicina

% Un rider è valido per un ordine solo se ha il mezzo considerato migliore
rider_valido(IDRider, IDOrdine) :-
    rider(IDRider, _, _, _, Mezzo),
    meglio_mezzo(IDOrdine, Mezzo).

miglior_rider(IDOrdine, IDRider) :-
    findall(Distanza-IdRider,
        (distanza(IdRider, IDOrdine, Distanza),
         rider_valido(IdRider, IDOrdine),
         \+ rider_assigned(IdRider)),
        ListaDistanze),
    ListaDistanze \= [],
    sort(1, @=<, ListaDistanze, [_-MigliorRider | _]),
    IDRider = MigliorRider.

% Se nessun rider ha il mezzo giusto, scegli il più vicino
miglior_rider(IDOrdine, IDRider) :-
    findall(Distanza-IdRider,
        (distanza(IdRider, IDOrdine, Distanza),
         \+ rider_assigned(IdRider)),
        ListaDistanze),
    ListaDistanze \= [],
    sort(1, @=<, ListaDistanze, [_-MigliorRider | _]),
    IDRider = MigliorRider.

% Assegna un ordine al rider migliore disponibile
assegna_ordine(IDOrdine, IDRider) :-
    miglior_rider(IDOrdine, IDRider),
    assertz(rider_assigned(IDRider)).  % Segna il rider come assegnato
