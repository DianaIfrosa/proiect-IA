import argparse
import copy
import os
import queue
import sys
import time


class Nod: # o stare
    def __init__(self, info, h):
        """
        Constructor in care initializez datele membre.
        Args:
            info : lista cu vase (tupluri) de tipul (cantitate_totala, cantitate_curenta, culoare)
            h: costul (estimat) de la nodul curent la un nod scop pe un anumit drum
        """
        self.info = info
        self.h = h

    def calculeaza_cost(self, nod):
        """
         Metoda care calculeaza costul de la o stare la alta (nodul curent si nodul dat).
         Se gasesc intai cele 2 vase modificate apoi se calculeaza pe cazuri costul final al turnarii.
         Args:
            nod: starea in care trece nodul curent
         Returns:
            cost_total: costul turnarii
        """

        configuratie1 = self.info
        configuratie2 = nod.info
        poz_primul_vas_schimbat = -1
        poz_al_doilea_vas_schimbat = -1
        cost_total = 0
        cost_vas1 = 0
        cost_vas2 = 0

        # gaseste cele 2 vase care au fost modificate (s-a turnat din unul in altul)
        for i in range(len(configuratie1)):
            vas1 = configuratie1[i]
            vas2 = configuratie2[i]
            if vas1[1]!=vas2[1] or vas1[2]!=vas2[2]:
                if poz_primul_vas_schimbat == -1:
                    poz_primul_vas_schimbat = i # retin id-ul lui
                else:
                    poz_al_doilea_vas_schimbat = i

        if configuratie1[poz_primul_vas_schimbat][1] < configuratie2[poz_primul_vas_schimbat][1]:
            # cantitatea de lichid din primul vas a crescut dupa turnare
            # inversez vasele ca sa stiu sigur ca din primul vas s-a turnat in al doilea
            poz_primul_vas_schimbat, poz_al_doilea_vas_schimbat = poz_al_doilea_vas_schimbat, poz_primul_vas_schimbat

        # calculeaza efectiv costul turnarii din primul vas schimbat in al doilea vas schimbat
        cantitate_turnata = min(configuratie1[poz_al_doilea_vas_schimbat][0] - configuratie1[poz_al_doilea_vas_schimbat][1], # se umple la maxim al doilea vas
                                configuratie1[poz_primul_vas_schimbat][1]) # se toarna totul din primul vas

        if configuratie1[poz_al_doilea_vas_schimbat][2] == 'nicio_culoare': # vasul al doilea era gol
            if configuratie1[poz_primul_vas_schimbat][2] == 'culoare_nedefinita':
                cost_total = cantitate_turnata
            else:
                cost_total = cantitate_turnata * Problema.costuri_culori[configuratie1[poz_primul_vas_schimbat][2]]

        else:
                if configuratie2[poz_al_doilea_vas_schimbat][2] != 'culoare_nedefinita': # s-a facut o combinatie valida
                    cost_total = cantitate_turnata * Problema.costuri_culori[configuratie1[poz_primul_vas_schimbat][2]]

                else: # nu s-a facut o combinatie valida
                    if configuratie1[poz_primul_vas_schimbat][2] == 'culoare_nedefinita':
                        cost_vas1 = cantitate_turnata # 1 * nr de litri
                    else:
                        cost_vas1 = cantitate_turnata * Problema.costuri_culori[configuratie1[poz_primul_vas_schimbat][2]]
                    if configuratie1[poz_al_doilea_vas_schimbat][2] == 'culoare_nedefinita':
                        cost_vas2 = configuratie1[poz_al_doilea_vas_schimbat][1] # 1 * nr de litri
                    else:
                        cost_vas2 = configuratie1[poz_al_doilea_vas_schimbat][1] * Problema.costuri_culori[configuratie1[poz_al_doilea_vas_schimbat][2]]
                    cost_total = cost_vas1 + cost_vas2

        return cost_total

    @classmethod
    def calculeaza_h(cls, configuratie, euristica = 'banala'):
        """
        Metoda statica care calculeaza h' in functie de configuratia data si un tip de euristica.
        Args:
            configuratie: starea curenta = lista cu vase (tupluri) de tipul (cantitate_totala, cantitate_curenta, culoare)
            euristica: tipul euristicii = banala, admisibila1, admisibila2, neadmisibila care determina o formula specifica
        Returns:
            h: valoarea functiei h' calculata
        """
        if euristica == 'banala':
            nod = Nod(configuratie, 0)
            if nod.test_stare_finala():
                return 0
            else:
                return 1

        elif euristica == 'admisibila1':
            multime_culori_finale = set()
            val_euristica = 0

            for (_, culoare) in Problema.stare_finala:
                multime_culori_finale.add(culoare)

            for (capacit, cant, cul) in configuratie:
                gasit = False # cauta vasul curent in configuratia finala
                cul_gasita = False # cauta culoarea curenta printre cele din configuratia finala

                if cul in multime_culori_finale:
                    for (cant_fin, cul_fin) in Problema.stare_finala:
                        if cul_fin == cul:
                            cul_gasita = True
                            if cant == cant_fin:
                                gasit = True
                                break

                # am gasit culoare din configuratia finala dar nu este in cantitatea buna
                # presupun ca se va muta un litru de lichid din acea culoare, deci adaug costul ei la valoarea euristica
                if cul_gasita is True and gasit is False:
                    val_euristica += Problema.costuri_culori[cul]
                    multime_culori_finale.remove(cul)

            return val_euristica

        elif euristica == 'admisibila2':
        # TODO admisibila2
            return 3
        elif euristica == 'neadmisibila':
            # pentru fiecare vas care nu se regaseste in configuratia finala se adauga la euristica costul culorii
            # din vas (daca e culoare valida)
            # se poate observa pe exemplul cu MEGA SCURT
            #todo descriere
            val_euristica = 0
            for (capacit, cant, cul) in configuratie:
                gasit = False  # cauta vasul curent in configuratia finala
                cul_gasita = False  # cauta culoarea curenta printre cele din configuratia finala

                for (cant_fin, cul_fin) in Problema.stare_finala:
                    if cul_fin == cul:
                        cul_gasita = True
                        if cant == cant_fin:
                            gasit = True
                            break
                if (gasit and cul_gasita) is False and cul != 'nicio_culoare' and cul != 'culoare_nedefinita':  # nu e in config finala
                    val_euristica += Problema.costuri_culori[cul]

            return val_euristica

    def test_stare_finala(self):
        """
        Metoda care verifica daca am ajuns la o configuratie (stare) finala sau nu.
        Returns:
              True daca e stare finala
              False daca nu e stare finala
        """
        configuratie_curenta = self.info
        configuratie_finala = Problema.stare_finala

        # verific ca fiecare vas final sa se regaseasca printre cele curente
        for vas_final in configuratie_finala:
            ok = 0
            for vas_curent in configuratie_curenta:
                if vas_final[0] == vas_curent[1] and vas_final[1] == vas_curent[2]:
                    ok = 1
                    break
            if ok == 0:
                return False
        return True

