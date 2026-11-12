# Telco — Dashboard statistique des départs clients

Projet du cours INF-5103 — Concepts statistiques pour la science des données.

## Objectif et utilisateur

L’application s’adresse à un responsable de la fidélisation d’un
opérateur télécom. Elle permet d’explorer les départs observés,
de comparer des groupes et d’examiner un modèle de classification.

Il s’agit d’un prototype pédagogique utilisant des données fictives.

## Fonctionnalités

- Indicateurs : effectif, départs, proportion de départs et ancienneté médiane.
- Filtre par type de contrat.
- Intervalles de confiance de Wilson à 95 %.
- Comparaison des départs par contrat.
- Répartition des anciennetés selon le départ observé.
- Exploration des variables et tests d’association.
- Régression logistique comparée à une référence constante.
- Comparaison des seuils sur la validation.
- Évaluation finale sur un groupe de test réservé.

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
| `/validation` | Comparaison avec la référence et sélection du seuil |
| `/test-final` | Résultats de l’évaluation finale |

Le profilage automatique est optionnel. Si sa dépendance n’est pas
installée, sa page affiche un message d’indisponibilité.

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
- Régression logistique.

Les couleurs du dashboard utilisent des repères de démonstration :
moins de 10 %, de 10 % à moins de 30 %, puis 30 % et plus.
Ces seuils ne sont pas des normes du secteur.

## Modèle et protocole d’évaluation

Variables du modèle :

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

La référence prédit l’absence de départ pour tous les clients.

### Choix du seuil

Hypothèse pédagogique : contacter au maximum 35 % des clients
de validation.

Parmi les seuils 0,20 ; 0,35 ; 0,50 ; 0,65 ; 0,80, la règle maximise
le rappel sous cette contrainte. Elle retient le seuil 0,35.

Le modèle et ce seuil ont été fixés avant l’évaluation finale.

### Résultats du test au seuil 0,35

| Mesure | Valeur |
|---|---:|
| Exactitude | 75,9 % |
| Précision | 53,7 % |
| Rappel | 68,7 % |
| F1 | 0,603 |
| Aire ROC | 0,835 |
| Alertes | 479 sur 1 409 |
| Part des clients signalés | 34,0 % |

Matrice de confusion :

| Observation / Prédiction | Absence de départ | Départ |
|---|---:|---:|
| Absence de départ | 813 | 222 |
| Départ | 117 | 257 |

## Limites

- Les données sont fictives.
- Les associations observées ne démontrent pas des relations causales.
- Les scores du modèle ne sont pas des certitudes individuelles.
- Un seuil fixe ne garantit pas le respect du quota sur un nouveau groupe.
- Détecter un départ ne démontre pas qu’un contact commercial l’éviterait.
- Toute modification motivée par les résultats du test nécessiterait
  de nouvelles données indépendantes pour une nouvelle évaluation finale.

## Vérifications réalisées

- Installation des dépendances dans un environnement virtuel séparé.
- Réponse HTTP 200 des huit pages et sélections vérifiées.
- Réponse HTTP 400 pour un contrat inconnu.
- Concordance des effectifs des tranches d’ancienneté avec les indicateurs.
- Vérification visuelle du dashboard et des graphiques.

Les contrôles HTTP ne constituent pas un audit exhaustif des méthodes
statistiques ni de l’interface.

## Utilisation de l’intelligence artificielle

ChatGPT / Codex a été utilisé pour proposer et corriger du code,
aider au débogage, expliquer des méthodes et proposer des éléments
d’interface et de documentation.

L’équipe doit compléter la déclaration du rapport pour refléter
l’utilisation effective de ces outils et vérifier les éléments retenus.