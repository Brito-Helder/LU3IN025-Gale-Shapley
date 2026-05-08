import numpy as np
from collections import deque
import heapq


def lecture_PrefEtu(file):
    """Lit PrefEtu.txt et retourne une matrice contenant le classement des parcours selon les préférences des étudiants"""
    fic = open(file, "r", encoding="utf-8-sig")
    contenu = fic.readlines()
    fic.close()
    
    contenu[0]=contenu[0].split()
    nbEtu = int(contenu[0][0])
    nbParcours = 10

    matrice = np.zeros((nbEtu, nbParcours), dtype=int)
    classement = np.zeros((nbEtu, nbParcours), dtype=int)

    for i in range(1,nbEtu+1):
        ligne = contenu[i].split()
        id_etu = int(ligne[0])

        for rang, j in enumerate(ligne[2:]):
            id_parcours = int(j)
            matrice[id_etu][rang] = id_parcours
            classement[id_etu][id_parcours] = rang
            
    return matrice, classement


def lecture_PrefSpe(file):
    """Lit PrefSpe.txt et retourne une matrice contenant le classement des étudiants selon les préférences des parcours"""
    fic = open(file, "r", encoding="utf-8-sig")
    contenu = fic.readlines()
    fic.close()

    contenu[0]=contenu[0].split()
    nbEtu = int(contenu[0][1])
    nbParcours = 10

    contenu[1]=contenu[1].split()
    capacites = [int(c) for c in contenu[1][1:]]

    matrice = np.zeros((nbParcours, nbEtu), dtype=int)
    classement = np.zeros((nbParcours, nbEtu), dtype=int)

    for i in range(2,nbParcours+2):
        ligne = contenu[i].split()
        id_parcours = int(ligne[0])

        for rang, j in enumerate(ligne[2:]):
            id_etu = int(j)
            matrice[id_parcours][rang] = id_etu
            classement[id_parcours][id_etu] = rang

    return capacites, matrice, classement


def gale_shapley_cote_etudiant(PrefEtu, PrefSpe, classement, capacites):
    nb_etu = PrefEtu.shape[0]
    nb_parcours = PrefSpe.shape[0]

    # 1. TROUVER UN ÉTUDIANT LIBRE : File (FIFO, deque) pour extraire en O(1)
    etu_libres = deque(range(nb_etu))

    # 2. PROCHAIN PARCOURS AUQUEL FAIRE UNE PROPOSITION : Tableau pour avancer en O(1) dans les préférences sans détruire PrefEtu
    prochain_voeu = [0] * nb_etu

    # Les affectations utiliseront des "Tas" (Heaps) pour chaque parcours
    AFFECTATIONS = {i: [] for i in range(nb_parcours)}

    while len(etu_libres) != 0:
        etu = etu_libres.popleft()

        if prochain_voeu[etu] >= len(PrefEtu[etu]):
            #print(f"L'étudiant {etu} n'a pas pu être affecté (plus de voeux).")
            continue

        next_parcours = PrefEtu[etu][prochain_voeu[etu]]
        prochain_voeu[etu] += 1

        # 3. POSITION DE L'ÉTUDIANT DANS UN PARCOURS : O(1)
        rang_etu = classement[next_parcours][etu]

        # En insérant un rang négatif, le pire rang (plus grand nombre) sera toujours le plus "petit", donc placé à la racine du tas !
        candidat = (-rang_etu, etu)

        if len(AFFECTATIONS[next_parcours]) < capacites[next_parcours]:
            # S'il reste de la place, ajout dans le tas en O(logC)
            heapq.heappush(AFFECTATIONS[next_parcours], candidat)
            #print(f"l'étudiant {etu} est affecté à {next_parcours} ")
        else:
            # 4. TROUVER LE PIRE ÉTUDIANT : O(1) car il est toujours à l'index 0 du tas
            pire_rang_negatif, pire_etu = AFFECTATIONS[next_parcours][0]
            pire_rang = -pire_rang_negatif  # On remet en positif pour comparer
            if rang_etu < pire_rang:
                # 5. REMPLACER : Le nouveau est meilleur !
                # Ajoute le nouveau et éjecte le pire en une seule passe O(log C)
                _, etu_ejecte = heapq.heappushpop(AFFECTATIONS[next_parcours], candidat)

                # L'étudiant éjecté redevient libre
                etu_libres.append(etu_ejecte)
                #print(f"{next_parcours} accepte la proposition de l'étudiant {etu}")

            else:
                etu_libres.append(etu)
                #print(f"{next_parcours} rejette la proposition de l'étudiant {etu}")

    # Nettoyage final : on retire les scores négatifs renvoyer un dictionnaire propre
    affectations_propres = {}
    for parcours, tas in AFFECTATIONS.items():
        affectations_propres[parcours] = [etu_id for _, etu_id in tas]

    return affectations_propres


