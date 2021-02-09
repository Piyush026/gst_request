import base64
from random import choice

import requests
import gspread


def solveCaptcha():
    url = 'http://api.captcha.guru/in.php'
    api_key = '6ba2e16514850409e3a33b479f8a9e92'
    with open("captcha.png", "rb") as image_file:
        b64 = base64.b64encode(image_file.read())
    data = {'method': 'base64', 'key': api_key, 'body': b64}
    response = requests.post(url, data=data)
    tst = response.text.split('OK|')[1]
    while True:
        response = requests.get(
            "http://api.captcha.guru/res.php?key=6ba2e16514850409e3a33b479f8a9e92&action=get&id=" + tst)
        if 'OK' in response.text: break
    captcha_text = response.text.split('|')[1].upper()
    print(captcha_text)
    return captcha_text


def change_filigstatus(data):
    for x in data:
        for y in x:
            del y['mof']
            del y['arn']
            y['Financial Year'] = y.pop('fy')
            y['Tax Period'] = y.pop('taxp')
            y['Date of filing'] = y.pop('dof')
            y['gstType'] = y.pop('rtntype')
            y['Status'] = y.pop('status')
    # print(x)
    return x


def format_gst(data):
    gstFiling = {}
    rtn = []
    rtn1 = []
    rtn2 = []
    rtn3 = []
    rtn4 = []
    for y in data:
        if y['gstType'] == 'GSTR1':
            rtn.append(y)
        if y['gstType'] == 'GSTR3B':
            rtn1.append(y)
        if y['gstType'] == 'GSTR9':
            rtn2.append(y)
        if y['gstType'] == 'GSTR9C':
            rtn3.append(y)
        if y['gstType'] == 'GSTR6':
            rtn3.append(y)
        y.pop('gstType')

    if rtn is not None:
        gstFiling['GSTR1'] = rtn
    if rtn1 is not None:
        gstFiling['GSTR3B'] = rtn1
    if rtn2 is not None:
        gstFiling['GSTR9'] = rtn2
    if rtn3 is not None:
        gstFiling['GSTR9C'] = rtn3
    if rtn4 is not None:
        gstFiling['GSTR6'] = rtn4
    # print(gstFiling['GSTR9C'])
    if not gstFiling['GSTR1']:
        gstFiling.pop('GSTR1')
    if not gstFiling['GSTR3B']:
        gstFiling.pop('GSTR3B')
    if not gstFiling['GSTR9']:
        gstFiling.pop('GSTR9')
    if not gstFiling['GSTR9C']:
        gstFiling.pop('GSTR9C')
    if not gstFiling['GSTR6']:
        gstFiling.pop('GSTR6')
    return gstFiling


# format_gst(filing)
import pandas


def read_csv():
    file = "/home/ezeia/PycharmProjects/geekforgeeks/csv/ghh.csv"
    df = pandas.read_csv(file, usecols=['CIN_Number', 'pan'])
    sd = df.values
    tuples = [tuple(x) for x in df.values]
    # print(tuples)
    return tuples


# read_csv()
def read_google_sheet():
    gc = gspread.service_account(filename='creds.json')
    sheet = gc.open('Financial').worksheet("uplauds_gst_piyush")
    data = sheet.get_all_records()
    # print("data", data)
    pan = [tuple(x.values()) for x in data]
    # print(pan)
    return pan


# read_google_sheet()

with open('proxylist.txt', 'r') as f:
    p = f.read().split(',')
    proxy_list = list(map(lambda x: x.replace("'", '').strip(), p))
    # print(proxy_list)


def get_proxies():
    ip = choice(proxy_list)
    proxies = {"https": "https://h8pabpjbjl0d4k9:3zjLG24H5BDhLJa@{}:6060".format(ip),
               "https": "http://h8pabpjbjl0d4k9:3zjLG24H5BDhLJa@{}:6060".format(ip)}
    return proxies


# hu = get_proxies()
# print(hu)