class NodParcurgere:

    def __init__(self, nod, parinte, g):
        """
        Constructor care initializeaza datele membre.
        Args:
            nod: (Nod) nodul curent
            parinte: (NodParcurgere) parintele nodului curent
            g: costul de la nodul start la un nod curent
        """
        self.nod = nod
        self.parinte = parinte
        self.g = g
        self.f = self.g + self.nod.h

    def expandeaza(self, euristica = 'banala'):
        """
        Calculeaza lista de succesori (obiecte NodParcurgere) a nodului curent, adica toate configurarile plecand de la cea curenta (toate turnarile)
        Args:
            euristica: tipul euristicii = banala, admisibila1, admisibila2, neadmisibila
        Returns:
            lista_succ: o lista cu elemente de tip NodParcurgere care sunt posibile mutari
        """
        lista_succ = []
        vase = self.nod.info
        for i in range(len(vase)): # caut un prim vas
            if vase[i][1] == 0: # primul vas nu trebuie sa fie vas gol
                continue
            for j in range(len(vase)): # caut un al doilea vas
                if i != j and vase[j][0] != vase[j][1]: # vase diferite, iar al doilea nu e plin
                    # torn din vasul i in vasul j
                    cantitate_max1 = vase[i][0]
                    cantitate_max2 = vase[j][0]

                    cantitate1 = vase[i][1]
                    cantitate2 = vase[j][1]

                    culoare1 = vase[i][2]
                    culoare2 = vase[j][2]

                    cantitate_turnata = min(cantitate_max2-cantitate2, cantitate1)

                    # mutare lichid
                    cantitate1 = cantitate1 - cantitate_turnata
                    cantitate2 = cantitate2 + cantitate_turnata

                    # aflare culoare
                    if culoare1 == culoare2:
                        culoare2 = culoare2
                    elif culoare1 == 'culoare_nedefinita' or culoare2 == 'culoare_nedefinita':
                        culoare2 = 'culoare_nedefinita'
                    elif culoare2 == 'nicio_culoare':
                        culoare2 = culoare1
                    else:
                        for combinatie in Problema.combinatii_culori:
                            if (combinatie[0] == culoare1 and combinatie[1] == culoare2) or (combinatie[0] == culoare2 and combinatie[1] == culoare1):
                                culoare2 = combinatie[2]
                                break
                        else: # nu s-a gasit o combinatie valida
                            culoare2 = 'culoare_nedefinita'

                    configuratie_noua = copy.deepcopy(vase)

                    if cantitate1 == 0:
                        culoare1 = 'nicio_culoare'

                    # actualizez cele 2 vase modificate
                    configuratie_noua[i] = (cantitate_max1, cantitate1, culoare1)
                    configuratie_noua[j] = (cantitate_max2, cantitate2, culoare2)

                    h = Nod.calculeaza_h(configuratie_noua, euristica)
                    succesor_nod = Nod(configuratie_noua, h)
                    g = self.g + self.nod.calculeaza_cost(succesor_nod)
                    succesor = NodParcurgere(succesor_nod, self, g)

                    if succesor.stare_cu_potential():
                        if self.stramos(succesor) is False:  # nodul gasit nu apare deja in drumul format (radacina -> nod curent)
                            lista_succ.append(succesor)

        return lista_succ

    def stare_cu_potential(self):
        """
        Functie care verifica daca nodul curent are potential.
        Returns:
            True daca starea curenta este una cu potential (poate conduce la solutii sau nu), deci merita sa fie expandata
            False, in caz contrar (sigur nu conduce la solutii)
        """

        vase = self.nod.info

        nr_combinatii = 0 # care se pot face intre vase
        nr_culori_finale = 0 # din vase
        nr_vase_pline = 0
        multime_culori_vase = set()
        multime_culori_finale = set() # din starea finala

        # verific sa pot obtine cantitatile din starea finala (sa nu am toate vasele cu capacitati maxime mai mici decat vreuna ceruta in starea finala)
        for (cantitate, culoare) in Problema.stare_finala:
            nr_vase = 0
            multime_culori_finale.add(culoare)
            for (capacit, cant, cul) in vase:
                if cantitate > capacit:
                    nr_vase = nr_vase + 1
            if nr_vase == len(vase):
                return False

        for (capacit, cant, cul) in vase:
            if cul != 'culoare_nedefinita' and cul != 'nicio_culoare':
                multime_culori_vase.add(cul)
            if capacit == cant:
                nr_vase_plin = nr_vase_pline + 1

        if len(multime_culori_vase) == 0: # nu mai am nicio culoare
            return False

        for cul in multime_culori_vase:
            for (cantitate, culoare) in Problema.stare_finala:
                if cul == culoare:
                    nr_culori_finale = nr_culori_finale + 1
                    break # ca sa nu numar de mai multe ori

        for (c1,c2, _) in Problema.combinatii_culori:
            if c1 in multime_culori_vase and c2 in multime_culori_vase:
                nr_combinatii = nr_combinatii + 1

        if (nr_combinatii == 0 or nr_vase_pline == len(vase)) and nr_culori_finale != len(multime_culori_finale):
        # m-am blocat (nu mai pot face combinatii sau vasele sunt toate pline) si nu am toate culorile finale
                return False

        return True

    def stramos(self, nodp):
        """
          Functie care verifica daca nodul dat ca parametru e stramosul celui curent.
          Args:
            nodp: obiect de tip NodParcurgere
          Returns:
            True, daca e stramos
            False, in caz contrar
        """
        nod_stramos = self.parinte

        # cat timp nu am ajuns la radacina
        while nod_stramos != None:
            if nod_stramos.nod.info == nodp.nod.info:
                return True
            nod_stramos = nod_stramos.parinte

        return False

    def drum(self):
        """
        Functie care calculeaza drumul de la nodul start pana la cel curent.
        Returns:
             drum = lista de stari (stare = lista de tupluri) din nodul initial pana in cel curent (final)
        """
        drum = []
        drum.append(self.nod.info)
        nod_stramos = self.parinte
        while nod_stramos != None:
            drum.append(nod_stramos.nod.info)
            nod_stramos = nod_stramos.parinte

        drum.reverse()
        return drum

    def afisare_drum(self, file_descriptor, timp_start, drum):
        """
        Functie care afiseaza drumul dat ca parametru dupa formatul cerut.
        Args:
            file_descriptor: descriptorul fisierului in care se scrie drumul
            timp_start: timestamp de la inceputul rularii unui anumit algoritm
            drum: lista de stari de la nodul start pana cel final
        """
        file_descriptor.write("Informatii solutie:\n")
        file_descriptor.write("Lungime drum: " + str(len(drum) - 1) + "\n")
        file_descriptor.write("Costul drumului: " + str(self.g) + "\n")
        file_descriptor.write("Timp gasire solutie: " + str(round((time.time()-timp_start)*1000)) + "ms\n")
        file_descriptor.write("Numarul maxim de noduri existente la un moment dat in memorie: " + str(Problema.nr_noduri_in_memorie) + "\n")
        file_descriptor.write("Numarul total de noduri generate: " + str(Problema.nr_noduri_total) + "\n")
        file_descriptor.write("\n")

        for nr_pas in range (len(drum)):
            pas = drum[nr_pas]
            if nr_pas != 0:
                Problema.afiseaza_mesaj(drum[nr_pas-1], drum[nr_pas], file_descriptor)
            for vas in range(len(pas)):
                file_descriptor.write(str(vas) + ': ')
                file_descriptor.write(str(pas[vas][0]) + ' ' + str(pas[vas][1]))
                if pas[vas][2] != 'nicio_culoare':
                    file_descriptor.write(' ' + str(pas[vas][2]) + '\n')
                else:
                    file_descriptor.write('\n')
            file_descriptor.write('\n')

    def in_lista(self, lista):
        """"
        Functie care cauta obiectul curent de tip NodParcurgere in lista data.
        Args:
            lista: lista de obiecte de tip NodParcurgere in care se cauta (de obicei, lista open sau lista closed)
        Returns:
            pozitie: pozitia elementului in lista sau -1 daca nu se gaseste
        """
        pozitie = -1
        for i in range(len(lista)):
            if self.nod.info == lista[i].nod.info:
                pozitie = i
        return pozitie


