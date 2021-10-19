# README 
# This script is to explore the questrade transaction file 

from numpy import true_divide
import pandas as pd 

filePath = "F:/workbench/Transaction Analysis/venv/Activities_for_01Sep2021_to_18Oct2021.xlsx"
tickerArray = ['ANY', 'BA', 'CLWR']

print("")
print("loading file: " + filePath)
print("")

transactionsDF = pd.read_excel(filePath, 'Activities')

print("File loaded successfully!!")
print("")

#cleanup the dataframe
dropColumns = ['Activity Type', 'Settlement Date', 'Account Type', 'Account #', 'Gross Amount', 'Description']

transactionsDF.drop(columns = dropColumns, inplace=True)

# find P&L from ANY and BA trades 
print("Transaction with:")
print(tickerArray)
print("")

print(transactionsDF.loc[transactionsDF['Symbol'].isin(tickerArray)])

print("")
print("Trade P&L")
print("")

print(transactionsDF.loc[transactionsDF['Symbol'].isin(tickerArray)].groupby('Symbol')['Net Amount'].sum())