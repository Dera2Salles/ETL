import sqlite3
import pandas as pd

# Étape 1 - Extraction
dataFrame = pd.read_excel("./dataset_account.xlsx", engine="openpyxl")
dataFrameProduct = pd.read_excel(
    "./dataset_account.xlsx", sheet_name="product mapping", engine="openpyxl"
)
dataFrameBranch = pd.read_excel(
    "./dataset_account.xlsx", sheet_name="branch mapping", engine="openpyxl"
)

dataFrame["BankCode"] = dataFrame["noCompte"].astype(str).str[0:5]
dataFrame["BranchCode"] = dataFrame["noCompte"].astype(str).str[6:11]
dataFrame["ProductCode"] = dataFrame["noCompte"].astype(str).str[12]
dataFrame["AccountNumber"] = dataFrame["noCompte"].astype(str).str[11:19]


dataFrameBranch['CodeBranch'] = dataFrameBranch['CodeBranch'].astype(str)
dataFrame['BranchCode'] = dataFrame['BranchCode'].astype(str)

## TODO : convertir CodeBranch  satria mbola int fa tsy string 0012

dataFrameMerged = pd.merge(
    dataFrame, 
    dataFrameProduct, 
    left_on="ProductCode", 
    right_on="productCode", 
    how="left"
)

dataFrameMerged = pd.merge(
    dataFrameMerged, 
    dataFrameBranch, 
    left_on="BranchCode", 
    right_on="CodeBranch", 
    how="left"
)
# 2. Filtrer uniquement les comptes actifs
dataFrameMerged = dataFrameMerged[dataFrameMerged["AccountStatus"] == "Actif"]

# 3. Formatage des dates, montants, etc.
dataFrameMerged["OpeningDate"] = pd.to_datetime(dataFrameMerged["OpeningDate"])
dataFrameMerged["Report_date_to"] = pd.to_datetime(dataFrameMerged["Report_date_to"])
dataFrameMerged["AvailableBalance"] = pd.to_numeric(dataFrameMerged["AvailableBalance"])

# 4. Création du dataset final harmonisé
final_dataset = dataFrameMerged[
    [
        "Code",
        "AccountNumber",
        "AvailableBalance",
        "OpeningDate",
        "AccountStatus",
        "Report_date_to",
        "Gestionnaire",
        "BankCode",
        "BranchCode",
        "ProductCode",
        "Nom du produit",
        "Nom de l'agence",
    ]
]
final_dataset = final_dataset.rename(
    columns={"Nom du produit": "ProductName", "Nom de l'agence": "BranchName", "Code": "ClientCode"}
)

# Étape 3 - Agrégation
# Répartition des comptes par agence
accounts_by_branch = final_dataset.groupby("BranchName").size().reset_index(name="AccountCount")

# Solde total disponible par agence
total_balance_by_branch = (
    final_dataset.groupby("BranchName")["AvailableBalance"]
    .sum()
    .reset_index(name="TotalAvailableBalance")
)

# Solde moyen par produit
average_balance_by_product = (
    final_dataset.groupby("ProductName")["AvailableBalance"]
    .mean()
    .reset_index(name="AverageAvailableBalance")
)

# Top 5 gestionnaires par solde total
top_gestionnaires = (
    final_dataset.groupby("Gestionnaire")["AvailableBalance"]
    .sum()
    .nlargest(5)
    .reset_index(name="TotalBalance")
)

# Total de comptes actifs
total_active_accounts = final_dataset.shape[0]

# Solde total de tous les comptes
total_balance_all_accounts = final_dataset["AvailableBalance"].sum()

# Nombre de clients uniques
unique_clients = final_dataset["ClientCode"].nunique()

# Étape 4 - Chargement dans Data Warehouse (SQLite)
conn = sqlite3.connect("etl_project.db")

# Création des tables dimensionnelles
# Table dimension Produit
product_dim = dataFrameProduct.copy()
product_dim.columns = ["ProductCode", "ProductName"]
product_dim.to_sql("dim_product", conn, if_exists="replace", index=False)

# Table dimension Agence
branch_dim = dataFrameBranch.copy()
branch_dim.columns = ["BranchCode", "BranchName"]
branch_dim.to_sql("dim_branch", conn, if_exists="replace", index=False)

# Table dimension Client (simplifiée)
client_dim = final_dataset[["ClientCode", "Gestionnaire"]].drop_duplicates()
client_dim.to_sql("dim_client", conn, if_exists="replace", index=False)

# Table des faits (Fact table)
fact_accounts = final_dataset[
    [
        "ClientCode",
        "AccountNumber",
        "AvailableBalance",
        "OpeningDate",
        "AccountStatus",
        "Report_date_to",
        "BankCode",
        "BranchCode",
        "ProductCode",
    ]
]
fact_accounts.to_sql("fact_accounts", conn, if_exists="replace", index=False)

# Table des agrégats pour le dashboard
accounts_by_branch.to_sql("agg_accounts_by_branch", conn, if_exists="replace", index=False)
total_balance_by_branch.to_sql("agg_balance_by_branch", conn, if_exists="replace", index=False)
average_balance_by_product.to_sql(
    "agg_avg_balance_by_product", conn, if_exists="replace", index=False
)
top_gestionnaires.to_sql("agg_top_gestionnaires", conn, if_exists="replace", index=False)

# Création d'une table pour les KPI globaux
kpi_data = pd.DataFrame(
    {
        "KPI": ["Total comptes actifs", "Solde total", "Clients uniques"],
        "Valeur": [total_active_accounts, total_balance_all_accounts, unique_clients],
    }
)
kpi_data.to_sql("kpi_globaux", conn, if_exists="replace", index=False)

conn.close()
