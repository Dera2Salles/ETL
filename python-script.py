import pandas

dataFrame = pandas.read_excel("./dataset_account.xlsx", engine="openpyxl")
dataFrameProduct = pandas.read_excel(
    "./dataset_account.xlsx", sheet_name="product mapping", engine="openpyxl"
)  # lis une feuille dans l'excel
dataFrameBranch = pandas.read_excel(
    "./dataset_account.xlsx", sheet_name="branch mapping", engine="openpyxl"
)  # lis une feuille dans l'excel

dataFrame["BankCode"] = dataFrame["noCompte"].str[0:5]
dataFrame["BranchCode"] = dataFrame["noCompte"].str[5:10]
dataFrame["ProductCode"] = dataFrame["noCompte"].str[12]
dataFrame["AccountNumber"] = dataFrame["noCompte"].str[11:21]

dataFrameMerged = dataFrame.merge(dataFrameProduct, on="ProductCode", how="left")
dataFrameMerged = dataFrame.merge(dataFrameBranch, on="BranchCode", how="left")
dataFrameMerged = dataFrameMerged[dataFrameMerged["AccountStatus"] == "Actif"]

dataFrameMerged["OpeningDate"] = pandas.to_datetime(dataFrameMerged["OpeningDate"])
dataFrameMerged["Report_date_to"] = pandas.to_datetime(dataFrameMerged["Report_date_to"])
dataFrameMerged["AvailableBalance"] = pandas.to_numeric(dataFrameMerged["AvailableBalance"])

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
    columns={"Nom du produit": "ProductName", "Nom de l'agence": "BranchName"}
)

accounts_by_branch = (
    dataFrameMerged.groupby("Nom de l'agence").size().reset_index(name="AccountCount")
)
total_balance_by_branch = (
    dataFrameMerged.groupby("Nom de l'agence")["AvailableBalance"]
    .sum()
    .reset_index(name="TotalAvailableBalance")
)
average_balance_by_product = (
    dataFrameMerged.groupby("Nom du produit")["AvailableBalance"]
    .mean()
    .reset_index(name="AverageAvailableBalance")
)
total_active_accounts = dataFrameMerged.shape[0]

# conn = sqlite3.connect("etl_project.db")
# dataFrameMerged.to_sql("accounts_data", conn, if_exists="replace", index=False)
# conn.close()
