# README 
# This script is to explore the questrade transaction file 

# DONE for the closed positions, find ( net amount / sum of all buys * 100 ) i.e. the P&L % 
# DONE plot the distribution of P&L 
# DONE print closed positions into an excel sheet
# TODO plot closedposition returns over time
# TODO find if there is correlation between P&L and transaction date 
from os import rename
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import openpyxl

from numpy import true_divide, where


filePath = "F:/workbench/Transaction Analysis/venv/Activities_for_01Sep2021_to_18Oct2021.xlsx"

filePath_printClosedPositions = 'F:/workbench/Transaction Analysis/venv/closedPositions.xlsx'

tickerArray = ['JAGGF', 'HOD.TO', 'TQNT', 'AMOT']

print("")
print("loading file: " + filePath)
print("")

transactionsDF = pd.read_excel(filePath, 'Activities')

print("File loaded successfully!!")
print("")

#cleanup the dataframe
dropColumns = ['Activity Type', 'Settlement Date', 'Account Type', 'Account #', 'Gross Amount','Commission', 'Currency']

transactionsDF.drop(columns = dropColumns, inplace=True)
#####
# util function 
##
# returns df with columns: Symbol, sum of Quantity, 
# sum of Net Amount, and the date of the first transaction
#####
def getClosedPositions():
    # create a df with symbol, sum of quantity, and sum of net amount
    
    #sumQuantityOfAllSymbols = ( transactionsDF.groupby#('Symbol')
    #.sum([['Quantity', 'Net Amount']])
    #)

    sumQuantityOfAllSymbols = ( transactionsDF.groupby ('Symbol', as_index=False)
    .agg( { 
        'Transaction Date' : min,   #first transaction
        'Quantity' : sum,           # sell's are '-' in the data
        'Net Amount' : sum },      
        axis = 1)
    .reset_index(drop = True)
    .set_index('Symbol')
    )
    
    # Return the Symbols that have no open positions 
    return sumQuantityOfAllSymbols.loc[sumQuantityOfAllSymbols['Quantity'] == 0]

#####
# find the transaction history and 
# net trading P&L for the passed in tickerArray
##### 
def findTransactionPandLByTicker(myTickerArray):

    # find P&L from ANY and BA trades 
    print("Transaction with:")
    print(tickerArray)
    print("")
    print("Transaction History...")

    print(transactionsDF.loc[transactionsDF['Symbol'].isin(tickerArray)])

    print("")
    print("Trade P&L")
    print("")

    print(
        transactionsDF.loc[transactionsDF['Symbol']
        .isin(tickerArray)]
        .groupby('Symbol')['Net Amount']
        .sum()
    )
    print("")

#####
# Find all symbols with net 0 holdings 
# (i.e. no longer has open position), 
# and figure out their P&L 
######
def findPandLOfClosedPositions():
    # Select the Symbols that have no open positions 
    closedPositions = getClosedPositions()

    # print closed positions
    print(closedPositions.sort_values('Net Amount', ascending=False).head(15))

    print("")
    print("###########")
    print("")

    # print the net P/L from ALL closed positions  
    print("Net of all closed positions:") 
    print(closedPositions['Net Amount'].sum())

#####
# plot a histogram of closed position returns 
#####
def histogram_closedPositionsPandL():
    print('Graphing!!')

    # Select the Symbols that have no open positions 
    closedPositions = getClosedPositions()

    closedPositions['Net Amount'].plot.hist(bins=30, alpha=0.5)
    plt.show()


######
# print closed positions into an excel 
######

def printToExecl_ClosedPositionsPandL():
    
    print("printing to excel file: " + filePath_printClosedPositions)

    closedPositions = getClosedPositions()

    with pd.ExcelWriter(filePath_printClosedPositions, engine='openpyxl') as writer: 
        closedPositions.to_excel(writer, sheet_name='Closed Positions', header=True, index=True)

    print("Printing to excel completed!")

#####
#END
#####


#findTransactionPandLByTicker(tickerArray)

#findPandLOfClosedPositions()

#histogram_closedPositionsPandL()

#print(getClosedPositions().head())

#printToExecl_ClosedPositionsPandL()