class Problema:

    # date statice
    cale_fisier_input = ""
    cale_folder_output = ""
    timeout = 0

    nsol = 0
    aux_nsol = 0 # retine numarul de solutii gasite pana la acel moment; ajuta in simularea transmiterii valorii prin referinta in functii

    costuri_culori= {}
    combinatii_culori = []
    stare_finala = []

    nod_start = Nod([], 0)

    nr_noduri_total = 0
    nr_noduri_in_memorie = 0

    def __init__(self, _cale_fisier_input, _cale_folder_output, _nsol, _timeout):
        """
        Constructor in care salvez argumentele primite in linia de comanda si initializez datele clasei precum:
            costuri_culori: dictionar in care retin culorile ca fiind chei si valorile ca fiind costurile culorilor
            combinatii_culori: lista de tupluri de tipul (culoare1, culoare2, culoare3)
            stare_finala: lista de tupluri de genul (cantitate, culoare)
            nod_start: configuratia din care se pleaca
        Args:
            _cale_fisier_input: calea fisierului de unde se citesc datele
            _cale_folder_output: calea folderului unde se vor afla fisiere cu rezultate pentru fiecare algoritm
            _nsol: numarul de solutii de calculat pentru algoritmii DF, BF, DFI, A*, IDA*
            _timeout: timpul dupa care sa se opreasca un algoritm
        """

        Problema.cale_fisier_input = _cale_fisier_input
        Problema.cale_folder_output = _cale_folder_output
        Problema.nsol = _nsol
        Problema.timeout = _timeout

        # citesc datele din fisierul de input si initializez celelalte date statice
        # stare_initiala e lista de tupluri de genul (cantitate_totala, cantitate_curenta, culoare) sau (cantitate_totala, 0)
        Problema.costuri_culori, Problema.combinatii_culori, stare_initiala, Problema.stare_finala = self.citire(cale_fisier_input)
        Problema.nod_start = Nod(stare_initiala, Nod.calculeaza_h(stare_initiala))

    @classmethod
    def citire(cls, cale_fisier_input):
        """
        Metoda care citeste datele din fisierul de input si le valideaza.
        Args:
            cale_fisier_input: calea fisierului de unde se citesc datele
        Returns:
            date membre ale clasei Problema cu care se vor rula algoritmii (costuri_culori, combinatii_culori, stare_initiala, stare_finala)
        """

        # validare pentru calea fisierului de input
        try:
            file_descriptor = open(cale_fisier_input)
        except:
            print("Fisierul de input nu a putut fi deschis!")
            sys.exit(0)

        # citire si validare pentru corectitudinea fisierului de input
        try:
            s = file_descriptor.readline()
            costuri_culori = {}
            combinatii_culori = []
            stare_initiala = []
            stare_finala= []

            # parsez linie cu linie fisierul de input dat
            while s != "":
                if s[-1] == '\n':
                     s = s[:-1] # elimin new line de la finalul liniei
                if s == "stare_initiala":
                    s = file_descriptor.readline()
                    s = s[:-1]
                    if s == "":
                        raise Exception  # nu am stare initiala efectiva
                    while s != "stare_finala":
                        valori = s.split()
                        if len(valori) < 2 or len(valori) > 3:
                            raise Exception # numar invalid de valori pentru un vas
                        if len(valori) == 2: # cantitate curenta 0
                            stare_initiala.append((int(valori[0]), int(valori[1]), "nicio_culoare"))
                        else:
                            if valori[2] not in costuri_culori.keys():
                                raise Exception # culoare necunoscuta in starea initiala
                            stare_initiala.append((int(valori[0]), int(valori[1]), valori[2]))

                        s = file_descriptor.readline()
                        if s == "":
                            raise Exception # nu am stare finala
                        s = s[:-1]

                elif s == "stare_finala":
                    s = file_descriptor.readline()
                    if s == "":
                        raise Exception # nu am stare finala efectiva
                    while s != "":
                        valori = s.split()
                        if len(valori) != 2:
                            raise Exception # numar invalid de valori pentru un vas
                        if valori[1] not in costuri_culori.keys():
                            raise Exception  # culoare necunoscuta in starea finala
                        stare_finala.append((int(valori[0]), valori[1]))
                        s = file_descriptor.readline()

                else: # primele randuri cu combinatiile de culori si costurile
                    valori = s.split()
                    if len(valori) == 3:
                        combinatii_culori.append((valori[0], valori[1], valori[2]))
                    elif len(valori) == 2:
                        costuri_culori[valori[0]] = int(valori[1])
                    else:
                        raise Exception # numar invalid de valori
                    s = file_descriptor.readline()

            if len(stare_finala) > len(stare_initiala):
                raise Exception  # am prea putine vase disponibile

        except Exception:
            print("Fisierul de input este invalid!")
            sys.exit(0)

        file_descriptor.close()
        return costuri_culori, combinatii_culori, stare_initiala, stare_finala

    def ruleaza_algoritmi(self):
        """
        Metoda care ruleaza pe rand algoritmii BF, DF, DFI, A* optimizat, A*, IDA*.
        """
        # cautare neinformata
        Problema.bfs()
        Problema.rezolva_dfs()
        Problema.rezolva_dfi()

        # cautare informata
        # A* optimizat
        Problema.a_star_optimizat('banala')
        Problema.a_star_optimizat('admisibila1')
        Problema.a_star_optimizat('admisibila2')
        Problema.a_star_optimizat('neadmisibila')

        # A* neoptimizat
        Problema.a_star('banala')
        Problema.a_star('admisibila1')
        Problema.a_star('admisibila2')
        Problema.a_star('neadmisibila')

        # IDA*
        Problema.rezolva_ida_star('banala')
        Problema.rezolva_ida_star('admisibila1')
        Problema.rezolva_ida_star('admisibila2')
        Problema.rezolva_ida_star('neadmisibila')

    @classmethod
    def testeaza_timeout(cls, timp_start):
        """
        Functie care testeaza daca a trecut timpul alocat unui algoritm.
        Args:
            timp_start: cand a inceput rularea algoritmului
        Returns:
            True, daca mai este timp din cel alocat
            False, daca timpul alocat a expirat
        """
        timp_acum = time.time() # secunde
        if (timp_acum - timp_start) > Problema.timeout:
            return False
        return True

    @classmethod
    def afiseaza_mesaj(cls, configuratie1, configuratie2, file_descriptor):
        """
        Functie care afiseaza mesajul corespunzator fiecarei turnari dintr-un vas in altul.
        Args:
            configuratie1: starea din care se pleaca
            configuratie2: starea in care se ajunge
            file_descriptor: fisierul unde sa se scrie mesajul
        """
        # gaseste cele 2 vase care au fost modificate (s-a turnat din unul in altul)
        poz_primul_vas_schimbat = -1
        poz_al_doilea_vas_schimbat = -1
        for i in range(len(configuratie1)):
            vas1 = configuratie1[i]
            vas2 = configuratie2[i]
            if vas1[1] != vas2[1] or vas1[2] != vas2[2]:
                if poz_primul_vas_schimbat == -1:
                    poz_primul_vas_schimbat = i  # retin id-ul lui
                else:
                    poz_al_doilea_vas_schimbat = i

        if configuratie1[poz_primul_vas_schimbat][1] < configuratie2[poz_primul_vas_schimbat][1]:
            # cantitatea de lichid din primul vas a crescut dupa turnare
            # inversez vasele ca sa stiu sigur ca din primul vas s-a turnat in al doilea
            poz_primul_vas_schimbat, poz_al_doilea_vas_schimbat = poz_al_doilea_vas_schimbat, poz_primul_vas_schimbat
        # calculeaza efectiv costul turnarii din primul vas schimbat in al doilea vas schimbat
        cantitate_turnata = min(configuratie1[poz_al_doilea_vas_schimbat][0] - configuratie1[poz_al_doilea_vas_schimbat][1],# se umple la maxim al doilea vas
                                configuratie1[poz_primul_vas_schimbat][1])  # se toarna totul din primul vas
        file_descriptor.write('Din vasul ' + str(poz_primul_vas_schimbat) + ' s-au turnat ' + str(cantitate_turnata) + ' litri de culoare ' +
                configuratie1[poz_primul_vas_schimbat][2] + ' in vasul ' + str(poz_al_doilea_vas_schimbat) + '\n')

    @classmethod
    def a_star_optimizat(cls, euristica):
        """
        Algoritmul de A* optimizat cu listele open si closed
        Args:
            euristica: tipul euristicii = banala, admisibila1, admisibila2, neadmisibila
        """
        timp_start = time.time()
        lista_open = []  # retine obiecte de tip NodParcurgere care urmeaza sa fie expandate
        lista_closed = []  # retine obiecte de tip NodParcurgere care au fost deja expandate
        Problema.aux_nsol = Problema.nsol
        Problema.nr_noduri_in_memorie = 1
        Problema.nr_noduri_total = 1

        # daca nu exista folderul de output, il creez
        if not os.path.exists(Problema.cale_folder_output + '\AStarOptimizat'):
            os.mkdir(Problema.cale_folder_output + '\AStarOptimizat')

        cale_fisier_output_completa = Problema.cale_folder_output + '\AStarOptimizat' + '\\' + euristica + '.txt'

        file_descriptor = open(cale_fisier_output_completa, 'w')

        nod_start = NodParcurgere(Problema.nod_start, None, 0)
        lista_open.append(nod_start)

        if not nod_start.stare_cu_potential():
            file_descriptor.write("Nu exista solutii!")
            file_descriptor.close()
            return

        if Problema.nod_start.test_stare_finala():
            file_descriptor.write("Starea initiala e si stare finala!")
            file_descriptor.close()
            return

        while lista_open:  # cat timp nu e vida
            Problema.nr_noduri_in_memorie = max(Problema.nr_noduri_in_memorie, len(lista_open) + len(lista_closed))

            nod_curent = lista_open.pop(0)
            lista_closed.append(nod_curent)
            if not Problema.testeaza_timeout(timp_start):
                file_descriptor.write("Solutia a depasit timpul alocat!\n")
                file_descriptor.close()
                return
            if nod_curent.nod.test_stare_finala() is True:
                drum = nod_curent.drum()
                Problema.aux_nsol = Problema.aux_nsol - 1
                nod_curent.afisare_drum(file_descriptor, timp_start, drum)
                break

            succesori = nod_curent.expandeaza(euristica)
            Problema.nr_noduri_total += len(succesori)

            # nod_curent e parinte pentru succ
            for succ in succesori:
                nod_nou = None
                poz_in_open = succ.in_lista(lista_open)
                poz_in_closed = succ.in_lista(lista_closed)

                # nodul se afla in open
                if poz_in_open != -1:
                    if lista_open[poz_in_open].f > succ.f:
                        lista_open.pop(poz_in_open)
                        succ.parinte = nod_curent

                        cost = nod_curent.nod.calculeaza_cost(succ.nod)
                        succ.g = nod_curent.g + cost
                        succ.f = succ.g + succ.nod.h

                        nod_nou = succ

                # nodul se afla in closed
                elif poz_in_closed != -1:
                    # calculez f-ul pentru acest succesor
                    cost = nod_curent.nod.calculeaza_cost(succ.nod)
                    g = nod_curent.g + cost
                    f = g + succ.nod.h

                    # daca f-ul gasit acum este mai bun fata de cel precedent
                    if f < lista_closed[poz_in_closed].f:
                        succ.parinte = nod_curent
                        lista_closed.pop(poz_in_closed)
                        succ.f = f
                        succ.g = g
                        nod_nou = succ
                else:
                    # nu sunt nici in open, nici in closed
                    nod_nou = succ
                if nod_nou != None:
                    lista_open.append(nod_nou)
                    # sortez lista open crescator dupa f si apoi descrescator dupa g
                    lista_open.sort(key=lambda x: (x.f, -x.g))

        if Problema.nsol == Problema.aux_nsol:
            file_descriptor.write("Nu exista solutie!")

        file_descriptor.close()

    @classmethod
    def rezolva_dfs(cls):
        """
        Functie care apeleaza algoritmul DFS si pregateste elementele necesare lui (stiva, nr sol,
        cale fisier output, timp start)
        """
        timp_start = time.time()
        stiva = queue.LifoQueue()
        nod_start = NodParcurgere(Problema.nod_start, None, 0)

        Problema.aux_nsol = Problema.nsol
        Problema.nr_noduri_in_memorie = 1
        Problema.nr_noduri_total = 1

        cale_fisier_output_completa = Problema.cale_folder_output + '\DFS.txt'
        file_descriptor = open(cale_fisier_output_completa, 'w')

        if not nod_start.stare_cu_potential():
            file_descriptor.write("Nu exista solutii!")
            file_descriptor.close()
            return

        if Problema.nod_start.test_stare_finala():
            file_descriptor.write("Starea initiala e si stare finala!")
            file_descriptor.close()
            return

        stiva.put(nod_start)
        Problema.dfs(stiva, file_descriptor, timp_start)

        if not Problema.testeaza_timeout(timp_start):
            file_descriptor.write("Solutia a depasit timpul alocat!\n")
            file_descriptor.close()
            return

        if Problema.nsol == Problema.aux_nsol:
            file_descriptor.write("Nu exista solutie!")

        elif Problema.aux_nsol != 0 :
            file_descriptor.write("\nNumarul maxim de drumuri este mai mic decat cel cerut!")

        file_descriptor.close()

    @classmethod
    def dfs(cls, stiva, file_descriptor, timp_start):
        """
        Algoritmul efectiv de DF.
        Args:
            stiva: stiva in care retin nodurile parcurse pana atunci; o folosesc pentru a afisa mai multe solutii
            file_descriptor: file descriptor pentru fisierul de output unde afisez drumurile
            timp_start: timestamp de cand a inceput algoritmul
        """
        if not Problema.testeaza_timeout(timp_start):
            return

        if Problema.aux_nsol == 0:
            return

        # simulez un peek
        nod_curent = stiva.get()
        stiva.put(nod_curent)

        Problema.nr_noduri_in_memorie = max(Problema.nr_noduri_in_memorie, stiva.qsize())

        if nod_curent.nod.test_stare_finala():
            drum = nod_curent.drum()
            Problema.aux_nsol = Problema.aux_nsol - 1
            file_descriptor.write('-' * 50 + "Solutia nr. " + str(Problema.nsol - Problema.aux_nsol) + '-' * 50 + '\n')
            nod_curent.afisare_drum(file_descriptor, timp_start,drum)
            return

        succesori = nod_curent.expandeaza()
        Problema.nr_noduri_total += len(succesori)

        for succ in succesori:
                stiva.put(succ)
                Problema.dfs(stiva, file_descriptor, timp_start)
        stiva.get()

    @classmethod
    def bfs(cls):
        """
        Algoritmul efectiv de BF.
        """
        timp_start = time.time()
        coada = queue.Queue()
        nod_start = NodParcurgere(Problema.nod_start, None, 0)

        Problema.aux_nsol = Problema.nsol
        Problema.nr_noduri_in_memorie = 1
        Problema.nr_noduri_total = 1

        cale_fisier_output_completa = Problema.cale_folder_output + '\BFS.txt'
        file_descriptor = open(cale_fisier_output_completa, 'w')

        if not nod_start.stare_cu_potential():
            file_descriptor.write("Nu exista solutii!")
            file_descriptor.close()
            return

        if Problema.nod_start.test_stare_finala():
            file_descriptor.write("Starea initiala e si stare finala!")
            file_descriptor.close()
            return

        coada.put(nod_start)
        in_coada = [] # retin info ale nodurilor care sunt in coada
        in_coada.append(nod_start.nod.info)

        while not coada.empty() and Problema.aux_nsol > 0:
            Problema.nr_noduri_in_memorie = max(Problema.nr_noduri_in_memorie, coada.qsize())

            # extrag cate un nod din coada
            nod_curent = coada.get()
            in_coada.remove(nod_curent.nod.info)

            if not Problema.testeaza_timeout(timp_start):
                file_descriptor.write("Solutia a depasit timpul alocat!\n")
                file_descriptor.close()
                return

            if nod_curent.nod.test_stare_finala():
                drum = nod_curent.drum()
                Problema.aux_nsol = Problema.aux_nsol - 1
                file_descriptor.write('-' * 50 + "Solutia nr. " + str(Problema.nsol - Problema.aux_nsol) + '-' * 50 + '\n')
                nod_curent.afisare_drum(file_descriptor, timp_start, drum)
                continue

            succesori = nod_curent.expandeaza()
            Problema.nr_noduri_total += len(succesori)

            for succ in succesori:
                if succ.nod.info not in in_coada: # nodul gasit nu e deja in coada
                    coada.put(succ)
                    in_coada.append(succ.nod.info)

        if Problema.nsol == Problema.aux_nsol:
            file_descriptor.write("Nu exista solutie!")
        elif Problema.aux_nsol != 0:
            file_descriptor.write("\nNumarul maxim de drumuri este mai mic decat cel cerut!")

        file_descriptor.close()

    @classmethod
    def rezolva_dfi(cls):
        """
        Functie care apeleaza algoritmul DFI si pregateste elementele necesare lui (lista de drumuri vizitate, nr sol,
        cale fisier output, timp start, adancime cautare)
        """
        adancime = 1
        final_graf = False
        timp_start = time.time()
        drumuri_vizitate = []
        nod_start = NodParcurgere(Problema.nod_start, None, 0)

        Problema.aux_nsol = Problema.nsol
        Problema.nr_noduri_total = 1

        cale_fisier_output_completa = Problema.cale_folder_output + '\DFI.txt'
        file_descriptor = open(cale_fisier_output_completa, 'w' )

        if not nod_start.stare_cu_potential():
            file_descriptor.write("Nu exista solutii!")
            file_descriptor.close()
            return

        if Problema.nod_start.test_stare_finala():
            file_descriptor.write("Starea initiala e si stare finala!")
            file_descriptor.close()
            return

        while final_graf is False:
            if Problema.aux_nsol == 0:
                break

            if not Problema.testeaza_timeout(timp_start):
                file_descriptor.write("Solutia a depasit timpul alocat!\n")
                file_descriptor.close()
                return

            Problema.nr_noduri_in_memorie = 1  # resetez numarul de noduri curente la fiecare cautare noua
            drumuri_vizitate, final_graf = Problema.dfi(nod_start, timp_start, 0, adancime, drumuri_vizitate, file_descriptor)
            adancime = adancime + 1

        if Problema.nsol == Problema.aux_nsol:
            file_descriptor.write("Nu exista solutie!")

        elif Problema.aux_nsol != 0:
            file_descriptor.write("\nNumarul maxim de drumuri este mai mic decat cel cerut!")

        file_descriptor.close()

    @classmethod
    def dfi(cls, nod_curent, timp_start, adancime_curenta, adancime_maxima, drumuri_vizitate, file_descriptor):
        """
        Algoritmul efectiv de DFI.
        Args:
            nod_curent: nodul curent din cautare
            timp_start: timestamp de cand a inceput algoritmul
            adancime_curenta: la ce adancime in graf ma aflu
            adancime_maxima: adancime maxima din graf pentru cautarea curenta
            drumuri_vizitate: lista cu solutiile gasite pana acum
            file_descriptor: file descriptor pentru fisierul de output unde afisez drumurile
        Returns:
            drumuri_vizitate: lista cu solutiile gasite pana acum
            variabila booleana: indica daca am ajuns la finalul cautarii sau nu (a trecut timpul alocat,
            am ajuns la adancimea maxima, am gasit solutie finala)
        """

        if not Problema.testeaza_timeout(timp_start):
            return drumuri_vizitate, True

        if nod_curent.nod.test_stare_finala():
            drum = nod_curent.drum()
            if drum not in drumuri_vizitate:
                Problema.aux_nsol = Problema.aux_nsol - 1
                file_descriptor.write('-' * 50 + "Solutia nr. " + str(Problema.nsol - Problema.aux_nsol) + '-' * 50 + '\n')
                nod_curent.afisare_drum(file_descriptor, timp_start, drum)
                drumuri_vizitate.append(drum)
            return drumuri_vizitate, True

        succesori = nod_curent.expandeaza()
        Problema.nr_noduri_total += len(succesori)
        Problema.nr_noduri_in_memorie += 1

        if adancime_curenta == adancime_maxima:
            if len(succesori) > 0: # nu am ajuns la finalul grafului
                return drumuri_vizitate, False
            else:
                return drumuri_vizitate, True

        final_graf = True # merg recursiv in fii
        for succ in succesori:
            drumuri_vizitate, final_graf_recursiv = Problema.dfi(succ, timp_start, adancime_curenta+1, adancime_maxima, drumuri_vizitate, file_descriptor)

            if Problema.aux_nsol == 0:
                return drumuri_vizitate, True

            final_graf = final_graf and final_graf_recursiv

        return drumuri_vizitate, final_graf

    @classmethod
    def a_star(cls, euristica):
        """
        Algoritmul de A* (care da toate drumurile).
        Args:
            euristica: tipul euristicii = banala, admisibila1, admisibila2, neadmisibila
        """
        timp_start = time.time()
        solutie_gasita = False
        coada_prioritati = []
        nod_start = NodParcurgere(Problema.nod_start, None, 0)

        Problema.aux_nsol = Problema.nsol
        Problema.nr_noduri_in_memorie = 1
        Problema.nr_noduri_total = 1

        # daca nu exista folderul de output, il creez
        if not os.path.exists(Problema.cale_folder_output + '\AStar'):
            os.mkdir(Problema.cale_folder_output + '\AStar')

        cale_fisier_output_completa = Problema.cale_folder_output + '\AStar' + '\\' + euristica + '.txt'
        file_descriptor = open(cale_fisier_output_completa, 'w')

        coada_prioritati.append(nod_start)
        if not nod_start.stare_cu_potential():
            file_descriptor.write("Nu exista solutii!")
            file_descriptor.close()
            return

        if Problema.nod_start.test_stare_finala():
            file_descriptor.write("Starea initiala e si stare finala!")
            file_descriptor.close()
            return

        while coada_prioritati:  # cat timp nu e vida
            Problema.nr_noduri_in_memorie = max(Problema.nr_noduri_in_memorie, len(coada_prioritati))

            nod_curent  = coada_prioritati.pop(0)
            if not Problema.testeaza_timeout(timp_start):
                file_descriptor.write("Solutia a depasit timpul alocat!\n")
                file_descriptor.close()
                return
            if nod_curent.nod.test_stare_finala():
                drum = nod_curent.drum()
                Problema.aux_nsol = Problema.aux_nsol - 1
                file_descriptor.write('-' * 50 + "Solutia nr. " + str(Problema.nsol - Problema.aux_nsol) + '-' * 50 + '\n')
                nod_curent.afisare_drum(file_descriptor, timp_start, drum)
                solutie_gasita = True
                if Problema.aux_nsol == 0:
                    break
                continue

            succesori = nod_curent.expandeaza(euristica)
            Problema.nr_noduri_total += len(succesori)

            # nod_curent e parinte pentru succ
            for succ in succesori:
                coada_prioritati.append(succ)
                # sortez lista open crescator dupa f si apoi descrescator dupa g
                coada_prioritati.sort(key=lambda x: (x.f, -x.g))

        if solutie_gasita is False:
            file_descriptor.write("Nu exista solutie!")
        file_descriptor.close()

    @classmethod
    def rezolva_ida_star(cls, euristica):
        """
        Functie care apeleaza algoritmul IDA* si pregateste elementele necesare lui (timp start, nr sol,
        file descriptor, lista drumuri gasite)
        Args:
            euristica: tipul euristicii = banala, admisibila1, admisibila2, neadmisibila
        """
        timp_start = time.time()

        Problema.aux_nsol = Problema.nsol
        Problema.nr_noduri_total = 1

        nod_start = NodParcurgere(Problema.nod_start, None, 0)

        # daca nu exista folderul de output, il creez
        if not os.path.exists(Problema.cale_folder_output + '\IDAStar'):
            os.mkdir(Problema.cale_folder_output + '\IDAStar')

        cale_fisier_output_completa = Problema.cale_folder_output + '\IDAStar' + '\\' + euristica + '.txt'
        file_descriptor = open(cale_fisier_output_completa, 'w')

        if not nod_start.stare_cu_potential():
            file_descriptor.write("Nu exista solutii!")
            file_descriptor.close()
            return

        if Problema.nod_start.test_stare_finala():
            file_descriptor.write("Starea initiala e si stare finala!")
            file_descriptor.close()
            return

        drumuri_vizitate = []
        limita = nod_start.f # pentru a nu explora noduri cu valori ale lui f foarte mari
        while True:
            Problema.nr_noduri_in_memorie = 1  # resetez numarul de noduri curente la fiecare cautare
            rezultat = Problema.ida_star(nod_start, limita, euristica, file_descriptor, timp_start, drumuri_vizitate)
            if rezultat == -1:
                break
            if rezultat == float('inf'):
                if Problema.nsol == Problema.aux_nsol:
                    file_descriptor.write("Nu exista solutie!")
                elif Problema.aux_nsol != 0:
                    file_descriptor.write("\nNumarul maxim de drumuri este mai mic decat cel cerut!")
                break
            limita = rezultat

        file_descriptor.close()

    @classmethod
    def ida_star(cls, nod_curent, limita, euristica, file_descriptor, timp_start, drumuri_vizitate):
        """
        Algoritmul efectiv de IDA*.
        Args:
            nod_curent: nodul curent din cautare
            limita: pana la ce valoare a functiei f' merg in cautarea curenta
            euristica: tipul euristicii = banala, admisibila1, admisibila2, neadmisibila
            file_descriptor: file descriptor pentru fisierul de output unde afisez drumurile
            timp_start: timestamp de cand a inceput algoritmul
            drumuri_vizitate: lista cu solutiile gasite pana acum
        Returns:
            valoarea minima a functiei f' din nodul curent; -1 daca trebuie sa opresc cautarea (timp alocat depasit,
            am gasit toate solutiile cerute)
        """
        if nod_curent.f > limita:
            return nod_curent.f

        if not Problema.testeaza_timeout(timp_start):
            file_descriptor.write("Solutia a depasit timpul alocat!\n")
            return -1

        if nod_curent.nod.test_stare_finala():
            drum = nod_curent.drum()
            if drum not in drumuri_vizitate:
                Problema.aux_nsol = Problema.aux_nsol - 1
                drumuri_vizitate.append(drum)
                file_descriptor.write('-' * 50 + "Solutia nr. " + str(Problema.nsol - Problema.aux_nsol) + '-' * 50 + '\n')
                nod_curent.afisare_drum(file_descriptor, timp_start, drum)
                if Problema.aux_nsol == 0:
                    return -1
            return nod_curent.f

        succesori = nod_curent.expandeaza(euristica)
        Problema.nr_noduri_total += len(succesori)
        Problema.nr_noduri_in_memorie += 1
        f_minim = float('inf')

        for succ in succesori:
            rezultat = Problema.ida_star(succ, limita, euristica, file_descriptor, timp_start, drumuri_vizitate)

            if rezultat == -1:
                return -1

            f_minim = min(f_minim, rezultat)

        return f_minim

