#!/usr/bin/env python3

import requests
import json
import instrument

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
        return int(a / b * 100)
    except:
        return None

def getTrend(bid, offer):
    if bid is None or offer is None:
        return ''
    return '<span style="color:%s";>%s' %('green' if bid > offer else 'red', 'к покупке' if bid > offer else 'к продаже')

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
        #jar.set('MicexPassportCert', '1664453989007', domain='.moex.com', path='/')
        
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
sortBy['VOLTODAY'] = sorted(data['marketdata'], key=lambda md: md['VOLTODAY'], reverse=True)
sortBy['VALTODAY'] = sorted(data['marketdata'], key=lambda md: md['VALTODAY'], reverse=True)

print('<html lang="ru_RU"><head><meta charset="UTF-8">', flush=True)
print(inTAG('style', 'table {border-collapse: collapse; border: 1px solid black;}'))
print('</head><body>')

print(inTAG('h3', 'X-MicexPassport-Marker: ' + inTAG('b', req.headers['X-MicexPassport-Marker'], NL=False)))
print(inTAG('h3', 'Загружено: %d инструменов' %len(data['marketdata'])))

print('<table border="1" style="border: 2px solid blue;"><tr>')
for s in sortBy:
    print(inTAG('th', 'Сортировка по: %s' %s, param=['style="text-align: center;"',]))
print('</tr><tr>')

for s in sortBy:
    col = ['BOARDID', 'SECID', s, 'BIDDEPTH', 'BIDDEPTHT', 'OFFERDEPTH', 'OFFERDEPTHT']
    print( \
        '<td><table border="1">' +
        inTAG('tr', ''.join(list(
            map(lambda c: inTAG('th', c, param=['style="text-align: center;"',], NL=False), col + ['BID %%', 'OFFER%%', 'Тенденция'])
        )))
    )
    tot = {
        'BIDDEPTHT': 0,
        'OFFERDEPTHT': 0,
    }
    for i in range(15):
        bid = getPrc(sortBy[s][i]['BIDDEPTHT'], sortBy[s][i]['BIDDEPTHT'] + sortBy[s][i]['OFFERDEPTHT'])
        offer = getPrc(sortBy[s][i]['OFFERDEPTHT'], sortBy[s][i]['BIDDEPTHT'] + sortBy[s][i]['OFFERDEPTHT'])
        tot['BIDDEPTHT'] = tot['BIDDEPTHT'] + sortBy[s][i]['BIDDEPTHT']
        tot['OFFERDEPTHT'] = tot['OFFERDEPTHT'] + sortBy[s][i]['OFFERDEPTHT']
        print(inTAG('tr',
                ''.join(list(map(lambda c: inTAG('td',sortBy[s][i][c], NL=False), col))) +
                inTAG('td', '%s %%' %bid, NL=False) +
                inTAG('td', '%s %%' %offer, NL=False) +
                inTAG('td', getTrend(bid, offer), NL=False)
            )
        )

    bid = getPrc(tot['BIDDEPTHT'], tot['BIDDEPTHT'] + tot['OFFERDEPTHT'])
    offer = getPrc(tot['OFFERDEPTHT'], tot['BIDDEPTHT'] + tot['OFFERDEPTHT'])
    print(
        inTAG('tr',
            inTAG('td', 'ИТОГО', param=['colspan=3',], NL=False) + inTAG('td', '', NL=False) +
            inTAG('td', tot['BIDDEPTHT'], NL=False) + inTAG('td', '', NL=False) +
            inTAG('tg', tot['OFFERDEPTHT'], NL=False) + inTAG('td', '', NL=False) +
            inTAG('td', '%s %%' % bid, NL=False) +
            inTAG('td', '%s %%' % offer, NL=False) +
            inTAG('td', getTrend(bid, offer), NL=False)
        )
    )

    print('</table></td>')
print('</tr></table>')
print('<p><h3>BID %% = BIDDEPTHT / (BIDDEPTHT + OFFERDEPTHT) * 100%</h3>')
print('<p><h3>OFFER %% = OFFERDEPTHT / (BIDDEPTHT + OFFERDEPTHT) * 100%</h3>')
print('</body></html>')
