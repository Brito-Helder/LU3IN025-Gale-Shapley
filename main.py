from fonctions import *

PrefEtu = lecture_PrefEtu("PrefEtu.txt")
capacites, PrefSpe, classement = lecture_PrefSpe("PrefSpe.txt")
affectations = gale_shapley(PrefEtu, PrefSpe, classement, capacites)

print(affectations)
print(liste_paires_instables(PrefEtu, classement, capacites, affectations))

C = matrice_utilites_totale(PrefEtu, PrefSpe)

print(C)
#tracer_courbe()