import pandas as pd
import numpy as np
import streamlit as st
import polars as pl
import plotly.express as px
import requests
import json

st.set_page_config(page_title='Ardshinbank parser', page_icon=':bank:', layout='centered')
excel_files = st.file_uploader(label='Upload excel file', accept_multiple_files=True)

def get_rate():
    url = "https://website-api.ardshinbank.am/currency"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload).text

    resp = json.loads(response)

    usd = resp['data']['currencies']['cash'][0]['sell']
    usd = float(usd)
    rub = resp['data']['currencies']['cash'][2]['sell']
    rub = float(rub)

    return(usd, rub)

def filter_excel(excel_file):
    df = pl.read_excel(excel_file, sheet_name='Account ARM',)
    no_header = df.tail(-23)
    final = no_header.head(-13)
    cols = ['Date', 'Amount in currency', 'Currency', 'Income', 'Empty1', 'Expense', 'Exchange rate', 'Empty2', 'Transction date', 'Empty3', 'Amount left', 'Empty4', 'Comment', 'Empty5']
    final.columns = cols
    df = pd.DataFrame(final, columns=cols)
    return(df)


def get_stats(df, show):
    df.dropna(subset=['Date'], inplace=True)
    df_final = df[['Date', 'Income', 'Expense', 'Comment']]
    income = 0
    for x in df['Income']:
        if x is None: continue
        x = float(x)
        income+=x  
    if st.radio == 'USD':
        income = income / usd
    st.metric(label='Gain', value = '', delta=f'{income} \u058F', label_visibility='collapsed')
    expense = 0
    for x in df['Expense']:
        if x is None: continue
        x = float(x[1:])
        abs(x)
        expense+=x
    loss = float("{:.1f}".format(expense))
    st.metric(label='Loss', value = '', delta=f'-{loss} \u058F', label_visibility='collapsed')
    if show:
       st.dataframe(df_final)


def draw_plots(df):
    df_final = df[['Comment', 'Expense']]
    dict = {}
    for comment, expense in df_final.values:
        if expense is None: continue
        expense = float(expense[1:])
        expense = float("{:.1f}".format(expense))
        if 'SAS' in comment:
            comment = 'SAS'
        if 'AMZN' in comment:
            comment = 'AMAZON'
        if '\AM\YEREVAN' in comment:
            comment = comment[20:]
        if comment not in dict:
            dict[comment] = 0
        dict[comment]+=expense
    datas = [x for x in dict.values()]
    label = [x for x in dict.keys()]
    fig = px.pie(values = datas, names = label, title=f'{filename[10:12]}.{filename[12:14]} - {filename[17:19]}.{filename[19:21]}',color = label, color_discrete_map={
        'SAS': 'red',
        'YANDEX EATS':'yellow',
        'BYUZAND BRANC':'grey',
        'BAREKAMUTYUN':'grey',
        'IDRAM':'lightsalmon',
        'YANDEX TAXI':'lightyellow',
        'WWW.WILDBERRI':'mediumvioletred',
        'WILDBERRIES':'mediumvioletred',
        'AMAZON':'chocolate'
    })
    fig.update_traces(textposition='inside', textinfo='percent+label+value', hoverinfo=None)
    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True)

usd, rub = get_rate()

st.header(f'Current exchange rates: {usd}\u0024, {rub}\u20BD')

show = st.checkbox(label='Show transactions', key='Show')

if excel_files:
    for excel_file in excel_files:
        filename = excel_file.name
        df = filter_excel(excel_file)
        get_stats(df, show)
        draw_plots(df)
        

        