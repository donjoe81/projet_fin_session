# Telco — Dashboard statistique des départs clients

Projet du cours INF-5103 — Concepts statistiques pour la science des données.

## Objectif et utilisateur

L’application s’adresse à un responsable de la fidélisation d’un
opérateur télécom. Elle permet d’explorer les départs observés,
de comparer des groupes et d’examiner deux modèles de classification.

Il s’agit d’un prototype pédagogique utilisant des données fictives.

## Fonctionnalités

- Indicateurs : effectif, départs, proportion de départs et ancienneté médiane.
- Filtre par type de contrat.
- Intervalles de confiance de Wilson à 95 %.
- Comparaison des départs par contrat.
- Répartition des anciennetés selon le départ observé.
- Exploration des variables et tests d’association.
- Régression logistique et réseau de neurones à deux couches cachées (8 et 4 neurones).
- Comparaison des deux modèles à une référence constante.
- Comparaison et sélection des seuils sur la validation sous contrainte de contact.
- Mesures de performance et matrices de confusion pour chaque modèle, sur validation et test.

## Installation sous WSL / Linux

La configuration a été vérifiée avec Python 3.14.
Les versions des dépendances sont enregistrées dans `requirements.txt`.

```bash
git clone https://github.com/donjoe81/projet_fin_session.git
cd projet_fin_session
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
python -m pip install -r requirements.txt
```

## Lancement

Une fois l’installation terminée et l’environnement activé :

```bash
python run.py
```

Ouvrir ensuite : http://127.0.0.1:5000

## Pages principales

| Adresse | Contenu |
|---|---|
| `/` | Dashboard et filtres |
| `/analyse_exploratoire` | Exploration des variables |
| `/correlation_vars` | Tests d’association |
| `/validation` | Évaluation des deux modèles et choix des seuils sur la validation |
| `/comparaison` | Même présentation de la comparaison sur la validation |
| `/test-final` | Évaluation des deux modèles aux seuils choisis sur la validation |

Les pages des modèles utilisent des groupes fixes, indépendants du filtre
par contrat du dashboard. Le premier affichage entraîne les modèles ;
les résultats sont ensuite conservés en mémoire. Redémarrer Flask après
une modification des données ou des paramètres.

## Données

Fichier utilisé :

`dataset/WA_Fn-UseC_-Telco-Customer-Churn.csv`

Le fichier contient 7 043 clients et 21 colonnes, dont la cible `Churn`.

Source de référence IBM :
https://github.com/IBM/telco-customer-churn-on-icp4d

Les données représentent une entreprise fictive. Elles ne constituent
pas un échantillon validé de la clientèle d’un opérateur réel.

### Préparation

- Le CSV original est conservé.
- `TotalCharges` est converti en numérique.
- Ses 11 valeurs non numériques deviennent manquantes.
- Les clients concernés restent dans les données.
- `SeniorCitizen` est traité comme une catégorie.
- `customerID` est exclu des tests d’association.
- Aucun identifiant client dupliqué n’a été détecté.

## Méthodes statistiques

- Statistique descriptive : effectifs, proportions, moyenne et médiane.
- Comparaisons de proportions conditionnelles au contrat.
- Intervalles de confiance de Wilson sous hypothèse binomiale
  et indépendance des observations.
- Tests d’association avec correction des comparaisons multiples.
- Régression logistique et réseau de neurones (perceptron multicouche).

Les couleurs du dashboard utilisent des repères de démonstration :
moins de 10 %, de 10 % à moins de 30 %, puis 30 % et plus.
Ces seuils ne sont pas des normes du secteur.

## Modèles et protocole d’évaluation

Variables communes aux deux modèles :

- `tenure` : ancienneté ;
- `MonthlyCharges` : montant mensuel ;
- `Contract` : type de contrat.

Cible : `Churn`, avec 1 pour un départ et 0 sinon.

Séparation stratifiée reproductible, avec la graine 5103 :

- entraînement : 4 225 clients ;
- validation : 1 409 clients ;
- test : 1 409 clients.

L’imputation, la standardisation et l’encodage sont ajustés uniquement
sur l’entraînement.

Le contrat est encodé en deux indicatrices : les modèles reçoivent donc
quatre entrées après transformation.

- Régression logistique : régularisation par défaut, maximum de 1 000 itérations.
- Réseau : couches cachées de 8 puis 4 neurones, activation ReLU, sortie
  sigmoïde, optimiseur Adam et arrêt anticipé. Il réserve 15 % du groupe
  d’entraînement à une validation interne pour cet arrêt.

