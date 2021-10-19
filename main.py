# README 
# This script is to explore the questrade transaction file 

from numpy import true_divide, where
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
#print("Transaction with:")
#print(tickerArray)
print("")

#print(transactionsDF.loc[transactionsDF['Symbol'].isin(tickerArray)])

print("")
#print("Trade P&L")
print("")

#print(
# transactionsDF.loc[transactionsDF['Symbol']
# .isin(tickerArray)]
# .groupby('Symbol')['Net Amount']
# .sum()
# )

#TODO find all symbols with net 0 holdings (i.e. no longer has open position), and figure out their P&L 

# For the SYMBOLS where SUM OF QUANTITY = 0 over all trasactions

# create a df with symbol, sum of quantity, and sum of net amount
sumQuantityOfAllSymbols = ( transactionsDF.groupby('Symbol')['Quantity', 'Net Amount']
.sum()
)

# Select the Symbols that have no open positions 
closedPositions = sumQuantityOfAllSymbols.loc[sumQuantityOfAllSymbols['Quantity'] == 0]

#TODO for the closed positions, find ( net amount / sum of all buys * 100 ) 

#print(sumQuantityOfAllSymbols.sort_values('Net Amount', ascending='true').head(15))

# print closed positions
print(closedPositions.sort_values('Net Amount', ascending=False).head(15))

print("")
print("###########")
print("")

# print the net P/L from ALL closed positions  
print(closedPositions['Net Amount'].sum())


#first col is symbol, second is sumof(quantity)
# print the SUM OF ( NET AMOUNT )
# print min(transaction date) and max(transaction date)