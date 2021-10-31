# README 
# This script is to explore the questrade transaction file 

# DONE for the closed positions, find ( net amount / sum of all buys * 100 ) i.e. the P&L % 
# DONE plot the distribution of P&L 
# DONE print closed positions into an excel sheet
# DONE print trading returns over last 30 days 
# TODO plot closedposition returns over time
# TODO find if there is correlation between P&L and transaction date 
from os import rename
import numpy as np
from numpy.core.arrayprint import printoptions
from numpy.core.records import record
import pandas as pd 
import matplotlib.pyplot as plt
import openpyxl
import datetime as dt
import warnings

from numpy import true_divide, where

#   Tickers to search transactions for
tickerArray = ['JAGGF', 'HOD.TO', 'TQNT', 'AMOT']

# path to relevant excel files:
# transactions, investmentsummary
filePath_transactions = "F:/workbench/Transaction Analysis/venv/Activities.xlsx"
filepath_investmentSummary = "F:/workbench/Transaction Analysis/venv/InvestmentSummary.xlsx"

# path to output  closed positions excel file
filePath_printClosedPositions = 'F:/workbench/Transaction Analysis/venv/closedPositions.xlsx'

print("")
print("")
print("##################################################")
print("##################################################")
print("##################################################")
print("")
print("loading file: " + filePath_transactions)
print("")

with warnings.catch_warnings(record = True):
    warnings.simplefilter("always")
    transactionsDF = pd.read_excel(filePath_transactions, 'Activities')

print(">> File loaded successfully!!")
print("")
print("loading file: " + filepath_investmentSummary)
print("")

with warnings.catch_warnings(record = True):
    warnings.simplefilter("always")
    balancesDF = pd.read_excel(filepath_investmentSummary, 'Balances')
    positionsDF = pd.read_excel(filepath_investmentSummary, 'Positions')


print(">> File loaded successfully!!")
print("")
print("cleaning up the data...")
print("")
###
#cleanup the dataframe
###

# drop unwanted columns
dropColumns = ['Activity Type', 'Settlement Date', 'Account Type', 'Account #', 'Gross Amount','Commission', 'Currency']
transactionsDF.drop(columns = dropColumns, inplace=True)

# Convert the Transaction Date column 
# into a useable datetime object
transactionsDF['Transaction Date'] = pd.to_datetime(transactionsDF['Transaction Date'])
transactionsDF.rename(columns={'Transaction Date' : 'First Transaction'}, inplace=True)

print(">> Data cleaned up successfully!!")
print("")
print(">> last recorded transaction:", transactionsDF['First Transaction'].max())
print("")
print("##################################################")
print("##################################################")
print("##################################################")
print("___________________________________________________")
print("")

#####
# util function 
##
# returns df with columns: Symbol, sum of Quantity, 
# sum of Net Amount, and the date of the first transaction
#####
def getClosedPositions():
    
    sumOfAllSymbols = ( transactionsDF
    .loc[ (transactionsDF['Action'] == 'Buy') | (transactionsDF['Action'] == 'Sell') ]
    .groupby ('Symbol', as_index=False)
    .agg( { 
        'First Transaction' : min,   #first transaction
        'Quantity' : sum,           # sell's are '-' in the data
        'Net Amount' : sum },      
        axis = 1)
    .reset_index(drop = True)
    .set_index('Symbol')
    .sort_values(by=['First Transaction'])
    )
    
    sumBuysOfAllSymbols = ( transactionsDF
    .loc[ (transactionsDF['Action'] == 'Buy') ]
    .groupby ('Symbol', as_index=False)
    .agg( {
        'Net Amount': sum
    })
    )
    sumBuysOfAllSymbols.rename(columns={'Net Amount': 'Position Cost'}, inplace=True)

    sumOfAllSymbols = pd.merge(sumOfAllSymbols, sumBuysOfAllSymbols, how='left', on='Symbol')

    # Return the Symbols that have no open positions 
    #print(sumBuysOfAllSymbols)
    return sumOfAllSymbols.loc[sumOfAllSymbols['Quantity'] == 0]

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
    print("###################################################")
    print("###################################################")
    print("###################################################")
    print("")
    print("            Closed Positions Statistics")
    print("")
    print("")

    #Group closed returns by year
    closedPositions_annual = closedPositions.groupby(closedPositions['First Transaction'].map(lambda x: x.year)).sum(['Net Amount'])
    
    # print closed positions
    print(closedPositions_annual)
    print("")
    
    # print the net P/L from ALL closed positions  
    print(">> Net of all closed positions: <<") 
    print(closedPositions['Net Amount'].sum())
    print("")
    print("")
    print("")
    print("###################################################")
    print("###################################################")
    print("###################################################")
    print("___________________________________________________")

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

######
# print trading return over the last user specified # of days 
# along with the associated transactions, and period returns
######
def findTradingReturn(targetPeriod):
    print(">> Finding Trading Returns over {0} day period".format( targetPeriod))
    print("")
    #set the beginning date 
    beginningDate = dt.datetime.now() - pd.DateOffset(days = targetPeriod)

    closedPositions = getClosedPositions()
    #filter by date < 30 days old
    closedInTargetPeriod = closedPositions.loc[closedPositions['First Transaction'] > beginningDate].copy() 

    closedInTargetPeriod.loc[:,'Net Return %'] = closedInTargetPeriod['Net Amount']/closedInTargetPeriod['Position Cost'] * -100

    print(closedInTargetPeriod)
    print('')
    print('Sum of closed positions over this period:', closedInTargetPeriod['Net Amount'].sum())
    #print('Avg Return per Trade:', closedInTargetPeriod['Net Return %'].mean())
    print('')
    print('')

#####
# print out interesting overall portfolio stats
# Stats: Total Contributions, Overall Return 
def findPortfolioStats():
    
    print("###################################################")
    print("###################################################")
    print("###################################################")
    print("")
    print("            Select Portfolio Statistics!!")
    print("")
    print("")
    
    # calculate % return on total contributions to-date
    totalEquity = balancesDF['Total Equity in CAD Combined'].sum()
    totalContributions = (
        transactionsDF.loc[transactionsDF['Action'] == 'CON']
        .agg( {
            'Net Amount' : sum
        })
    )
    
    returnOnContribution = (totalEquity - totalContributions[0]) / totalContributions[0] * 100

    #TODO '%' formatting on output
    print('Return on Contribution(%):', returnOnContribution )
    print('           Total Holdings:', positionsDF['Equity Symbol'].count())
    print('                 Open P&L:', positionsDF['Profit And Loss'].sum())

    print("")
    print("")
    print("                 END portfolio stats")
    print("###################################################")
    print("###################################################")
    print("###################################################")
    print("")
    print("")
#####
#END
#####


#findTransactionPandLByTicker(tickerArray)

#findPandLOfClosedPositions()

#histogram_closedPositionsPandL()

#printToExecl_ClosedPositionsPandL()

findTradingReturn(60)

#findPortfolioStats()
