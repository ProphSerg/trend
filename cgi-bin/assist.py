import requests
import os

MOEX_URL_PREF = 'https://iss.moex.com/'


def sendHeader():
    print('Content-Type: text/html;charset=utf-8')
    print()


def sendDocBegin(style='', MOEXinfo=None):
    print(
        '<!DOCTYPE html>\n'
        '<html lang="ru_RU">\n'
        '<head>\n'
        '<meta charset="UTF-8">' +
        inTAG('style', style, NL=False) +
        '\n</head><body>'
    )
    if MOEXinfo is not None:
        print(inTAG('h3', 'X-MicexPassport-Marker: ' +
                    inTAG('span', MOEXinfo.headers['X-MicexPassport-Marker'],
                          param=['style="color:%s";' % (
                              'green' if MOEXinfo.headers['X-MicexPassport-Marker'] == 'granted' else 'red'), ],
                          NL=False))
              )


def sendDocEnd():
    print('</body></html>')


def inTAG(tag, data, param=None, NL=True):
    return '<%s%s>%s</%s>%s' % (
        tag,
        ' ' + ' '.join(param) if param is not None else '',
        data,
        tag,
        '' if NL == False else '<p>'
    )


def MOEXrequest(url, params):
    if not url.endswith('.json'):
        url += '.json'
    jar = requests.cookies.RequestsCookieJar()
    jar.set('MicexPassportCert', os.getenv('MOEX_AUTH'))

    req = requests.get(MOEX_URL_PREF + url,
                       params=params,
                       cookies=jar
                       )
    return req


def genTableHead(columns, skipCol=[], colInfo={}):
    thead = ''
    for col in columns:
        if col in skipCol:
            continue
        thead += inTAG('th',
                       (colInfo[col]['title'] if isinstance(colInfo[col], dict) else colInfo[col]) if col in colInfo else col,
                       NL=False)
    return inTAG('thead', inTAG('tr', thead, NL=False), NL=False)


def genTableBody(columns, data, skipCol=[], colInfo={}):
    tbody = ''
    for dt in data:
        tr = ''
        for col in range(len(columns)):
            if columns[col] in skipCol:
                continue
            tr += inTAG('td',
                        colInfo[columns[col]]['view'](dt[col]) if
                            columns[col] in colInfo and
                            'view' in colInfo[columns[col]]
                        else dt[col],
                        NL=False)
        tbody += inTAG('tr', tr, NL=False)
    return inTAG('tbody', tbody, NL=False)


def genTable(columns, data, skipCol=[], colInfo={}):
    return inTAG('table',
                 genTableHead(columns, skipCol=skipCol, colInfo=colInfo) +
                 genTableBody(columns, data, skipCol=skipCol, colInfo=colInfo),
                 )
