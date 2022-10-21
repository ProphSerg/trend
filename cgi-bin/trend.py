#!/usr/bin/env python3

import requests
import json
import instrument
import os

settingISS = {
    'stock': {
        'shares': ['TQBR', 'TQPI', 'TQIF', 'TQTF'],
        'foreignshares': ['FQBR', ]
    },
}

URL_PREF = 'http://iss.moex.com/'
data = {
    'securities': [],
    'marketdata': []
}

def convertData(dt):
    da = []
    for d in dt['data']:
        dh = {}
        for c in range(len(dt['columns'])):
            dh.update({dt['columns'][c]: d[c]})
        da.append(dh)
    return da

def getPrc(a, b):
    try:
        return round(a / b * 100)
    except:
        return None

def getTrend(bid, offer):
    trend = (
        ('к покупке', 'к продаже'),
        ('green',     'red')
    )
    if bid is None or offer is None:
        return ''
    idx = 0 if bid >= offer else 1
    return inTAG('span', trend[0][idx], param=['style="color:%s";' %(trend[1][idx]), ], NL=False)


def sendHeader():
    print('Content-Type: text/html;charset=utf-8')
    print()

def sendDocBegin():
    print(
        '<!DOCTYPE html>\n'
        '<html lang="ru_RU">\n'
        '<head>\n'
        '<meta charset="UTF-8">' +
        inTAG('style', 'table {border-collapse: collapse; border: 1px solid black;}', NL=False) +
        '\n</head><body>'
    )

def sendDocEnd():
    print('</body></html>')

def inTAG(tag, data, param=None, NL=True):
    return '<%s%s>%s</%s>%s' %(
        tag,
        ' ' + ' '.join(param) if param is not None else '',
        data,
        tag,
        '' if NL == False else '<p>'
    )

for e in settingISS:
    for m in settingISS[e]:
        jar = requests.cookies.RequestsCookieJar()
        # установка cookie `tasty_cookie=yum` на путь `httpbin.org/cookies`
        jar.set('MicexPassportCert', os.getenv('MOEX_AUTH'),
                #domain='.moex.com', path='/'
                )
        
        req = requests.get(URL_PREF + 'iss/engines/%s/markets/%s/securities.json' %(e, m),
            params = {
                'iss.meta': 'off',
                #'securities': 'SBER',
                #'marketdata.columns': 'SECID,BOARDID,VOLTODAY,VALTODAY',
                'iss.only': 'marketdata',
            },
            cookies = jar
        )
        j = req.json()
        
        for i in j['marketdata']['data']:
            if not (i[1] in instrument.instrument and i[0] in instrument.instrument[i[1]]):
                j['marketdata']['data'].remove(i)
        
        #data['securities'] = data['securities'] + convertData(j['securities'])
        data['marketdata'] = data['marketdata'] + convertData(j['marketdata'])

sortBy = {}
#sortBy['VOLTODAY'] = sorted(data['marketdata'], key=lambda md: md['VOLTODAY'], reverse=True)
sortBy['VALTODAY'] = sorted(data['marketdata'], key=lambda md: md['VALTODAY'], reverse=True)

sendHeader()
sendDocBegin()

print(inTAG('h3', 'X-MicexPassport-Marker: ' +
            inTAG('span', req.headers['X-MicexPassport-Marker'],
                  param=['style="color:%s";' %('green' if req.headers['X-MicexPassport-Marker'] == 'granted' else 'red'), ],
                  NL=False))
      )
print(inTAG('h3', 'Загружено: %d инструменов' %len(data['marketdata'])))

print('<table border="1" style="border: 2px solid blue;"><tr>')
for s in sortBy:
    print(inTAG('th', 'Сортировка по: %s' %s, param=['style="text-align: center;"',], NL=False))
print('</tr><tr>')