if __name__ == "__main__":

    # parsare argumente
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", required=True, help="calea folderului cu fisierul de input")
    parser.add_argument("-out", required=True, help="calea folderului cu fisierele de output")
    parser.add_argument("-nrsol", required=True, help="numarul de solutii de calculat")
    parser.add_argument("-time", required=True, help="timeout")

    args = vars(parser.parse_args())
    folder_input = args['in']
    folder_output = args['out']
    nsol = int(args['nrsol'])
    timeout = int(args['time'])

    # prelucrare fisiere
    # daca nu exista folderul de output, il creez
    if not os.path.exists(folder_output):
        os.mkdir(folder_output)

    fisiere_intrare = os.listdir(folder_input)

    # pentru fiecare fisier de intrare ii calculez calea intreaga si denumirea fisierului de output corespunzator (urmata de /A* sau /DFS etc.)
    for nume_fisier in fisiere_intrare:
        cale_fisier_input = folder_input + "\\" + nume_fisier
        cale_folder_output = folder_output + "\output_" + nume_fisier
        cale_folder_output = cale_folder_output[:-4] # elimin .txt de la final pentru a putea crea
        # daca nu exista folderul de output, il creez
        if not os.path.exists(cale_folder_output):
            os.mkdir(cale_folder_output)
        problema = Problema(cale_fisier_input, cale_folder_output, nsol, timeout)
        problema.ruleaza_algoritmi()
