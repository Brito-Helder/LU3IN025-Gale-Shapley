from fonctions import *

if __name__ == "__main__":
    # 1. Lecture des fichiers de préférences
    PrefEtu, classement_etu = lecture_PrefEtu("PrefEtu.txt")
    capacites, PrefSpe, classement_spe = lecture_PrefSpe("PrefSpe.txt")

    print("=== ALGORITHME DE GALE-SHAPLEY (COTE ETUDIANTS) ===")
    # 2. Exécution côté étudiants 
    affectations_etu, _ = gale_shapley_cote_etudiant(PrefEtu, PrefSpe, classement_spe, capacites)
    for master, liste_etus in affectations_etu.items():
        print(f"Master {master} ({len(liste_etus)}/{capacites[master]} places) : Etudiants {liste_etus}")

    # 3. Vérification de la stabilité 
    instables_etu = liste_paires_instables(PrefEtu, classement_spe, capacites, affectations_etu)
    print(f"-> Nombre de paires instables : {len(instables_etu)}\n")


    print("=== ALGORITHME DE GALE-SHAPLEY (COTE PARCOURS) ===")
    # 4. Exécution côté parcours
    affectations_parcours, _ = gale_shapley_cote_parcours(PrefEtu, PrefSpe, classement_etu, capacites)
    for master, liste_etus in affectations_parcours.items():
        print(f"Master {master} ({len(liste_etus)}/{capacites[master]} places) : Etudiants {liste_etus}")

    # 5. Vérification de la stabilité 
    instables_parcours = liste_paires_instables(PrefEtu, classement_spe, capacites, affectations_parcours)
    print(f"-> Nombre de paires instables : {len(instables_parcours)}\n") 
