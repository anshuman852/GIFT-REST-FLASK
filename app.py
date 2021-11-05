import re
import datetime
import requests
import sys
import traceback
from flask import Flask, Response, request, jsonify
from pyquery import PyQuery as pq
import json
import re
import markdown
import markdown.extensions.fenced_code
from bs4 import BeautifulSoup
from id_gen.id_generator import generate_id
word_regex_pattern = re.compile("[^A-Za-z]+")

def camel(chars):
  words = word_regex_pattern.split(chars)
  return "".join(w.lower() if i == 0 else w.title() for i, w in enumerate(words))

def create_app():
    app = Flask(__name__)
    @app.route('/')
    def index():
        readme_file = open("README.md", "r")
        md_template_string = markdown.markdown(
        readme_file.read(), extensions=["fenced_code"]
    )

        return md_template_string

    @app.route('/student/data', methods=["GET", "POST"])
    def get_data():
        if request.method == "POST":
            body=request.get_json()
            username=body["id"]
            password=body["pass"]
        else:
            username = request.args.get("id", default=None, type=str)
            password = request.args.get("pass", default=None, type=str)

        url = 'https://cms.gift.edu.in/index.php'

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

            resp=s.get(url)
            soup=BeautifulSoup(resp.text,'html.parser')
            info_url=soup.find('a',class_="btn btn-default btn-sm")['href']
            info_url='https://cms.gift.edu.in'+info_url
            info_resp=s.get(info_url)
            info_soup=BeautifulSoup(info_resp.text,'html.parser')
            #basic info like name, mentor etc
            basic_table=info_soup.find("table",class_="table table-striped")
            basic_soup=BeautifulSoup(str(basic_table),'html.parser')
            basic_table_keys=basic_soup.find_all("th")
            basic_table_values=basic_soup.find_all("td")
            basic_table_dict={}
            for i in range(len(basic_table_keys)):
                basic_table_dict[camel(basic_table_keys[i].text)]=basic_table_values[i].text.strip()
            profile_image=info_soup.find("img",alt="User Image")['src']
            profile_image='https://cms.gift.edu.in'+profile_image
            basic_table_dict['profileImage']=profile_image
            # personal details
            personal_table=info_soup.find("div",class_="tab-pane",id="personal")
            personal_soup=BeautifulSoup(str(personal_table),'html.parser')
            personal_table_keys=personal_soup.find_all('div',class_="edusec-profile-label")
            personal_table_values=personal_soup.find_all('div',class_="edusec-profile-text")
            personal_table_dict={}
            for i in range(len(personal_table_keys)):
                personal_table_dict[camel(personal_table_keys[i].text)]=personal_table_values[i].text.strip()

            #academic details
            academic_table=info_soup.find("div",class_="tab-pane",id="academic")
            academic_soup=BeautifulSoup(str(academic_table),'html.parser')
            academic_table_keys=academic_soup.find_all('div',class_="edusec-profile-label")
            academic_table_values=academic_soup.find_all('div',class_="edusec-profile-text")
            academic_table_dict={}
            for i in range(len(academic_table_keys)):
                academic_table_dict[camel(academic_table_keys[i].text)]=academic_table_values[i].text.strip()
            qualification_table=academic_soup.find("table",class_="table-bordered table table-striped")
            qualification_table=str(qualification_table).replace("<th>","<td>").replace("</th>","</td>")
            qualification_soup=BeautifulSoup(qualification_table,'html.parser')
            qual_rows=qualification_soup.find_all('tr')
            qual_rows=qual_rows[1:]
            qual_table_list=[]
            for i in range(len(qual_rows)):
                qual_dict={
                'qualification':qual_rows[i].find_all('td')[0].text.strip(),
                'institute':qual_rows[i].find_all('td')[1].text.strip(),
                'passoutYear':qual_rows[i].find_all('td')[2].text.strip(),
                'marks':qual_rows[i].find_all('td')[3].text.strip()
                }
                qual_table_list.append(qual_dict)
            academic_table_dict['qualification']=qual_table_list


            # guardians
            guardian_table=info_soup.find("div",class_="tab-pane",id="guardians")
            guardian_soup=BeautifulSoup(str(guardian_table),'html.parser')
            guardian_rows=guardian_soup.find_all("div",class_="row")
            guardian_rows=[s for s in guardian_rows if "edusec-profile-label" in str(s)]
            guardian_table_list=[]
            for i in range(len(guardian_rows)):
                guardian_dict={}
                guardian_row_keys=guardian_rows[i].find_all('div',class_="edusec-profile-label")
                guardian_row_values=guardian_rows[i].find_all('div',class_="edusec-profile-text")
                for j in range(len(guardian_row_keys)):
                    guardian_dict[camel(guardian_row_keys[j].text)]=guardian_row_values[j].text.strip()
                guardian_table_list.append(guardian_dict)

            #address
            address_table=info_soup.find("div",class_="tab-pane",id="address")
            address_soup=BeautifulSoup(str(address_table),'html.parser')
            address_table_rows=address_soup.find_all("div",class_="row")
            address_table_rows=[s for s in address_table_rows if "edusec-profile-label" in str(s)]
            address_table_list=[]
            for i in range(len(address_table_rows)):
                address_dict={}
                address_row_keys=address_table_rows[i].find_all('div',class_="edusec-profile-label")
                address_row_values=address_table_rows[i].find_all('div',class_="edusec-profile-text")

                for j in range(len(address_row_keys)):
                    address_dict["type"]="Current" if i==0 else "Permanent"
                    address_dict[camel(address_row_keys[j].text)]=address_row_values[j].text.strip()
                address_table_list.append(address_dict)

            #fees
            fees_table=info_soup.find("div",class_="tab-pane",id="fees")
            fees_soup=BeautifulSoup(str(fees_table),'html.parser')
            fees_basic=fees_soup.find("h4")
            fees_basic_vals=fees_basic.find_all('font')
            fees_dict={
                'total':fees_basic_vals[0].text.strip(),
                'paid':fees_basic_vals[1].text.strip(),
                'outstanding':fees_basic_vals[2].text.strip(),
            }
            fees_details_table=fees_soup.find('table',class_="kv-grid-table table table-bordered table-striped kv-table-wrap")
            fees_details_keys=fees_details_table.find_all('th')
            fees_details_body=fees_details_table.find('tbody')
            fees_details_body_rows=fees_details_body.find_all('tr')
            fees_details_list=[]
            for i in range(len(fees_details_body_rows)):
                fees_details_dict={
                    "num":fees_details_body_rows[i].find_all('td')[0].text.strip(),
                    camel(fees_details_keys[1].text.strip()):fees_details_body_rows[i].find_all('td')[1].text.strip(),
                    camel(fees_details_keys[2].text.strip()):fees_details_body_rows[i].find_all('td')[2].text.strip(),
                    camel(fees_details_keys[3].text.strip()):fees_details_body_rows[i].find_all('td')[3].text.strip(),
                }
                fees_details_list.append(fees_details_dict)
            payment_history_table=fees_soup.find_all('table',class_="kv-grid-table table table-bordered table-striped kv-table-wrap")[1]
            payment_history_keys=payment_history_table.find_all('th')
            payment_history_body=payment_history_table.find('tbody')
            payment_history_body_rows=payment_history_body.find_all('tr')
            payment_history_list=[]
            for i in range(len(payment_history_body_rows)):
                payment_history_dict={
                    "num":payment_history_body_rows[i].find_all('td')[0].text.strip(),
                    camel(payment_history_keys[1].text.strip()):payment_history_body_rows[i].find_all('td')[1].text.strip(),
                    camel(payment_history_keys[2].text.strip()):payment_history_body_rows[i].find_all('td')[2].text.strip(),
                    camel(payment_history_keys[3].text.strip()):payment_history_body_rows[i].find_all('td')[3].text.strip(),
                    camel(payment_history_keys[4].text.strip()):payment_history_body_rows[i].find_all('td')[4].text.strip(),
                    camel(payment_history_keys[5].text.strip()):payment_history_body_rows[i].find_all('td')[5].text.strip(),
                    camel(payment_history_keys[6].text.strip()):payment_history_body_rows[i].find_all('td')[6].text.strip(),
                    camel(payment_history_keys[7].text.strip()):payment_history_body_rows[i].find_all('td')[7].text.strip(),
                }
                payment_history_list.append(payment_history_dict)
            fees_dict['feesDetails']=fees_details_list
            fees_dict['paymentHistory']=payment_history_list

            #attendance
            attendance_table=info_soup.find("div",class_="tab-pane",id="attendance")
            attendance_soup=BeautifulSoup(str(attendance_table),'html.parser')
            attendance_table_rows=attendance_soup.find_all("tr")
            attendance_table_rows=attendance_table_rows[1:-1]
            attendance_table_list=[]
            for i in range(len(attendance_table_rows)):
                attendance_row_values=attendance_table_rows[i].find_all('th')
                attendance_dict={
                    "semester":attendance_row_values[0].text.strip(),
                    "totalClasses":attendance_row_values[1].text.strip(),
                    "classesAttended":attendance_row_values[2].text.strip(),
                    "percentage":attendance_row_values[3].text.strip(),
                }

                attendance_table_list.append(attendance_dict)
            #id card
            id_card_table=info_soup.find("div",class_="tab-pane",id="idcard")
            id_card_soup=BeautifulSoup(str(id_card_table),'html.parser')
            id_card_table_body=id_card_soup.find_all('td')[-1]
            id_card_table_body_rows=id_card_table_body.find_all('tr')
            id_card_dict={}
            for i in id_card_table_body_rows:
                ok=i.find_all("th")
                id_card_dict[camel(ok[0].text.strip())]=ok[-1].text.strip()
            id_card_dict['template']="https://cms.gift.edu.in/images/stu_i_card_template.jpg"

            id_link=generate_id(id_card_dict['name'],id_card_dict['regdNo'],id_card_dict['branch'],id_card_dict['validity'],personal_table_dict['bloodgroup'],profile_image)
            id_card_dict['idLink']=id_link
            final_dict=basic_table_dict
            final_dict['personal']=personal_table_dict
            final_dict['academic']=academic_table_dict
            final_dict['guardian']=guardian_table_list
            final_dict['address']=address_table_list
            final_dict['fees']=fees_dict
            final_dict['attendance']=attendance_table_list
            final_dict['id_card']=id_card_dict
            #send json
            return jsonify(final_dict)
        except:
            print(sys.exc_info()[0])
            traceback.print_exc()
            return "Unauthorized",503
    return app
if __name__ == "__main__":
   app = create_app()
   app.run(host='0.0.0.0', debug=True)
