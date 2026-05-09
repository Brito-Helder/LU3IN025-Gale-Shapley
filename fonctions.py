import numpy as np
from collections import deque
import heapq
import gurobipy as gp
from gurobipy import GRB
import numpy as np


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
    nb_iterations = 0
    
    # 1. TROUVER UN ÉTUDIANT LIBRE : File (FIFO, deque) pour extraire en O(1)
    etu_libres = deque(range(nb_etu))

    # 2. PROCHAIN PARCOURS AUQUEL FAIRE UNE PROPOSITION : Tableau pour avancer en O(1) dans les préférences sans détruire PrefEtu
    prochain_voeu = [0] * nb_etu

    # Les affectations utiliseront des "Tas" (Heaps) pour chaque parcours
    AFFECTATIONS = {i: [] for i in range(nb_parcours)}

    while len(etu_libres) != 0:
        nb_iterations  += 1
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
                # 5. REMPLACER : Le nouveau est meilleur
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

    return affectations_propres, nb_iterations  


def gale_shapley_cote_parcours(PrefEtu, PrefSpe, classement_etu, capacites):
    """Applique l'algorithme de Gale-Shapley côté parcours (les masters proposent)"""
    nb_etu = len(PrefEtu)
    nb_parcours = len(PrefSpe)
    nb_iterations = 0
    
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
        nb_iterations += 1

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

    return affectations_propres, nb_iterations


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


def calculer_metrics_GS(affectations, PrefEtu, PrefSpe):
    """Calcul l'utilité totale, l'utilité moyenne et l'utilité minimale parmi les étudiants pour une affectation donnée"""
    nb_etu = len(PrefEtu)
    nb_parcours = len(PrefSpe)
    x_gs = np.zeros((nb_etu, nb_parcours), dtype=int)
    for master, liste_etus in affectations.items():
        for etu in liste_etus:
            x_gs[etu][master] = 1
            
    U_etu = matrice_utilites(PrefEtu)
    U_spe = matrice_utilites(PrefSpe)
    U_totale = U_etu + U_spe.T
    
    utilite_totale = np.sum(x_gs * U_totale)
    u_moyenne = utilite_totale / (nb_etu * 2) # Moyenne par agent (Etu + Spe)
    utilites_individuelles = []
    for i in range(nb_etu):
        u_i = np.sum(x_gs[i, :] * U_etu[i, :])
        utilites_individuelles.append(u_i)
    u_min = min(utilites_individuelles)
    
    print(f"Utilite totale (Somme) : {utilite_totale}")
    print(f"Utilite moyenne par affectation : {u_moyenne:.2f}")
    print(f"Utilite minimale parmi les etudiants : {u_min}")
    return 
    
def PLNE_UTILITARISTE(PrefEtu, PrefSpe, capacites):
    """
    Résolution du PLNE maximisant l'utilité totale.
    Calcule également l'utilité moyenne et l'utilité minimale des étudiants.
    """
    nb_etu = len(PrefEtu)
    nb_parcours = len(PrefSpe)
    
    # 1. Préparation des données d'utilité 
    U_etu = matrice_utilites(PrefEtu)
    U_totale = matrice_utilites_totale(PrefEtu, PrefSpe)
    
    # 2. Création du modèle Gurobi
    m = gp.Model("Maximisation_Efficacite")
    m.setParam('OutputFlag', 0) # Masquer les logs techniques
    
    # Variables de décision x[i,j] ∈ {0,1} 
    x = m.addVars(nb_etu, nb_parcours, vtype=GRB.BINARY, name="x")
    
    # 3. Fonction Objectif : Maximiser la somme des utilités totales 
    m.setObjective(gp.quicksum(x[i,j] * U_totale[i,j] for i in range(nb_etu) for j in range(nb_parcours)), GRB.MAXIMIZE)
    
    # 4. Contraintes 
    #  1 étudiant = 1 master, respect des capacités
    m.addConstrs((gp.quicksum(x[i,j] for j in range(nb_parcours)) == 1 for i in range(nb_etu)), name="Affectation_Unique")
    m.addConstrs((gp.quicksum(x[i,j] for i in range(nb_etu)) <= capacites[j] for j in range(nb_parcours)), name="Capacite")
    
    # 5. Lance l'optimisation
    m.optimize()
    
    if m.status == GRB.OPTIMAL:
        # Récupération de l'affectation finale
        affectation = {j: [] for j in range(nb_parcours)}
        utilites_individuelles = []
        
        for i in range(nb_etu):
            for j in range(nb_parcours):
                if x[i,j].x > 0.5:
                    affectation[j].append(i)
                    # On stocke l'utilité de l'étudiant pour les stats
                    utilites_individuelles.append(U_etu[i,j])
        
        # Calcul de l'utilité totale, moyenne et minimale
        utilite_totale_groupe = m.objVal
        utilite_moyenne = utilite_totale_groupe / (nb_etu * 2) # Moyenne par agent (Etu + Spe)
        utilite_min_etu = min(utilites_individuelles)
        
        print(f"Utilite totale (Somme) : {utilite_totale_groupe}")
        print(f"Utilite moyenne par affectation : {utilite_moyenne:.2f}")
        print(f"Utilite minimale parmi les etudiants : {utilite_min_etu}")
        
        return affectation
    else:
        print("Erreur : Gurobi n'a pas trouvé de solution optimale.")
        return None
    
    
