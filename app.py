import re
from datetime import datetime

import requests
from flask import Flask, Response, request
from pyquery import PyQuery as pq
def create_app():
    app = Flask(__name__)


    @app.route('/', methods=["GET", "POST"])
    def get_data():
        url = 'https://cms.gift.edu.in/index.php'
        username = request.args.get("id", default=None, type=str)
        password = request.args.get("pass", default=None, type=str)
        if not username or not password:
            return "Error BC",503
        s = requests.session()
        rget = s.get(url)
        csrfpass = rget.text.split('"csrf-token" content="')[1].split('"')[0]
        headers = {}
        headers['Cookie'] = 'PHPSESSID='+s.cookies['PHPSESSID'] + \
            '; _csrf=' + s.cookies['_csrf']
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        headers['Accept-Encoding'] = 'gzip, deflate, br'
        headers['Accept-Language'] = 'en-GB,en-US;q=0.9,en;q=0.8'
        headers['Cache-Control'] = 'max-age=0'
        headers['Connection'] = 'keep-alive'
        headers['Content-Length'] = '206'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Host'] = 'cms.gift.edu.in'
        headers['Origin'] = 'https://cms.gift.edu.in'
        headers['Referer'] = 'https://cms.gift.edu.in/index.php?r=site%2Flogin'
        headers['Sec-Fetch-Dest'] = 'document'
        headers['Sec-Fetch-Mode'] = 'navigate'
        headers['Sec-Fetch-Site'] = 'same-origin'
        headers['Sec-Fetch-User'] = '?1'
        headers['Upgrade-Insecure-Requests'] = '1'
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
        payload = {'_csrf': csrfpass, 'LoginForm[username]': username,
                'LoginForm[password]': password, 'LoginForm[rememberMe]': '0', 'LoginForm[rememberMe]': '1', 'login-button': ''}

        resp = s.post('https://cms.gift.edu.in/index.php?r=site%2Flogin',
                    data=payload, headers=headers)
        headers['Cookie'] = 'PHPSESSID='+s.cookies['PHPSESSID'] + \
            '; _csrf=' + s.cookies['_csrf']

        try:
            mainpage = s.get(url)
            d = pq(mainpage.text)
            pictureselector = "body > div.wrapper.row-offcanvas.row-offcanvas-left > aside.right-side > section > section.content.edusec-user-profile > div > div.col-lg-3.table-responsive.edusec-pf-border.no-padding.edusecArLangCss > div > img"
            button = d("body > div.wrapper.row-offcanvas.row-offcanvas-left > aside.right-side > section > section > div:nth-child(2) > div.col-sm-4.col-xs-12 > div > div.box-footer.text-right > a")
            dashboardlink = "https://cms.gift.edu.in" + \
                button.attr("href") + "#attendance"
            dashhtml = (s.get(dashboardlink)).text
            d = pq(dashhtml)
            picslink = d(pictureselector).attr("src")
            attdtable = d(
                'div[id="attendance"] > table[class="table-bordered table table-striped"] > tbody > tr')
            print(attdtable)
            for i in attdtable:
                print(attdtable[i].children[2].children[0].data)
            ok = d('#attendance > table.table-bordered.table.table-striped')
            semester = []
            for a in ok.items():
                semester = re.findall("[0-9]+\%", ok.text())
            print(semester)
            result = {
                "picurl": picslink,
                "semester": semester
            }
            return result
            print(picslink)
            print(result)
            print(datetime.now() - startTime)
        except:
            print("fail")
            return "Invalid Creds",503
    return app
if __name__ == "__main__":
   app = create_app()
   app.run(host='0.0.0.0', debug=True)