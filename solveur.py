import gurobipy as gp
from gurobipy import GRB
import numpy as np

def matrice_utilites(MatricePref):
    """Renvoie la matrice des utilités en utilisant les scores de Borda"""
    n = len(MatricePref)
    m = len(MatricePref[0])
    matrice = np.zeros((n, m), dtype=int)
    for i in range(n):
        for j in range(m):
            l = MatricePref[i][j]
            matrice[i][l] = m - j - 1
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
    u_moyenne = utilite_totale / (nb_etu * 2)  # Moyenne par agent (Etu + Spe)
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
    m.setParam('OutputFlag', 0)  # Masquer les logs techniques

    # Variables de décision x[i,j] ∈ {0,1}
    x = m.addVars(nb_etu, nb_parcours, vtype=GRB.BINARY, name="x")

    # 3. Fonction Objectif : Maximiser la somme des utilités totales
    m.setObjective(gp.quicksum(x[i, j] * U_totale[i, j] for i in range(nb_etu) for j in range(nb_parcours)),
                   GRB.MAXIMIZE)

    # 4. Contraintes
    #  1 étudiant = 1 master, respect des capacités
    m.addConstrs((gp.quicksum(x[i, j] for j in range(nb_parcours)) == 1 for i in range(nb_etu)),
                 name="Affectation_Unique")
    m.addConstrs((gp.quicksum(x[i, j] for i in range(nb_etu)) <= capacites[j] for j in range(nb_parcours)),
                 name="Capacite")

    # 5. Lance l'optimisation
    m.optimize()

    if m.status == GRB.OPTIMAL:
        # Récupération de l'affectation finale
        affectation = {j: [] for j in range(nb_parcours)}
        utilites_individuelles = []

        for i in range(nb_etu):
            for j in range(nb_parcours):
                if x[i, j].x > 0.5:
                    affectation[j].append(i)
                    # On stocke l'utilité de l'étudiant pour les stats
                    utilites_individuelles.append(U_etu[i, j])

        # Calcul de l'utilité totale, moyenne et minimale
        utilite_totale_groupe = m.objVal
        utilite_moyenne = utilite_totale_groupe / (nb_etu * 2)  # Moyenne par agent (Etu + Spe)
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
    m.setParam('OutputFlag', 0)  # Masquer les logs techniques

    # Variables de décision x[i,j] ∈ {0,1}
    x = m.addVars(nb_etu, nb_parcours, vtype=GRB.BINARY, name="x")

    # Variable z qui représente l'utilité minimale parmi les étudiants
    z = m.addVar(vtype=GRB.INTEGER, name="z")

    # 3. Fonction Objectif : Maximiser z (l'utilité minimale parmi les étudiants)
    m.setObjective(z, GRB.MAXIMIZE)

    # 4. Contraintes
    #  1 étudiant = 1 master, respect des capacités
    m.addConstrs((gp.quicksum(x[i, j] for j in range(nb_parcours)) == 1 for i in range(nb_etu)),
                 name="Affectation_Unique")
    m.addConstrs((gp.quicksum(x[i, j] for i in range(nb_etu)) <= capacites[j] for j in range(nb_parcours)),
                 name="Capacite")

    # z doit être inférieur ou égal à l'utilité obtenue par chaque étudiant i
    m.addConstrs((z <= gp.quicksum(x[i, j] * U_etu[i, j] for j in range(nb_parcours)) for i in range(nb_etu)),
                 name="Contrainte_Min")

    # 5. Lance l'optimisation
    m.optimize()

    if m.status == GRB.OPTIMAL:
        affectation = {j: [] for j in range(nb_parcours)}
        utilite_somme_totale = 0

        for i in range(nb_etu):
            for j in range(nb_parcours):
                if x[i, j].x > 0.5:
                    affectation[j].append(i)
                    # On recalcule la somme totale pour pouvoir la comparer avec la Q12 !
                    utilite_somme_totale += U_totale[i, j]

        utilite_moyenne = utilite_somme_totale / (nb_etu * 2)  # Moyenne par agent (Etu + Spe)
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
        m.setObjective(gp.quicksum(x[i, j] * U_totale[i, j] for i in range(nb_etu) for j in range(nb_parcours)),
                       GRB.MAXIMIZE)

        # Contraintes classiques : 1 étudiant = 1 master, respect des capacités
        m.addConstrs((gp.quicksum(x[i, j] for j in range(nb_parcours)) == 1 for i in range(nb_etu)),
                     name="Affectation_Unique")
        m.addConstrs((gp.quicksum(x[i, j] for i in range(nb_etu)) <= capacites[j] for j in range(nb_parcours)),
                     name="Capacite")

        # L'utilité de chaque étudiant i doit être >= (10 - k)
        seuil_utilite = nb_parcours - k
        m.addConstrs(
            (gp.quicksum(x[i, j] * U_etu[i, j] for j in range(nb_parcours)) >= seuil_utilite for i in range(nb_etu)),
            name="Top_k")

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
                    if x[i, j].x > 0.5:
                        affectation[j].append(i)
                        utilites_individuelles.append(U_etu[i, j])

            # Calcul de l'utilité totale, moyenne et minimale
            utilite_totale_groupe = m.objVal
            utilite_moyenne = utilite_totale_groupe / (nb_etu * 2)  # Moyenne par agent (Etu + Spe)
            utilite_min_etu = min(utilites_individuelles)

            print(f"Utilite totale (Somme) : {utilite_totale_groupe}")
            print(f"Utilite moyenne par affectation : {utilite_moyenne:.2f}")
            print(f"Utilite minimale parmi les etudiants : {utilite_min_etu}")

            return k, affectation

    print("Aucune solution trouvée, même pour k max.")
    return None, None