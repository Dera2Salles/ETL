Projet : Pipeline ETL & Dashboard de Comptes Clients 
Objectf général 
Metre en place un processus ETL complet (Extracton – Transformaton – Loading) à partr de 
fchiers Excel, puis produire un dashboard (PDF, ou Excel, ou Tableau, lookerstudio) 
présentant diférents indicateurs sur les comptes clients de la microfnance. 
Les étudiants doivent : 
1.  Lire les données sources (Excel) 
2.  Transformer les données pour les rendre exploitables 
3.  Charger les données fnales dans un Data Warehouse (SQLLite, PostgreSQL, ou 
autre…) 
4.  Construire un dashboard inspiré de dashboardCompte.PNG 
5.  Proposer éventuellement des indicateurs ou graphiques supplémentaires 
 
1. Descripton des données 
Les données se trouvent dans un fchier Excel ( dataset_account.xlsx) contenant notamment : 
Feuille 1 : data source   
Colonnes disponibles : 
•  Code : Identfant client 
•  noCompte : Numéro de compte 
•  AvailableBalance : Solde disponible du client 
•  OpeningDate : Date d’ouverture du compte 
•  AccountStatus : Statut du compte (utliser uniquement les comptes "Actf") 
•  Report_date_to : Date de situaton du compte 
•  Gestonnaire : Gestonnaire de compte 
 
Compositon du numéro de compte 
Le champ noCompte est structuré comme suit : 
Segment Signifcaton  Exemple 
00115  Code banque  00115 
00001  Code agence  00001 
9…  Produit (1er digit) + numéro de compte 
9000031
6601 
39  Clé RIB  39 
Exemple complet : 00115 00001 90000316601 39 (9 : code produit ;  00001 : code agence) 
 
Feuille 2 : Product Mapping 
Content la correspondance entre : 
•  Code produit (ex : 9) 
•  Nom du produit (ex : “Dépôt à Terme”) 
 
Feuille 3 : Branch Mapping 
Content la correspondance entre : 
•  Code agence (ex : 00001) 
•  Nom de l’agence (ex : “Champagne-Ardenne”) 
 
. Travail demandé (Pipeline ETL) 
Étape 1 – Extracton 
Importer les données depuis : 
•  la feuille data source 
•  la feuille Product Mapping 
•  la feuille Branch Mapping 
 
Étape 2 – Transformatons 
Appliquer les opératons suivantes : 
1.  Décomposer le numéro de compte (noCompte) 
o  Extraire : 
▪  Code banque 
▪  Code agence 
▪  Code produit (1er digit de la 3e secton) 
▪  Numéro de compte proprement dit 
o  Rapprocher les codes avec : 
▪  Mapping des produits  
▪  Mapping des agences 
➔  Ici vous avez 2 optons : 
o  Faire les « join » dans l’ETL (plus rapide côté rendu vers le 
dashboard).  
Join avec panda dataframe: 
In: Df_merged = d.merge (df_left, df_right, on=”ici_le_PK_de_jointure”, how=’left’)  
#how -> (left, right, inner, outer) # **mais attention!) 
o  Faire les “join “ dans le Data warehouse (plus souples pour les 
rajouts ou modifcaton de nom d’agence, ou utlisaton par 
d’autre « fact ») ** 
** Souvenez-vous : la bonne pratque pour metre en place les tables dans les data 
warehouse c’est d’avoir des tables des dimensions (Agence, produit, gestonnaire etc….) et 
des tables des faits (exemple : les situatons de chaque compte à date avec les clés primaires 
des dimensions) 
2.  Filtrer uniquement les comptes actfs 
Garder seulement AccountStatus = "Actf". 
3.  Formatage des dates, montants, etc. 
4.  Créaton d’un dataset fnal 
Harmonisé, enrichi, prêt pour la visualisaton et agrégaton. 
 
Étape 3 – Agrégaton 
Préparer les indicateurs nécessaires au dashboard, par exemple : 
•  Répartton des comptes par agence 
•  Solde total disponible par agence 
•  Solde moyen par produit 
•  Top N gestonnaires par solde total 
•  Total de comptes actfs  
Ou tous autres indicateurs que vous jugez import 
 
Étape 4 – Chargement 
Charger les données fnales dans un Data Warehouse : 
•  SQL Server 
•  PostgreSQL 
•  MySQL 
•  SQLite 
•  ou autre base relatonnelle  
L’objectf ici c’est de représenter un Data warehouse et non d’en avoir un vraie (donc à vous 
d’en choisir) 
Assurez-vous de fournir l’accès à la base 
(connecton string / privilèges). 
 
3. Dashboard à produire 
Créer un dashboard inspiré du fchier dashboardCompte.PNG. 
Vous pouvez utliser : 
•  Power BI 
•  Tableau 
•  Metabase 
•  Grafana 
•  Dash / Streamlit 
•  ou un autre outl BI de votre choix (même MS Excel) 
Le dashboard doit présenter : 
•  Au moins 3 indicateurs clés 
•  Au moins 4 graphiques 
Liberté accordée : 
•  Vous n’êtes pas obligés de reproduire exactement les mêmes graphiques. 
•  Vous pouvez ajouter des visuels que vous jugez pertnents. 
•  Design et lisibilité comptent plus que la technologie ou plateforme choisie. 
 
4. Livrables 
Chaque étudiant doit fournir : 
1.  Code ETL (Python, SQL) 
2.  Schéma du pipeline ETL 
3.  Dashboard fnal 
4.  Courte documentaton expliquant : 
o  Le pipeline ETL 
o  Les transformatons choisies 
o  Les indicateurs du dashboard 
Format des livrables : à envoyer par mail à razaonja@gmail.com en respectant les points ci-
après 
•  Nom de fchier : ASJA -L3_ETL_PROJECT-MatriculeXXXX-2025_2026.zip 
•  Object du mail : ASJA -L3 ETL PROJECT MatriculeXXXX 2025-2026 
Ex :  
•  Filename : ASJA-L2-ETL_PROJECT-Matricule5984-2025_20263.zip 
•  Mail Object : ASJA -L3 ETL PROJECT Matricule5984 2025-2026 
 
 
Objectf pédagogique 
À la fn du projet, les compétences que vous devriez acquérir sont: 
•  Lire et transformer un dataset réel 
•  Manipuler des Jointures 
•  Concevoir un pipeline ETL complet 
•  Documenter un processus analytque 
•  Produire un dashboard professionnel 
 
 
 
 
