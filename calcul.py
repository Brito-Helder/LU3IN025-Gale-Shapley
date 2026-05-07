import time
import matplotlib.pyplot as plt
from fonctions import *

nb_parcours = 9

def generer_matrice_prefEtu(n):
    PrefEtu = np.zeros((n, nb_parcours), dtype=int)
    for i in range(n):
        PrefEtu[i] = np.random.permutation(nb_parcours)
    return PrefEtu


def generer_matrice_prefSpe(n):
    PrefSpe = np.zeros((nb_parcours, n), dtype=int)
    for i in range(nb_parcours):
        PrefSpe[i] = np.random.permutation(n)
    classement = np.argsort(PrefSpe, axis=1)
    return PrefSpe, classement


def generer_capacites_deterministes(n):
    base = n // nb_parcours
    reste = n % nb_parcours
    # On initialise la liste avec la base pour tout le monde
    capacites = [base] * nb_parcours
    # On ajoute 1 place aux premiers parcours jusqu'à épuiser le reste
    for i in range(reste):
        capacites[i] += 1
    return capacites


def tracer_courbe():
    nb_tests = 10
    temps_moyens = []
    valeurs_n = list(range(200, 2201, 200))
    for n in valeurs_n:
        print(f"tracer_courbe: {n}")
        capacites = generer_capacites_deterministes(n)
        temps_total = 0.0
        for test in range(nb_tests):
            # Chargement des données de test
            PrefEtu = generer_matrice_prefEtu(n)
            PrefSpe, classement = generer_matrice_prefSpe(n)

            # Mesure du temps de calcul
            debut = time.perf_counter()
            affectations = gale_shapley(PrefEtu, PrefSpe, classement, capacites)
            fin = time.perf_counter()

            temps_total += (fin - debut)

        temps_moyen = temps_total / nb_tests
        temps_moyens.append(temps_moyen)

    # Tracé de la courbe
    plt.figure()
    plt.plot(valeurs_n, temps_moyens, marker='o')

    plt.title("Temps de calcul de Gale-Shapley en fonction du nombre n d'étudiants (n)")
    plt.xlabel("Nombre d'étudiants (n)")
    plt.ylabel("Temps moyen d'exécution (secondes)")
    plt.grid(True)

    # Affiche le graphique à l'écran
    plt.show()
    plt.savefig("temps_moyens.png")