def gale_shapley_cote_parcours(PrefEtu, PrefSpe, classement_etu, capacites):
    """Applique l'algorithme de Gale-Shapley côté parcours (les masters proposent)"""
    nb_etu = len(PrefEtu)
    nb_parcours = len(PrefSpe)

    # 1. File des parcours qui ont encore des places libres à proposer
    parcours_libres = deque(range(nb_parcours))

    # Pointeur sur le prochain étudiant à qui le parcours va faire une offre
    prochain_voeu = [0] * nb_parcours
    
    # Nombre d'étudiants actuellement affectés à chaque parcours
    places_prises = [0] * nb_parcours

    # État des étudiants : quel est leur parcours actuel (-1 si aucun)
    affectation_etu = [-1] * nb_etu

    while len(parcours_libres) != 0:
        parcours = parcours_libres.popleft()

        # Si le parcours a fait une offre à TOUS les étudiants de sa liste, il abandonne
        if prochain_voeu[parcours] >= len(PrefSpe[parcours]):
            continue

        # L'étudiant à qui le master va proposer
        etu = PrefSpe[parcours][prochain_voeu[parcours]]
        prochain_voeu[parcours] += 1

        # Cas A : L'étudiant est libre
        if affectation_etu[etu] == -1:
            affectation_etu[etu] = parcours
            places_prises[parcours] += 1
        
        # Cas B : L'étudiant a déjà un parcours, il va comparer
        else:
            parcours_actuel = affectation_etu[etu]
            
            # On utilise le classement pré-calculé des étudiants pour comparer en O(1)
            # Attention : Plus le rang est petit (proche de 0), meilleur est le choix !
            rang_nouveau = classement_etu[etu][parcours]
            rang_actuel = classement_etu[etu][parcours_actuel]

            if rang_nouveau < rang_actuel:
                # L'étudiant accepte le nouveau master et rejette l'ancien (comme Amy avec Xavier et Zach)
                affectation_etu[etu] = parcours
                places_prises[parcours] += 1
                
                # L'ancien master perd un étudiant, libère une place et retourne faire la queue !
                places_prises[parcours_actuel] -= 1
                if places_prises[parcours_actuel] == capacites[parcours_actuel] - 1:
                    parcours_libres.append(parcours_actuel)
            else:
                # L'étudiant refuse, le parcours actuel a essuyé un refus
                pass 

        # Si le parcours n'est pas encore plein après cette démarche, il retourne dans la file
        if places_prises[parcours] < capacites[parcours]:
            parcours_libres.append(parcours)

    # Reformater la sortie pour que ton code de vérification (Q6) fonctionne correctement
    # On veut un dictionnaire : { id_master : [liste_id_etudiants] }
    affectations_propres = {i: [] for i in range(nb_parcours)}
    for etu, master in enumerate(affectation_etu):
        if master != -1:
            affectations_propres[master].append(etu)

    return affectations_propres



def liste_paires_instables(PrefEtu, classement, capacites, affectations):
    """Renvoie la liste des paires instabes de l'affectation"""
    nb_etu = len(PrefEtu)
    paires_instables = []

    # Dictionnaire pour trouver le master auquel chaque étudiant est affecté
    master_etu = dict()
    for master, liste_etus in affectations.items():
        for etu in liste_etus:
            master_etu[etu] = master

    #Vérifier pour chaque étudiant
    for etu in range(nb_etu):
        master_actuel = master_etu[etu]
        for master_prefere in PrefEtu[etu]:
            # On arrête la boucle parceque les masters en dessous sont moins préférés
            if master_prefere == master_actuel:
                break

            etus_du_master = affectations[master_prefere]

            # Si le master a encore de la place libre, on a une paire instable
            if len(etus_du_master) < capacites[master_prefere]:
                paires_instables.append((etu, master_prefere))
            
            # Si le master préfère l'étudiant actuel à son pire étudiant, paire instable
            else:
                pire_etu = max(etus_du_master, key = lambda e:classement[master_prefere][e])
                if classement[master_prefere][etu] < classement[master_prefere][pire_etu]:
                    paires_instables.append((etu, master_prefere))
            
    return paires_instables


def matrice_utilites(MatricePref):
    """Renvoie la matrice des utilités en utilisant les scores de Borda"""
    n = len(MatricePref)
    m = len(MatricePref[0])
    matrice = np.zeros((n, m), dtype=int)
    for i in range(n):
        for j in range(m):
            l = MatricePref[i][j]
            matrice[i][l] = m - j -1
    return matrice

def matrice_utilites_totale(PrefEtu, PrefSpe):
    U_etu = matrice_utilites(PrefEtu)
    U_spe = matrice_utilites(PrefSpe)
    return U_etu + U_spe.T
