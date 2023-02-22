# Proiect Inteligenta Artificiala

## Context
&nbsp; Consideram ca avem niste vase cu apa colorata. Despre fiecare vas stim capacitatea maxima si cat lichid contine. Pot exista si vase vide. De asemenea pentru combinatia a doua culori de lichide stim ce culoare rezulta din combinatia lor. Pentru combinatiile de culori neprecizate, inseamna ca nu ne intereseaza rezultatul si desi le putem amesteca (uneori e nevoie sa depozitam apa intr-un vas, ca sa facem loc pentru alte mutari) culoarea rezultata nu va aparea in starea solutie niciodata (puteti considera un identificator special pentru acea culoare, de exemplu "nedefinit"). Evident, apa cu culoare nedefinita nu poate fi folosita pentru a obtine alte culori (apa cu culoare nedefinita, amestecata cu orice rezulta in culoare nedefinita).

## Stări și tranziții
Mutările se fac ținând cont de următoarele reguli: 
* Lichidul dintr-un vas nu poate fi varsat decat in alt vas (nu dorim sa pierdem din lichid; nu se varsa in exterior).  
* Indiferent de cantitatea de lichid turnată și cea existentă in vas, culoarea rezultată în vasul în care s-a turnat apa e fie e culoarea indicată în fișierul de intrare pentru combinarea celor două culori, fie nedefinită dacă nu se specifică în fișîerul de intrare rezultatul unei astfel de combinări. Apa de culoare nedefinită, turnată peste orice altă culoare, va transforma apa din vasul în care se toarnă în apă de culoare nedefinită.
* Apa se poate turna dintr-un vas în altul doar în două moduri: fie se toarnă apă până se golește vasul din care turnăm, fie se umple vasul în care turnăm. Nu se pot turna cantități intermediare.

## Costul
&nbsp; Costul turnării este dat de cati litri de o anumită culoare au fost turnați înmulțit cu costul culorii respective. în cazul în care rezultatul turnării este o culoare nedefinită, costul va fi numărul de litri turnați înmulțit cu cât costă un litru din acea culoare, adunat cu numărul de litri din vasul în care se toarnă înmulțit cu costul asociat culorii din el. În cazul în care unul sau ambele vase au deja culoare nedefinită, se consideră cost 1 pentru un litru de culoare nedefinită.

## Starea finala (scopul) 
Considerăm că ajungem în starea finală când obținem cantități fixe (cerute în fișierul de intrare) de apă de o anumită culoare.

## Fisierul de intrare
&nbsp; Primele randuri se vor referi la combinatiile de culori. Vor fi cate 3 pe rand, de exemplu:
c1 c2 c3
cu semnificatia ca din combinarea culorii c1 cu c2 rezulta c3 (nu conteaza cantitatea apei amestecate ci doar culoarea ei). Combinatiile sunt simetrice, adica, daca din c1 combinat cu c2 rezulta c3, atunci si din c2 combinat cu c1 rezulta c3.
Sub randurile cu culorile avem rânduri cu prețul pe litru al manipulării fiecărei culori. Apoi, un rand cu textul "stare_initiala", dupa care urmeaza starea initiala a vaselor. Pentru fiecare vas se precizeaza cantitatea maxima a acestuia, cata apa are si ce culoare are apa. Toate cantitatile sunt date in litri. In cazul in care cantitatea de apa este 0, lipseste si culoarea. Dupa precizarea starii, initiale, avem textul "stare_finala". Sub acest text pe cate un rand, se specifica o cantitate si o culoare, cu sensul ca in starea finala, pentru fiecare astfel de cantitate (si culoare) precizata trebuie sa existe un vas care sa o contina.
Tranzitia consta din turnarea apei dintr-un vas in altul. Se considera ca nu stim sa masuram litrii altfel decat folosind vasele. Cand turnam lichid putem turna ori pana se termina lichidul din vasul din care turnam, ori pana se umple vasul in care turnam.. Nu se varsa lichid in exterior, lichidul nu da pe afara. Asfel daca, de exemplu, am un vas cu capacitate 6 si cantitate 3 si unul cu capacitate 4 si cantitate 2, nu putem turna din primul doar un litru, ci doar 2 litri (fiindca sunt 4-2=2 litri liberi in vasul al doilea). In felul asta ramanem cu un litru in primul.
Ne oprim din cautat cand reusim sa ajungem in starea finala: cu alte cuvinte, cand fiecare cantitate de apa colorata specificata in stare se gaseste in cate un vas (nu ne intereseaza cantitatile de apa din restul vaselor)

Exemplu de fisier de intrare:  
rosu albastru mov  
albastru galben verde  
mov verde maro  
rosu 2  
albastru 5  
mov 7  
galben 3  
verde 5  
maro 4  
stare_initiala  
5 4 rosu  
2 2 galben  
3 0  
7 3 albastru  
1 0  
4 3 rosu  
stare_finala  
3 mov  
2 verde  

## Fișier output  
&nbsp; In fisierul de output se vor afisa starile intermediare, pornind de la starea initiala la starea finala. Pentru fiecare vase se aloca un id (poate fi numarul de ordine din fisier - de exemplu, vasul cu id-ul 0 este cel cu capacitate 5 si 4 litri de apa rosie)
O stare se va afisa, afisand intai (daca nu e vorba de prima stare) ce miscare s-a facut, in formatul:
Din vasul X s-au turnat L litri de apa de culoare C in vasul Y.  

Apoi se va afisa starea vaselor astfel:
id_vas: capacitate_maxima cantitate_apa culoare_apa  

De exemplu, pentru un succesor al starii initiale de mai sus am avea:  
Din vasul 0 s-au turnat 1 litri de apa de culoare rosu in vasul 4.  
0: 5 3 rosu  
1: 2 2 galben  
2: 3 0  
3: 7 3 albastru  
4: 1 1 rosu  
5: 4 3 rosu  
 

Insa starea initiala s-ar fi afisat in drum fara randul cu mutarea:  
0: 5 4 rosu  
1: 2 2 galben  
2: 3 0  
3: 7 3 albastru  
4: 1 0  
5: 4 3 rosu  


Nu ne preocupam de corectitudine gramaticala ("culoare rosie" in loc de "culoare rosu").  
Cand se afiseaza "drumul" de stari, se afiseaza si prima stare in formatul de mai sus (cu id-urile vaselor), dar fara mesajul mutarii.  
Un exemplu de distributie a apei intr-o stare finala este (observam ca nu am precizat culoarea pentru cantitate 0):  
0: 5 5 rosu  
1: 2 1 galben  
2: 3 1 albastru  
3: 7 2 verde  
4: 1 0  
5: 4 3 mov  

 
Indicatie: nu precizati toate starile finale posibile, ci faceti o functie care testeaza daca o stare indeplineste conditia ceruta.  

## Alte precizari: 
* Pentru fisierele de input nu e obligatoriu sa folositi nume reale de culori.
* Nu e obligatoriu sa se foloseasca toate culorile in starea finala.
* În afișarea drumurilor-soluție, se va afișa pentru fiecare nod și indicele stării (nodului) în drum.
