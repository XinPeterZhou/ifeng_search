# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 13:17:08 2018
凤凰搜索爬虫
@author: baili
"""

import requests
import pandas as pd
import re
import datetime
from bs4 import BeautifulSoup
 
#在这里输入要搜索的关键词 
keywords=['挖财','百里']

#建立输出文本的框架
df=pd.DataFrame

for key in keywords:
    #确定搜索结果页数total_num
    url='https://search.ifeng.com/sofeng/article?c=1&u=&q='+key+'&p=1'
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text,'html.parser')
    total_info = soup.find('p', class_ = 'result', align="reft")
    total_str=total_info.get_text()
    total_num=int(total_str[total_str.find('约')+1:total_str.find('条')])
    
    #建立输出文本的框架
    df=pd.DataFrame(columns=('title','from','time','url','status'))
    
    #从搜索页查询基本信息
    for page in range(0,total_num//10):
        url='https://search.ifeng.com/sofeng/article?c=1&u=&q='+key+'&p='+repr(page+1)
        res = requests.get(url)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text,'html.parser')
        news = soup.find_all('div', class_ = 'searchResults')
        for i in range(10):
            item=news[i]
            df.loc[page*10+i,'title']=item.p.a.get_text().strip()
            temp_str=item.find_all('font')[-1].get_text().strip().replace('\t','')
            df.loc[page*10+i,'from']=re.split('\r\n',temp_str)[0]
            try:
                temp_time=re.split('\r\n',temp_str)[1].strip()
                df.loc[page*10+i,'time']=datetime.datetime.strptime(temp_time[0:10],'%Y-%m-%d')
            except:
                pass
            
            df.loc[page*10+i,'url']=item.p.a.get('href').strip()

    #结果去重和排序
    #df=df.sort_values(by='time')
    #df=df.drop_duplicates(['title'],'last')

    #检查原文是否有效
    for page in range(0,len(df)):
        url=df.loc[page,'url']
        res = requests.get(url)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text,'html.parser')
        #print(soup)
        if soup.title.string in('404 Not Found','手机凤凰网-提示页','404-页面不存在'):
            df.loc[page,'status']='无效'
        else: 
            df.loc[page,'status']='有效'
    #print (df)
    df.to_excel('ifeng_search_'+key+'.xls')
