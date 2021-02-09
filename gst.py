import json
from json_format import change_filigstatus, format_gst, solveCaptcha, read_csv, read_google_sheet, get_proxies
import requests
from datetime import date
import save_db
from fake_useragent import UserAgent
import time

ua = UserAgent()

proxy = get_proxies()


def fetch_pan(num):
    headers = {
        'User-Agent': str(ua.random)}
    session = requests.session()
    # response = session.get('https://services.gst.gov.in/services/searchtpbypan', headers=headers)
    captchaRequest = session.get('https://services.gst.gov.in/services/captcha')
    if captchaRequest.status_code == 200:
        with open("captcha.png", 'wb') as f:
            f.write(captchaRequest.content)
    response = session.post('https://services.gst.gov.in/services/api/get/gstndtls', headers=headers, proxies=proxy,
                            json={"panNO": num, "captcha": solveCaptcha()})
    data = response.json()
    print(data)
    return data


def pan(number):
    data = fetch_pan(number)
    while 'errorCode' in data.keys():
        print("error")
        data = fetch_pan(number)
        if 'errorCode' not in data.keys():
            break
    active_gst = data['gstinResList']
    lst = []
    for x in active_gst:
        if x['authStatus'] == 'Active':
            lst.append(x['gstin'])
    return lst


# panNO = 'AADCF2098R'
# cin = 'U74900AN2016PTC000286'
# lst = pan(panNO)
# print(lst)

cname = {}


def call_api(session, headers, gstin):
    print("call in api")
    captchaRequest = session.get('https://services.gst.gov.in/services/captcha')
    if captchaRequest.status_code == 200:
        with open("captcha.png", 'wb') as f:
            f.write(captchaRequest.content)
    taxpayerDetails = session.post('https://services.gst.gov.in/services/api/search/taxpayerDetails',
                                   headers=headers, proxies=proxy,
                                   json={"gstin": gstin, "captcha": solveCaptcha()})

    return taxpayerDetails


def gst(panNO):
    # outr = {}
    try:
        for gstin in panNO:
            headers = {
                'User-Agent': str(ua.random)}
            session = requests.session()
            captchaRequest = session.get('https://services.gst.gov.in/services/captcha')

            if captchaRequest.status_code == 200:
                with open("captcha.png", 'wb') as f:
                    f.write(captchaRequest.content)
                    taxpayerDetails = session.post('https://services.gst.gov.in/services/api/search/taxpayerDetails',
                                                   headers=headers, proxies=proxy,
                                                   json={"gstin": gstin, "captcha": solveCaptcha()})
                    error = taxpayerDetails.json()
                    while 'errorCode' in error.keys():
                        print("errorCode")
                        taxpayerDetails = call_api(session, headers, gstin)
                        error = taxpayerDetails.json()
                        if 'errorCode' not in error.keys():
                            break

                    taxpayerReturnDetails = session.post(
                        'https://services.gst.gov.in/services/api/search/taxpayerReturnDetails',
                        headers=headers, proxies=proxy,
                        json={"gstin": gstin, "captcha": solveCaptcha()})
                    # return True

                    url = f"https://services.gst.gov.in/services/api/search/goodservice?gstin={gstin}"
                    page = requests.get(url)
                    bzgddtls = page.text
                    jsn = json.loads(bzgddtls)
                    cmp = json.loads(taxpayerDetails.text)
                    # print(cmp)
                    cmp_details = {
                        # 'companyName': cmp['lgnm'],
                        'Legal Name of Business': cmp['lgnm'],
                        'Trade Name': cmp['tradeNam'],
                        'date': cmp['rgdt'],
                        'Administrative Office': cmp['stj'],
                        'Other Office': cmp['ctj'],
                        'Principal Place of Business': cmp['pradr'].get('adr'),
                        'pan': gstin[2:-3]

                    }
                    filingstatus = json.loads(taxpayerReturnDetails.text)
                    filing = change_filigstatus(filingstatus['filingStatus'])
                    # print("filing", filing)
                    gstdata = format_gst(filing)
                    inner_dict = {
                        "CompanyDetails": cmp_details,
                        'gstFiling': gstdata,
                        'goodsAndServices': jsn,
                        'Created_at': str(date.today())

                    }
                    # outr[gstin] = inner_dict
    finally:
        return inner_dict


# gst(lst)


def main():
    while True:
        tuples = read_csv()
        print(tuples[:1])
        for x in tuples[:1]:
            gst_dict = {}
            try:
                pan_lst = pan(x[1][2:-3])
                respo = gst(pan_lst)
                gst_dict[x[0]] = respo
            except Exception as e:
                print(str(e))
                continue
            finally:
                print("gstt", gst_dict)
                if gst_dict:
                    save_db.insertData(gst_dict)
        time.sleep(60)


start_time = time.time()
print(start_time)
main()
duration = time.time() - start_time
print(f"data  in {duration} seconds")
# proxy = get_proxies()
# headers = {'User-Agent': str(ua.random)}
# url = 'https://httpbin.org/ip'
# r = requests.get(url, headers=headers, proxies=proxy)
# print(r.json())
