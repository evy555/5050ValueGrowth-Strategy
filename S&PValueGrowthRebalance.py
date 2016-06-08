import numpy as np
import os
import pandas as pd 
import pandas.io.data
from pandas import Series, DataFrame
from pandas import ExcelWriter
from pandas import read_csv
import matplotlib.pyplot as plt
import datetime
from scipy.stats import ttest_1samp
import matplotlib.pyplot as plt
from random import randint
import math 
test = 10
results = []
while test > 0:

    ### Establish Time and Get Stock Returns 
    now = datetime.datetime.now()  
    list = ['IVE', 'IVW', 'SPY']
    start = datetime.datetime(randint(2000,2015),randint(1,12),randint(1,28))
    print(start) 
    end = datetime.datetime(now.year,now.month,now.day)
    df = pd.io.data.get_data_yahoo(list, start, end)['Adj Close']
    df = DataFrame(df)
    df['IVEReturn'] = df['IVE'].pct_change()
    df['IVWReturn'] = df['IVW'].pct_change()
    df['SP500Return'] = df['SPY'].pct_change() 
    df['Date'] = df.index
    df['Date'] = [time.date() for time in df['Date']] 
    l = df.index.values
    for i in range(0,len(l)):
        df.loc[l[i], 'Year'] = datetime.datetime.strptime(str(df.loc[l[i], 'Date']), '%Y-%m-%d').strftime('%Y')    

    ### Create Investment Test
    ### Set DataFrame Variables 
    df['InvestmentTotal'] = ''
    df['Growth'] = ''
    df['Value'] = ''
    df['InvestmentTotal'][0] = 100000
    df['Growth'] = df['InvestmentTotal'][0]/2
    df['Value'] = df['InvestmentTotal'][0]/2
    df['SP500Total'] = ''
    df['SP500Total'][0] = 100000
    ### Rebalance Decision Rule Loop 
    for i in range(1,len(l)): 
        if df.loc[l[i], 'Year'] != df.loc[l[i-1], 'Year']:
            df.loc[l[i-1], 'Rebalance'] = 'Yes'
        else:
            df.loc[l[i-1], 'Rebalance'] = 'No' 

            
    ### Investment Returns Loop
    for i in range(1, len(l)):
        df.loc[l[i], 'Growth'] = df.loc[l[i-1], 'Growth'] * (1 + df.loc[l[i], 'IVWReturn']) 
        df.loc[l[i], 'Value'] = df.loc[l[i-1], 'Value'] * (1 + df.loc[l[i], 'IVEReturn'])
        df.loc[l[i], 'InvestmentTotal'] = df.loc[l[i], 'Value'] + df.loc[l[i], 'Growth'] 
        
        df.loc[l[i], 'SP500Total'] = df.loc[l[i-1], 'SP500Total'] * (1 + df.loc[l[i], 'SP500Return']) 
        
        ### Growth vs Value allocation 
        df.loc[l[i], 'Growth%'] = df.loc[l[i],'Growth']/df.loc[l[i],'InvestmentTotal']
        df.loc[l[i], 'Value%'] = df.loc[l[i],'Value']/df.loc[l[i], 'InvestmentTotal']
        df.loc[l[i], 'Total%'] = df.loc[l[i], 'Growth%'] + df.loc[l[i], 'Value%']
        
        
        ### Execute Rebalance 
        if df.loc[l[i-1], 'Rebalance'] == 'Yes':
            if df.loc[l[i-1], 'Growth%'] > .5:
                trade_value = .5 * (df.loc[l[i-1], 'Growth'] - df.loc[l[i-1], 'Value'])  
                df.loc[l[i], 'Value'] = (df.loc[l[i-1], 'Value'] + trade_value) * (1 + df.loc[l[i], 'IVEReturn'])
                df.loc[l[i], 'Growth'] = (df.loc[l[i-1], 'Growth'] - trade_value) * (1 + df.loc[l[i], 'IVWReturn']) 
                df.loc[l[i], 'InvestmentTotal'] = df.loc[l[i], 'Value'] + df.loc[l[i], 'Growth'] 
                df.loc[l[i], 'Growth%'] = df.loc[l[i],'Growth']/df.loc[l[i],'InvestmentTotal']
                df.loc[l[i], 'Value%'] = df.loc[l[i],'Value']/df.loc[l[i], 'InvestmentTotal']
                df.loc[l[i], 'Total%'] = df.loc[l[i], 'Growth%'] + df.loc[l[i], 'Value%']
            else:
                trade_value = .5 * (df.loc[l[i-1], 'Value'] - df.loc[l[i-1], 'Growth'])
                df.loc[l[i], 'Growth'] = (df.loc[l[i-1], 'Growth'] + trade_value) * (1 + df.loc[l[i], 'IVWReturn'])
                df.loc[l[i], 'Value'] = (df.loc[l[i-1], 'Value'] - trade_value) * (1 + df.loc[l[i], 'IVEReturn'])
                df.loc[l[i], 'InvestmentTotal'] = df.loc[l[i], 'Value'] + df.loc[l[i], 'Growth'] 
                df.loc[l[i], 'Growth%'] = df.loc[l[i],'Growth']/df.loc[l[i],'InvestmentTotal']
                df.loc[l[i], 'Value%'] = df.loc[l[i],'Value']/df.loc[l[i], 'InvestmentTotal']
                df.loc[l[i], 'Total%'] = df.loc[l[i], 'Growth%'] + df.loc[l[i], 'Value%']

    final_value = df.loc[l[len(l)-1], 'InvestmentTotal'] - df.loc[l[len(l)-1],'SP500Total']
    if math.isnan(final_value) == True:
        print("result removed it was nan")
        test = test + 1 
    else:
        results.append(final_value)
    print(results)
    test = test - 1 

dg = pd.Series(results, name = 'Results')
dff = DataFrame(dg)
print(dff) 
dff.hist()
plt.show() 
file = ExcelWriter('ValueGrowth.xlsx')
df.to_excel(file, 'Data')
file.close()
os.startfile('ValueGrowth.xlsx')

df.plot(y = ['SP500Total', 'InvestmentTotal'])
plt.show()   


