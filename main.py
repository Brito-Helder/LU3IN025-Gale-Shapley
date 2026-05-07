from fonctions import *

PrefEtu = lecture_PrefEtu("PrefEtu.txt")
capacites, PrefSpe, classement = lecture_PrefSpe("PrefSpe.txt")
affectations = gale_shapley(PrefEtu, PrefSpe, classement, capacites)
print(PrefEtu)
print(score_borda(PrefEtu))
#print(PrefSpe)
print(affectations)
print(liste_paires_instables(PrefEtu, classement, capacites, affectations))

#tracer_courbe()