Aucune pondération des classes ni aucun suréchantillonnage n’est appliqué.
La référence prédit l’absence de départ pour tous les clients. Sa précision
est indéfinie puisqu’elle ne produit aucune alerte.

Les pages affichent l’exactitude, la précision, le rappel, le F1 et l’aire
ROC, au seuil commun de 0,50 et aux seuils retenus sur la validation.

### Choix du seuil

Hypothèse pédagogique : contacter au maximum 35 % des clients
de validation.

Pour 1 409 clients, le plafond est de 493 contacts (arrondi à l’entier inférieur).
Pour chaque modèle, la règle compare les seuils 0,20 ; 0,35 ; 0,50 ; 0,65 ;
0,80 et maximise le rappel sans dépasser le plafond. En cas d’égalité,
elle privilégie la précision, puis le seuil le plus élevé.
Les deux modèles retiennent ici 0,35. Ce seuil de score est distinct
de la capacité de contact de 35 %.

### Résultats sur la validation aux seuils retenus

| Mesure | Régression logistique | Réseau 8–4 |
|---|---:|---:|
| Seuil | 0,35 | 0,35 |
| Exactitude | 75,2 % | 75,7 % |
| Précision | 52,5 % | 53,3 % |
| Rappel | 69,0 % | 66,6 % |
| F1 | 0,597 | 0,592 |
| Aire ROC | 0,829 | 0,835 |
| Alertes | 491 | 467 |
| Départs détectés | 258 | 249 |
| Fausses alertes | 233 | 218 |
| Départs manqués | 116 | 125 |

### Résultats sur le test aux seuils de validation

La régression a d’abord été évaluée sur le test réservé. Le réseau a été
ajouté après consultation de ces résultats : la comparaison actuelle est
complémentaire et ne constitue pas une nouvelle évaluation indépendante.
Les seuils proviennent de la validation et ne sont pas réajustés sur le test.

| Mesure | Régression logistique | Réseau 8–4 |
|---|---:|---:|
| Seuil | 0,35 | 0,35 |
| Exactitude | 75,9 % | 77,1 % |
| Précision | 53,7 % | 55,6 % |
| Rappel | 68,7 % | 67,6 % |
| F1 | 0,603 | 0,610 |
| Aire ROC | 0,835 | 0,840 |
| Alertes sur 1 409 clients | 479 | 455 |
| Part des clients signalés | 34,0 % | 32,3 % |

Matrices de confusion : les lignes indiquent l’observation réelle et les
colonnes la prédiction. Les deux modèles respectent ici le plafond de
493 contacts, avec des nombres de contacts différents.

**Régression logistique**

| Observation / Prédiction | Absence de départ | Départ |
|---|---:|---:|
| Absence de départ | 813 | 222 |
| Départ | 117 | 257 |

**Réseau de neurones**

| Observation / Prédiction | Absence de départ | Départ |
|---|---:|---:|
| Absence de départ | 833 | 202 |
| Départ | 121 | 253 |

## Limites

- Les données sont fictives.
- Les associations observées ne démontrent pas des relations causales.
- Les scores des modèles ne sont pas des certitudes individuelles.
- Une seule séparation des données et une seule initialisation par architecture
  du réseau ont été examinées ; la stabilité des résultats n’est pas mesurée.
- Un seuil fixe ne garantit pas le respect du quota sur un nouveau groupe.
- Détecter un départ ne démontre pas qu’un contact commercial l’éviterait.
- Toute modification motivée par les résultats du test nécessiterait
  de nouvelles données indépendantes pour une nouvelle évaluation finale.

## Vérifications réalisées

- Installation des dépendances dans un environnement virtuel séparé.
- Réponse HTTP 200 des neuf pages et sélections vérifiées.
- Réponse HTTP 400 pour un contrat inconnu.
- Concordance des effectifs des tranches d’ancienneté avec les indicateurs.
- Contrôle des totaux des matrices et du nombre d’alertes pour les deux modèles.
- Concordance des résultats avec les tableaux du rapport.
- Vérification visuelle du dashboard et des graphiques.

Les contrôles HTTP ne constituent pas un audit exhaustif des méthodes
statistiques ni de l’interface.

## Utilisation de l’intelligence artificielle

ChatGPT / Codex a été utilisé pour proposer et corriger du code,
aider au débogage, expliquer des méthodes et proposer des éléments
d’interface et de documentation.

L’annexe du rapport présente la déclaration d’utilisation de l’IA.
Elle doit refléter l’aide effectivement reçue au cours du projet.