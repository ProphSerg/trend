import requests
import os

MOEX_URL_PREF = 'http://iss.moex.com/'

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

def MOEXrequest(url, params):
    jar = requests.cookies.RequestsCookieJar()
    jar.set('MicexPassportCert', os.getenv('MOEX_AUTH') )

    req = requests.get(MOEX_URL_PREF + url,
        params = params,
        cookies = jar
    )
    return req
