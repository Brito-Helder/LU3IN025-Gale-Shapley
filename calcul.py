import time
import os
import matplotlib.pyplot as plt
from fonctions import *

nb_parcours = 9

def generer_matrice_prefEtu(n):
    PrefEtu = np.zeros((n, nb_parcours), dtype=int)
    for i in range(n):
        PrefEtu[i] = np.random.permutation(nb_parcours)
    classement_etu = np.argsort(PrefEtu, axis=1)
    return PrefEtu, classement_etu


def generer_matrice_prefSpe(n):
    PrefSpe = np.zeros((nb_parcours, n), dtype=int)
    for i in range(nb_parcours):
        PrefSpe[i] = np.random.permutation(n)
    classement_parcours = np.argsort(PrefSpe, axis=1)
    return PrefSpe, classement_parcours


def generer_capacites_deterministes(n):
    base = n // nb_parcours
    reste = n % nb_parcours
    # On initialise la liste avec la base pour tout le monde
    capacites = [base] * nb_parcours
    # On ajoute 1 place aux premiers parcours jusqu'à épuiser le reste
    for i in range(reste):
        capacites[i] += 1
    return capacites


def tracer_courbe(type): 
    if type != "cote_etudiant" and type != "cote_parcours":
        print("Type de courbe inconnu. Veuillez choisir 'cote_etudiant' ou 'cote_parcours'.")
        return
    
    nb_tests = 20
    temps_moyens = []
    valeurs_n = list(range(200, 2201, 200))
    for n in valeurs_n:
        print(f"tracer_courbe: {n}")
        capacites = generer_capacites_deterministes(n)
        temps_total = 0.0
        for test in range(nb_tests):
            # Chargement des données de test
            PrefEtu, classement_etu = generer_matrice_prefEtu(n)
            PrefSpe, classement_parcours = generer_matrice_prefSpe(n)

            # Mesure du temps de calcul
            debut = time.perf_counter()
            if type == "cote_etudiant":
                gale_shapley_cote_etudiant(PrefEtu, PrefSpe, classement_parcours, capacites)
            else:   
                gale_shapley_cote_parcours(PrefEtu, PrefSpe, classement_etu, capacites)
            fin = time.perf_counter()

            temps_total += (fin - debut)

        temps_moyen = temps_total / nb_tests
        temps_moyens.append(temps_moyen)

    # Tracé de la courbe
    plt.figure()
    plt.plot(valeurs_n, temps_moyens, marker='o')

    plt.title(f"Temps de calcul de Gale_Shapley_{type} en fonction du nombre n d'étudiants (n)")
    plt.xlabel("Nombre d'étudiants (n)")
    plt.ylabel("Temps moyen d'exécution (secondes)")
    plt.grid(True)
    
    if not os.path.exists("Graphiques"):
        os.makedirs("Graphiques")

    plt.savefig(os.path.join("Graphiques", f"temps_moyens_{type}.png"))

    
    # Affiche le graphique à l'écran
    plt.show()
    
def tracer_courbe_iterations(type): 
    if type != "cote_etudiant" and type != "cote_parcours":
        print("Type de courbe inconnu. Veuillez choisir 'cote_etudiant' ou 'cote_parcours'.")
        return
    
    nb_tests = 50
    iterations_moyennes = []
    valeurs_n = list(range(200, 2201, 200))
    for n in valeurs_n:
        print(f"tracer_courbe: {n}")
        capacites = generer_capacites_deterministes(n)
        iterations_total = 0 
        for test in range(nb_tests):
            # Chargement des données de test
            PrefEtu, classement_etu = generer_matrice_prefEtu(n)
            PrefSpe, classement_parcours = generer_matrice_prefSpe(n)

            # Mesure du temps de calcul
            if type == "cote_etudiant":
                _, iterations = gale_shapley_cote_etudiant(PrefEtu, PrefSpe, classement_parcours, capacites)
            else:   
                _, iterations = gale_shapley_cote_parcours(PrefEtu, PrefSpe, classement_etu, capacites)
            iterations_total += iterations

        mean_iterations = iterations_total / nb_tests
        iterations_moyennes.append(mean_iterations)

    # Tracé de la courbe
    plt.figure()
    plt.plot(valeurs_n, iterations_moyennes, marker='o')

    plt.title(f"Nombre d'itérations de Gale_Shapley_{type} en fonction du nombre n d'étudiants (n)")
    plt.xlabel("Nombre d'étudiants (n)")
    plt.ylabel("Nombre moyen d'itérations")
    plt.grid(True)
    if not os.path.exists("Graphiques"):
        os.makedirs("Graphiques")

    plt.savefig(os.path.join("Graphiques", f"iterations_moyennes_{type}.png"))
    
    # Affiche le graphique à l'écran
    plt.show()
    
if __name__ == "__main__":
    tracer_courbe("cote_etudiant")
    tracer_courbe("cote_parcours")
    tracer_courbe("test")
    
    #tracer_courbe_iterations("cote_etudiant")
    #tracer_courbe_iterations("cote_parcours")
    #tracer_courbe_iterations("test")
    
