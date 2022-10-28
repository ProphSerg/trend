from assist import MOEXrequest, inTAG,genTableBody, genTableHead
import requests


def indexConsists(index):
    skipCol = ["indexid", "tradedate", "secids", "tradingsession"]
    colInfo = {
        'ticker': 'Инструмент',
        'shortnames': 'Наименование',
        'weight': 'Вес',
    }

    for start in range(20):
        req = MOEXrequest(url='iss/statistics/engines/stock/markets/index/analytics/' + index,
                          params={
                              'iss.meta': 'off',
                              'limit': 20,
                              'start': 20 * start,
                          },
                          )
        j = req.json()
        if len(j['analytics']['data']) == 0:
            break
        if start == 0:
            print(inTAG('h4', f'Индекс {index} расчитывается на основе:'))
            print('<table>' + genTableHead(
                j['analytics']['columns'],
                skipCol=skipCol,
                colInfo=colInfo
            ))
        print(genTableBody(j['analytics']['columns'], j['analytics']['data'], skipCol=skipCol, colInfo=colInfo))

    print('</table>')
