#!/usr/bin/env python3

import requests
import json
from urllib.parse import parse_qs
from assist import *
import secinfo_css
import secinfo_index

import os

inParam = parse_qs(os.getenv('QUERY_STRING'))

sendHeader()

if 'sec' not in inParam:
    # print(inTAG('h1','Не указан параметр sec, код инструмента!', param=['style="color:red";', ]))
    skipCol = ['id', 'regnumber', 'emitent_id', 'emitent_inn', 'emitent_okpo', 'gosreg', 'type', 'marketprice_boardid']
    colInfo = {
        'name': 'Наименование',
        'emitent_title': 'Наименование эмитента',
        'is_traded': {'title': 'Торгуется', 'view': lambda a: 'Да' if a == 1 else 'Нет'}
    }
    for start in range(10):
        req = MOEXrequest(url='iss/securities',
                          params={
                              'iss.meta': 'off',
                              'limit': 100,
                              'start': 100 * start,
                          },
                          )
        j = req.json()
        if len(j['securities']['data']) == 0:
            break
        if start == 0:
            sendDocBegin(style=secinfo_css.style, MOEXinfo=req)
            print('<table>' + genTableHead(
                j['securities']['columns'],
                skipCol=skipCol,
                colInfo=colInfo
            ))
        print(genTableBody(j['securities']['columns'], j['securities']['data'], skipCol=skipCol, colInfo=colInfo))

    print('</table>')
    sendDocEnd()
    exit(0)

sendDocBegin(style=secinfo_css.style)

securites = {
    'ticker': inParam['sec'][0].upper(),
    'type': '',
}
print(inTAG('h3', f'Информация о инструменте: {securites["ticker"]}'))
req = MOEXrequest(url='iss/securities/' + securites['ticker'],
                  params={
                      'iss.meta': 'off',
                  },
                  )
j = req.json()
if len(j['description']['data']) == 0:
    exit(-1)

skipCol = ["type", "sort_order", "is_hidden", "precision"]
colInfo = {
    'title': 'Наименование',
    'value': 'Значение',
}
print(genTable(j['description']['columns'], j['description']['data'], skipCol=skipCol, colInfo=colInfo))

for dt in j['description']['data']:
    if dt[0] == 'GROUP' and dt[2] == 'stock_index':
        securites['type'] = 'index'

print(inTAG('h3', 'Торгуется на:'))
skipCol = ["board_group_id", "market_id", "engine_id", "decimals", "history_from", "history_till", "listed_from", "listed_till"]
colInfo = {
    'title': 'Наименование',
    'market': 'Рынок',
    'engine': 'Торговая система',
    'is_traded': {'title': 'Торгуется', 'view': lambda a: 'Да' if a == 1 else 'Нет'},
    'is_primary': {'title': 'Основной режим', 'view': lambda a: 'Да' if a == 1 else 'Нет'},
    'currencyid': {'title': 'Код валюты', 'view': lambda a: '' if a is None else a},
}
print(genTable(j['boards']['columns'], j['boards']['data'], skipCol=skipCol, colInfo=colInfo))

if securites['type'] == 'index':
    secinfo_index.indexConsists(securites['ticker'])

sendDocEnd()
