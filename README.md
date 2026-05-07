# LU3IN025 : Intelligence Artificielle et Jeux - Algorithme de Gale-Shapley

Ce projet a été réalisé dans le cadre de l'UE **LU3IN025** à **Sorbonne Université**. Il porte sur la résolution d'un problème d'affectation des étudiants dans les différents parcours du Master Informatique en utilisant des algorithmes d'appariement stable et de l'optimisation mathématique.

## Contexte du Projet
L'objectif est d'automatiser et d'optimiser l'affectation de $n$ étudiants vers $m=10$ parcours de master spécialisés :
* **IA2D, BIM, CCA, IMA, MIND, QI, RES, SAR, SESI, STL**.

Le système s'appuie sur les vœux exprimés par les étudiants et les classements établis par les responsables de parcours.

## Fonctionnalités Principales

### 1. Algorithme de Gale-Shapley
Implémentation complète en **Python** de l'algorithme de Gale-Shapley adapté au problème des hôpitaux (plusieurs places par parcours) :
* **Version "Côté Étudiants"** : Favorise les préférences des étudiants.
* **Version "Côté Parcours"** : Favorise les préférences des masters.
* **Vérification de stabilité** : Algorithme de détection des paires instables pour valider les résultats.

### 2. Optimisation et Performance
* **Structures de données optimisées** : Utilisation de structures spécifiques pour garantir des opérations rapides (recherche d'étudiants libres, mise à jour des affectations).
* **Analyse de complexité** : Étude théorique et expérimentale de la complexité des algorithmes.
* **Tests de montée en charge** : Mesure des temps de calcul sur des populations allant de 200 à 2000 étudiants avec génération de courbes de performance.

### 3. Équité et Optimisation (PLNE)
Au-delà de la stabilité, le projet explore l'équité via la Programmation Linéaire en Nombres Entiers (PLNE) avec le solveur **Gurobi** :
* **Maximisation de l'utilité minimale** (Équité brute).
* **Maximisation de la somme des utilités** (Efficacité globale) via les scores de Borda.
* **Compromis entre choix et utilité** : Recherche du meilleur rang $k$ pour garantir un mariage parfait.
