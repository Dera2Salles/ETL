import pandas 

dataFrame = pandas.read_excel('./dataset_account.xlsx' , engine='openpyxl')
dataFrameProduct = pandas.read_excel('./dataset_account.xlsx' , sheet_name='product mapping',engine='openpyxl') # lis une feuille dans l'excel
dataFrameBranch = pandas.read_excel('./dataset_account.xlsx' , sheet_name='product mapping',engine='openpyxl') # lis une feuille dans l'excel

dataFrame['BankCode'] = dataFrame['noCompte'].str[0:5]
dataFrame['BranchCode'] = dataFrame['noCompte'].str[5:10]
dataFrame['ProductCode'] = dataFrame['noCompte'].str[10]
dataFrame['AccountNumber'] = dataFrame['noCompte'].str[11:21]

dataFrameMerged = dataFrame.merge(dataFrameProduct, on='ProductCode', how='left')
dataFrameMerged = dataFrame.merge(dataFrameBranch, on='BranchCode', how='left')

dataFrameMerged
