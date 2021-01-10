import re
import datetime
import requests
import sys
import traceback
from flask import Flask, Response, request
from pyquery import PyQuery as pq
import json

def create_app():
    app = Flask(__name__)

    @app.route('/', methods=["GET", "POST"])
    def get_data():
        url = 'https://cms.gift.edu.in/index.php'
        username = request.args.get("id", default=None, type=str)
        password = request.args.get("pass", default=None, type=str)
        if not username or not password:
            return "Error BC",503
        with open("ok.json") as f:
            ttdata=json.load(f)
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
            picslink = "https://cms.gift.edu.in"+d(pictureselector).attr("src")
            ok = d('#attendance > table.table-bordered.table.table-striped')
            semester = []
            for a in ok.items():
                semester = re.findall("[0-9]+.[0-9]+\%", ok.text())
            today=datetime.datetime.today()
            ##name = d("body > div.wrapper.row-offcanvas.row-offcanvas-left > aside.right-side > section > section.content.edusec-user-profile > div > div.col-lg-3.table-responsive.edusec-pf-border.no-padding.edusecArLangCss > table > tbody > tr:nth-child(2) > td").text()
            datatable="body > div.wrapper.row-offcanvas.row-offcanvas-left > aside.right-side > section > section.content.edusec-user-profile > div > div.col-lg-3.table-responsive.edusec-pf-border.no-padding.edusecArLangCss"
            infolist=((d(datatable)).text()).split("\n")
            ##Convert the list to a dict
            print(infolist)
            infodict={infolist[i]: infolist[i+1] for i in range(0,(len(infolist)-1),2)}
            course=infodict["Batch"].split()[0]
            section=d("#academic > div:nth-child(4) > div > div.col-md-8.col-xs-8.edusec-profile-text").text()
            passout=infodict["Batch"].split()[1].split("-")[0]
            passout=int(passout)
            if course == "BTECH":
                sem= (today.year - passout) * 2 + 8
            if course =="MBA" or course =="MCA":
                sem= (today.year -passout) *2 + 4
                section=course

            if today.month >= 7:
                sem=sem+1
            timetable=""
            for i in ttdata:
                title=i["title"]
                if course in title and section in title and str(sem) in title:
                    timetable=i["link"]
            result = {
                "id": username,
                "name": infodict["Name"],
                "section": section,
                "course":course,
                "sem":sem,
                "phone": infodict["Mobile No"],
                "email": infodict["Domain Email ID"],
                "passout":passout,
                "picurl": picslink,
                "attendance": semester,
                "timetable": timetable
                }
            return result
        except:
            print(sys.exc_info()[0])
            traceback.print_exc()
            return "Unauthorized",503
    return app
if __name__ == "__main__":
   app = create_app()
   app.run(host='0.0.0.0', debug=True)
