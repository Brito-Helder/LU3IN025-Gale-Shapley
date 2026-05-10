from fonctions import *
from solveur import *

if __name__ == "__main__":
    # 1. Lecture des fichiers de préférences
    PrefEtu, classement_etu = lecture_PrefEtu("PrefEtu.txt")
    capacites, PrefSpe, classement_spe = lecture_PrefSpe("PrefSpe.txt")

    print("=== ALGORITHME DE GALE-SHAPLEY (COTE ETUDIANTS) ===")
    # 2. GS côté étudiants 
    affectations_etu, _ = gale_shapley_cote_etudiant(PrefEtu, PrefSpe, classement_spe, capacites)
    calculer_metrics_GS(affectations_etu, PrefEtu, PrefSpe)
    for master, liste_etus in affectations_etu.items():
        print(f"Master {master} ({len(liste_etus)}/{capacites[master]} places) : Etudiants {liste_etus}")

    instables_etu = liste_paires_instables(PrefEtu, classement_spe, capacites, affectations_etu)
    print(f"-> Nombre de paires instables : {len(instables_etu)}\n")


    print("=== ALGORITHME DE GALE-SHAPLEY (COTE PARCOURS) ===")
    # 3. GS côté parcours
    affectations_parcours, _ = gale_shapley_cote_parcours(PrefEtu, PrefSpe, classement_etu, capacites)
    calculer_metrics_GS(affectations_parcours, PrefEtu, PrefSpe)
    for master, liste_etus in affectations_parcours.items():
        print(f"Master {master} ({len(liste_etus)}/{capacites[master]} places) : Etudiants {liste_etus}")

    instables_parcours = liste_paires_instables(PrefEtu, classement_spe, capacites, affectations_parcours)
    print(f"-> Nombre de paires instables : {len(instables_parcours)}\n") 
    
    
    print("=== ALGORITHME PLNE UTILITARISTE ===")
    # 4. PLNE maximisant l'utilité totale
    affectations_parcours = PLNE_UTILITARISTE(PrefEtu, PrefSpe, capacites)
    for master, liste_etus in affectations_parcours.items():
        print(f"Master {master} ({len(liste_etus)}/{capacites[master]} places) : Etudiants {liste_etus}")

    instables_parcours = liste_paires_instables(PrefEtu, classement_spe, capacites, affectations_parcours)
    print(f"-> Nombre de paires instables : {len(instables_parcours)}\n") 
    
    
    print("=== ALGORITHME PLNE EQUITABLE ===")
    # 5. PLNE maximisant l'équité (utilité minimale)
    affectations_parcours = PLNE_EQUITABLE(PrefEtu, PrefSpe, capacites)
    for master, liste_etus in affectations_parcours.items():
        print(f"Master {master} ({len(liste_etus)}/{capacites[master]} places) : Etudiants {liste_etus}")

    instables_parcours = liste_paires_instables(PrefEtu, classement_spe, capacites, affectations_parcours)
    print(f"-> Nombre de paires instables : {len(instables_parcours)}\n") 
    
    
    print("=== ALGORITHME PLNE MARIAGE PARFAIT TOP-K ===")
    # 6. PLNE maximisant l'équité (utilité minimale)
    k_min, affectations_parcours = PLNE_PARFAIT_top_k(PrefEtu, PrefSpe, capacites)
    for master, liste_etus in affectations_parcours.items():
        print(f"Master {master} ({len(liste_etus)}/{capacites[master]} places) : Etudiants {liste_etus}")

    instables_parcours = liste_paires_instables(PrefEtu, classement_spe, capacites, affectations_parcours)
    print(f"-> Nombre de paires instables : {len(instables_parcours)}\n") 