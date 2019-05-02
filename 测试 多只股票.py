# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 21:29:12 2019

@author: Kris
"""
import os 
print(os.getcwd())
os.chdir('C:/Users/18036/Desktop/凯纳资本')

import numpy as np
import pandas as pd

raw = pd.read_excel('HS300 DATA.xlsx')
#去除空值行
raw = raw.drop(index=[1,3])
#设置列索引
raw.columns = np.arange(0,1199)

#重设列索引
raw.index = np.arange(486)

#获取所有股票标签
ticks = raw.iloc[0,:]
ticks = ticks[ticks.notna()]

#获取所有日期标签（因为最后一天没有开盘价，就不要）
date = raw.iloc[2:484,0]

#把所有open作为一组，所有close作为一组
#复制一个raw
raw1 = raw
#创建一个空dataframe

#获取开盘价
price = raw1.iloc[2:484,:]
open_range = np.arange(1,1198,4).astype(int)
#创建一个空dataframe
open_price = pd.DataFrame(columns=ticks)
for i in open_range:
    open_price[ticks[i]] = price.iloc[:,i]

#收盘价
close_range = np.arange(2,1199,4).astype(int)
close_price = pd.DataFrame(columns=ticks)
for i in close_range:
    close_price[ticks[i-1]] = price.iloc[:,i]

#重设列索引
open_price.index = range(len(open_price))
close_price.index = range(len(close_price))
ticks.index = range(len(ticks))

#创建空回报率
day_return_rate = pd.DataFrame(index=range(481),columns=ticks)
#计算当日回报率
for m in range(299):
    for i in range(len(open_price)):
        rate = (close_price.at[i,ticks[m]] - open_price.at[i,ticks[m]])/open_price.at[i,ticks[m]]
        day_return_rate.at[i,ticks[m]] = rate

day_return_rate.index = range(482)

#先做一支股票这种投资策略的回报率
#可以把这一段封装在函数里，传入批量生成的每一支股票的dataframe，进行持有期判断，输出每只股票投资成本，收益，回报率
#ascending升序，descending降序


###########################
#返回大下降的日期，这里要注意有可能大下降正好是这段时间的最后一天

list1 = []
list2 = []
list3 = []
for i in range(300):
    tag1 = ticks[i]+'buy_date'
    tag2 = ticks[i]+'sale_date'
    list1.append(tag1)
    list1.append(tag2)
    
    tag3 = ticks[i]+'buy_price'
    tag4 = ticks[i]+'sale_price'
    tag5 = ticks[i]+'return_rate'
    list2.append(tag3)
    list2.append(tag4)
    list2.append(tag5)
    
    tag6 = ticks[i]+'cost'
    tag7 = ticks[i]+'revenue'
    tag8 = ticks[i]+'return'
    list3.append(tag5)
    list3.append(tag6)
    list3.append(tag7)
    
    
buy_sale_date = pd.DataFrame(index=range(10),columns=list1)
#获取大下降买入价
#这里的columns可以写成一个列表遍历
buy_sale_price = pd.DataFrame(index=range(10),columns=list2)
#做一个判断：防止最终交易日期超出范围
#持有期要是一个可调参数，这里可以做成一个函数，这样调用起来方便一点
stock_return = pd.DataFrame(index=range(1),columns=list3)

#这里一共有300个排序
def return_rate(t):
    holding_period = t
    transaction_times = 10
    #循环300支股票
    for m in range(300): 
        decrease = day_return_rate.sort_values(by=ticks[m],ascending=True).index
        #获取前10行
        buy_index = decrease[:transaction_times]
        sale_index = buy_index + holding_period
        #判断是否超过这段实际那得最后一天，如果超过就在最后一天收盘时卖出
        #这里因为数据只有一列，所以ticks[0]要加一个中括号
        for i in range(transaction_times):
            buy_sale_date.at[i,list1[2*m]] = date[buy_index[i]]
            buy_sale_price.at[i,list2[3*m]] = close_price.at[buy_index[i],ticks[m]]
            if sale_index[i] <= 481:
                #获取卖出日期
                buy_sale_date.at[i,list1[2*m+1]] = date[sale_index[i]]
                #获取卖出价格
                buy_sale_price.at[i,list2[3*m+1]] = open_price.at[sale_index[i],ticks[m]]
            else:
                #如果超出最后一天成交日，就用最后一天
                buy_sale_date.at[i,list1[2*m+1]] = date[483]
                buy_sale_price.at[i,list2[3*m+1]] = open_price.at[481,ticks[0]]
            #计算每次投资回报率
            buy_sale_price.at[i,list2[3*m+2]] = (buy_sale_price.at[i,list2[3*m+1]]-buy_sale_price.at[i,list2[3*m]])/buy_sale_price.at[i,list2[3*m]]
        #计算每支股票的回报率
        stock_return.at[0,list3[3*m]] = buy_sale_price[list2[3*m]].sum()
        stock_return.at[0,list3[3*m+1]] = buy_sale_price[list2[3*m+1]].sum()
        stock_return.at[0,list3[3*m+2]] = (stock_return.at[0,list3[3*m+1]]-stock_return.at[0,list3[3*m]])/stock_return.at[0,list3[3*m]]


hh = return_rate(1)
hh


#寻找找一个最使得回报率最大的持有期
different_period = []
period = range(1,20)
for i in period:
    gg = return_rate(i) 
    different_period.append(gg)
max_return = max(different_period)
max_period = different_period.index(max(different_period))


print('操作记录:')
for i in range(10):
    print('{0}买入1股，{1}卖出'.format(buy_sale_date.at[i,'buy_date'],buy_sale_date.at[i,'sale_date']))
print('\n')
print('每笔投资持有{0}个交易日，回报{1:.5f}%'.format(max_period,max_return*100))


#需要优化的参数：持有天数，什么情况下买入，多少算大跌？
#时间可以用后面对应的序号索引结合date调取
#计算买入某一支股票的成本，收益，回报率