def PLNE_EQUITABLE(PrefEtu, PrefSpe, capacites):
    """
    Résolution du PLNE maximisant l'utilité totale.
    Calcule également l'utilité moyenne et l'utilité minimale des étudiants.
    """
    nb_etu = len(PrefEtu)
    nb_parcours = len(PrefSpe)
    
    # 1. Préparation des données d'utilité 
    U_etu = matrice_utilites(PrefEtu)
    U_totale = matrice_utilites_totale(PrefEtu, PrefSpe)
    
    # 2. Création du modèle Gurobi
    m = gp.Model("Maximisation_Equite")
    m.setParam('OutputFlag', 0) # Masquer les logs techniques
    
    # Variables de décision x[i,j] ∈ {0,1} 
    x = m.addVars(nb_etu, nb_parcours, vtype=GRB.BINARY, name="x")
    
    #Variable z qui représente l'utilité minimale parmi les étudiants
    z = m.addVar(vtype=GRB.INTEGER, name="z")
    
    # 3. Fonction Objectif : Maximiser z (l'utilité minimale parmi les étudiants)
    m.setObjective(z, GRB.MAXIMIZE)
    
    # 4. Contraintes 
    #  1 étudiant = 1 master, respect des capacités
    m.addConstrs((gp.quicksum(x[i,j] for j in range(nb_parcours)) == 1 for i in range(nb_etu)), name="Affectation_Unique")
    m.addConstrs((gp.quicksum(x[i,j] for i in range(nb_etu)) <= capacites[j] for j in range(nb_parcours)), name="Capacite")
    
    # z doit être inférieur ou égal à l'utilité obtenue par chaque étudiant i
    m.addConstrs((z <= gp.quicksum(x[i,j] * U_etu[i,j] for j in range(nb_parcours)) for i in range(nb_etu)), name="Contrainte_Min")
    
    # 5. Lance l'optimisation
    m.optimize()
    
    if m.status == GRB.OPTIMAL:
        affectation = {j: [] for j in range(nb_parcours)}
        utilite_somme_totale = 0
        
        for i in range(nb_etu):
            for j in range(nb_parcours):
                if x[i,j].x > 0.5:
                    affectation[j].append(i)
                    # On recalcule la somme totale pour pouvoir la comparer avec la Q12 !
                    utilite_somme_totale += U_totale[i,j]
        
        utilite_moyenne = utilite_somme_totale / (nb_etu * 2) # Moyenne par agent (Etu + Spe)
        print(f"Utilite totale globale (Somme) : {utilite_somme_totale}")
        print(f"Utilite moyenne par affectation : {utilite_moyenne:.2f}")
        print(f"Utilite minimale garantie aux etudiants (z) : {z.x}")
        
        return affectation
    else:
        print("Erreur : Gurobi n'a pas trouvé de solution.")
        return None
    
    
def PLNE_PARFAIT_top_k(PrefEtu, PrefSpe, capacites):
    """
    Trouve le plus petit k permettant une affectation parfaite 
    où chaque étudiant a au pire son k-ième choix, en maximisant l'utilité globale.
    """
    nb_etu = len(PrefEtu)
    nb_parcours = len(PrefSpe)
    
    U_etu = matrice_utilites(PrefEtu)
    U_totale = matrice_utilites_totale(PrefEtu, PrefSpe)
    
    # On teste les valeurs de k de 1 jusqu'à 10 (le nombre de masters)
    for k in range(1, nb_parcours + 1):
        
        m = gp.Model(f"Q14_Top_{k}")
        m.setParam('OutputFlag', 0)
        
        x = m.addVars(nb_etu, nb_parcours, vtype=GRB.BINARY, name="x")
        
        # Objectif : Maximiser l'utilité totale globale (Comme la Q12)
        m.setObjective(gp.quicksum(x[i,j] * U_totale[i,j] for i in range(nb_etu) for j in range(nb_parcours)), GRB.MAXIMIZE)
        
        # Contraintes classiques : 1 étudiant = 1 master, respect des capacités
        m.addConstrs((gp.quicksum(x[i,j] for j in range(nb_parcours)) == 1 for i in range(nb_etu)), name="Affectation_Unique")
        m.addConstrs((gp.quicksum(x[i,j] for i in range(nb_etu)) <= capacites[j] for j in range(nb_parcours)), name="Capacite")
        
        # L'utilité de chaque étudiant i doit être >= (10 - k)
        seuil_utilite = nb_parcours - k
        m.addConstrs((gp.quicksum(x[i,j] * U_etu[i,j] for j in range(nb_parcours)) >= seuil_utilite for i in range(nb_etu)), name="Top_k")
        
        # On lance la résolution pour ce k spécifique
        m.optimize()
        
        # Si Gurobi trouve une solution (OPTIMAL), c'est qu'on a trouvé notre k minimal !
        if m.status == GRB.OPTIMAL:
            print(f"Succes ! Le plus petit k possible est k = {k}")
            print(f"Cela signifie que personne n'a pire que son {k}eme voeu.")
            
            # Récupération de l'affectation
            affectation = {j: [] for j in range(nb_parcours)}
            utilites_individuelles = []
            for i in range(nb_etu):
                for j in range(nb_parcours):
                    if x[i,j].x > 0.5:
                        affectation[j].append(i)
                        utilites_individuelles.append(U_etu[i,j])
                        
            # Calcul de l'utilité totale, moyenne et minimale
            utilite_totale_groupe = m.objVal
            utilite_moyenne = utilite_totale_groupe / (nb_etu * 2) # Moyenne par agent (Etu + Spe)
            utilite_min_etu = min(utilites_individuelles)
            
            print(f"Utilite totale (Somme) : {utilite_totale_groupe}")
            print(f"Utilite moyenne par affectation : {utilite_moyenne:.2f}")
            print(f"Utilite minimale parmi les etudiants : {utilite_min_etu}")
            
            return k, affectation
            
    print("Aucune solution trouvée, même pour k max.")
    return None, None