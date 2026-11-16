from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        # TODO
        # lista vuota per il risultato (da passare alla UI)
        risultato = []
        # scorro ogni distributore (A e B)
        for d in self._distributori:
            # lista vuota per raccogliere i prezzi del mese scelto
            prezzi_mese = []
            # per ogni prezzo associato ad un distributore + chiamata d_get prezzi per caricare i prezzi
            for prezzo in d.get_prezzi():
                # filtro: se il mese della data del prezzo coincide con quello scelto dall'utente
                if prezzo.data.month == mese:
                    # lo aggiungo alla lista intermedia per raccogliere i prezzi al litro del mese scelto
                    prezzi_mese.append(prezzo.prezzo_litro)
            # ci calcolo la media fuori dal ciclo (da fare alla fine dell'append), no medie parziali
            media = sum(prezzi_mese)/len(prezzi_mese)
            # aggiungo alla lista risultato la tupla col nome del distributore e la media relativa
            risultato.append((d.nome,media))
        return risultato



    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        # TODO
        # condizione di terminazione: se siamo arrivati al gg 8
        if giorno==8:
            # verifica se il costo attuale è migliore di quello ottimo o se siamo all'inizio (costo_ottimo=-1 valore di default)
            if costo_corrente<self.__costo_ottimo or self.__costo_ottimo == -1:
                self.__costo_ottimo = costo_corrente
                # salvo una copia indipendente della sequenza 'vincente'
                self.__sequenza_ottima = list(sequenza_parziale)
            # interrompo ramo ricorsione e torno indietro
            return
        # passo ricorsivo
        else:
            # per ogni scelta possibile (id_distributore) nella giornata odierna
            for id_distributore in prezzi_settimana:
                # costo benzina attuale (100 litri per il prezzo del giorno)
                costo_carb = prezzi_settimana[id_distributore][giorno-1]*100
                # se non siamo al primo giorno e abbiamo cambiato distributore rispetto a ieri
                if ultimo_distributore is not None and ultimo_distributore!=id_distributore:
                    # aggiungiamo 5 euro per lo spostamento
                    costo_carb+=5
                # aggiungiamo temporaneamente la scelta di oggi alla sequenza parziale
                sequenza_parziale.append(id_distributore)
                # chiamata ricorsiva
                self.__ricorsione(sequenza_parziale,giorno+1,id_distributore,costo_corrente+costo_carb,prezzi_settimana)
                # backtracking: per rimuovere l'ultima scelta fatta e permettere al ciclo di testare l'alternativa successiva
                sequenza_parziale.pop()



    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        # TODO
        # dizionario vuoto per avere un veloce 'listino prezzi' (id distributore - prezzo)
        prezzi_settimana = {}
        # scorro ogni distributore
        for d in self._distributori:
            # lista vuota per i prezzi della prima settimana
            prezzi = []
            # per ogni prezzo (anno) di quel distributore + chiamata get_prezzi
            for prezzo in d.get_prezzi():
                # filtro: se il mese coincide con quello scelto dall'utente E siamo tra i primi sette gg di quel mese
                if prezzo.data.month == mese and prezzo.data.day<=7:
                    # aggiungo alla lista prezzi
                    prezzi.append(prezzo.prezzo_litro)
            # associo l'id del distributore alla lista dei prezzi tramite il dizionario creato in precedenza
            prezzi_settimana[d.id] = prezzi
        return prezzi_settimana