for s in sortBy:
    col = ['BOARDID', 'SECID', s, 'BIDDEPTH', 'BIDDEPTHT', 'OFFERDEPTH', 'OFFERDEPTHT']
    print(
        '<td><table border="1">' +
        inTAG('tr', ''.join(list(
            map(lambda c: inTAG('th', c, param=['style="text-align: center;"',], NL=False), col +
                ['BID %%', 'OFFER %%', 'Тенденция', 'BIDT %%', 'OFFERT %%', 'Тенденция'])
        )), NL=False)
    )
    tot = {
        'BIDDEPTH': 0,
        'BIDDEPTHT': 0,
        'OFFERDEPTH': 0,
        'OFFERDEPTHT': 0,
    }
    for i in range(15):
        bid = getPrc(sortBy[s][i]['BIDDEPTH'], sortBy[s][i]['BIDDEPTH'] + sortBy[s][i]['OFFERDEPTH'])
        offer = getPrc(sortBy[s][i]['OFFERDEPTH'], sortBy[s][i]['BIDDEPTH'] + sortBy[s][i]['OFFERDEPTH'])
        bidt = getPrc(sortBy[s][i]['BIDDEPTHT'], sortBy[s][i]['BIDDEPTHT'] + sortBy[s][i]['OFFERDEPTHT'])
        offert = getPrc(sortBy[s][i]['OFFERDEPTHT'], sortBy[s][i]['BIDDEPTHT'] + sortBy[s][i]['OFFERDEPTHT'])
        for t in tot:
            tot[t] = tot[t] + sortBy[s][i][t]
        print(inTAG('tr',
                ''.join(list(map(lambda c: inTAG('td',sortBy[s][i][c], NL=False), col))) +
                inTAG('td', '%s %%' %bid, NL=False) +
                inTAG('td', '%s %%' %offer, NL=False) +
                inTAG('td', getTrend(bid, offer), NL=False) +
                inTAG('td', '%s %%' % bidt, NL=False) +
                inTAG('td', '%s %%' % offert, NL=False) +
                inTAG('td', getTrend(bidt, offert), NL=False)
        , NL=False)
        )

    bid = getPrc(tot['BIDDEPTH'], tot['BIDDEPTH'] + tot['OFFERDEPTH'])
    offer = getPrc(tot['OFFERDEPTH'], tot['BIDDEPTH'] + tot['OFFERDEPTH'])
    bidt = getPrc(tot['BIDDEPTHT'], tot['BIDDEPTHT'] + tot['OFFERDEPTHT'])
    offert = getPrc(tot['OFFERDEPTHT'], tot['BIDDEPTHT'] + tot['OFFERDEPTHT'])
    print(
        inTAG('tr',
            inTAG('th', 'ИТОГО', param=['colspan=3 style="text-align: left;"',], NL=False) +
            inTAG('td', tot['BIDDEPTH'], NL=False) +
            inTAG('td', tot['BIDDEPTHT'], NL=False) +
            inTAG('td', tot['OFFERDEPTH'], NL=False) +
            inTAG('td', tot['OFFERDEPTHT'], NL=False) +
            inTAG('td', '%s %%' % bid, NL=False) +
            inTAG('td', '%s %%' % offer, NL=False) +
            inTAG('td', getTrend(bid, offer), NL=False) +
            inTAG('td', '%s %%' % bidt, NL=False) +
            inTAG('td', '%s %%' % offert, NL=False) +
            inTAG('td', getTrend(bidt, offert), NL=False)
    , NL=False)
    )

    print('</table></td>')

print('</tr></table>')
print(inTAG('h3', 'BID %% = BIDDEPTH / (BIDDEPTH + OFFERDEPTH) * 100%'))
print(inTAG('h3', 'OFFER %% = OFFERDEPTH / (BIDDEPTH + OFFERDEPTH) * 100%'))
print(inTAG('h3', 'BIDT %% = BIDDEPTHT / (BIDDEPTHT + OFFERDEPTHT) * 100%'))
print(inTAG('h3', 'OFFERT %% = OFFERDEPTHT / (BIDDEPTHT + OFFERDEPTHT) * 100%'))

req = requests.get(URL_PREF + 'iss/engines/stock/markets/shares/securities/columns.json',
       params={
           'iss.meta': 'off',
           'iss.only': 'marketdata',
       },
)
j = req.json()

print('<table border="1">')
for c in ['BOARDID', 'SECID', 'VOLTODAY', 'VALTODAY', 'BIDDEPTH', 'BIDDEPTHT', 'OFFERDEPTH', 'OFFERDEPTHT']:
    for d in j['marketdata']['data']:
        if d[1] == c:
            print(
                inTAG('tr',
                      inTAG('th', c, param=['style="text-align: left;"',], NL=False) +
                      inTAG('td', d[3], NL=False)
                , NL=False)
            )
            break
print('</table>')

sendDocEnd()
