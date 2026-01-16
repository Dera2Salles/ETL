
# Pipeline ETL

Le **Pipeline ETL** est développé en **Python** en utilisant :

* **Pandas** pour la manipulation et le traitement des données.
* **SQLAlchemy** pour l’interaction avec la base de données PostgreSQL.

---

## 1. Étapes du Pipeline ETL

### 1.1 Extract (Extraction)

Les données brutes sont extraites à partir d’un fichier Excel central (`dataset_account.xlsx`).
Trois feuilles distinctes sont chargées :

1. **Comptes**
2. **Mapping des produits**
3. **Mapping des agences**

---

### 1.2 Transform (Transformation)

Les données sont ensuite :

* **Nettoyées et typées** : grâce à des DataFrames Pandas.
* **Enrichies** : calcul des indicateurs clés via agrégation.

Les principales transformations appliquées sont :

#### a) Parsing du Numéro de Compte (`noCompte`)

Découpage de la chaîne pour extraire :

* **Code Banque** : positions 0-5
* **Code Agence** : positions 6-11
* **Code Produit** : position 12
* **Numéro de Compte pur** : reste de la chaîne

#### b) Normalisation des Codes Agence

Utilisation d’une fonction de formatage pour s’assurer que chaque **CodeBranch** possède toujours **5 caractères** (ajout de zéros en tête si nécessaire).
Cela garantit des jointures correctes avec la feuille de mapping.

#### c) Jointures (Merges)

Enrichissement de la table principale avec :

* **Nom complet des produits**
* **Nom complet des agences**

via des jointures **gauche (Left Join)** sur les codes correspondants.

#### d) Filtrage Métier

Seuls les comptes **actifs** sont conservés pour l’analyse, les comptes fermés ou inactifs sont exclus.

#### e) Calcul Temporel

* Conversion des colonnes `OpeningDate` et `Report_date_to` en **format Date**.
* Calcul de **l’ancienneté des comptes** en jours et en années (`AccountAgeYears`).

---

### 1.3 Load (Chargement)

Les données sont ensuite chargées dans une **base PostgreSQL locale** via SQLAlchemy :

* **Table principale** : données nettoyées.
* **Tables d’agrégation** : indicateurs clés (KPIs).

---

## 2. Indicateurs Clés (KPIs)

| Table SQL                 | Indicateur (KPI)          | Description / Utilité                                                                                  |
| ------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------ |
| `numberAccountsByBranch`  | Volume par Agence         | Nombre total de comptes ouverts par agence. Permet de mesurer l'activité commerciale locale.           |
| `totalBalanceByBranch`    | Encours par Agence        | Somme des `AvailableBalance` par agence. Identifie les agences les plus rentables en termes de dépôts. |
| `averageBalanceByProduct` | Solde Moyen par Produit   | Solde moyen disponible par type de produit. Aide à segmenter la clientèle.                             |
| `topGestionnaires`        | Performance Gestionnaires | Top 10 des gestionnaires cumulant le plus grand volume de fonds (Balance totale).                      |
| `averageAgeByBranch`      | Fidélité par Agence       | Ancienneté moyenne des comptes par agence. Indicateur de rétention client.                             |
| `data`                    | Données Brutes            | Table complète permettant des analyses détaillées (**drill-down**) dans le dashboard.                  |

---
