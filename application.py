from flask import Flask, jsonify, request
import requests
import json
from bs4 import BeautifulSoup
import re
import datetime
import urllib3
from neispy import Neispy
import asyncio

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
dt = datetime.datetime
application = Flask(__name__)
a = {}
weekday = {
    "1":"일요일",
    "2":"월요일",
    "3":"화요일",
    "4":"수요일",
    "5":"목요일",
    "6":"금요일",
    "7":"토요일"
}

def get_html(url):
   _html = ""
   resp = requests.get(url)
   if resp.status_code == 200:
      _html = resp.text
   return _html
 
def get_school_info(sc,n=0):
    scu = "https://open.neis.go.kr/hub/schoolInfo"
    para = {
        "KEY": None,
        "Type": "json",
        "pIndex": None,
        "pSize": None,
        "ATPT_OFCDDC_SC_CODE": None,
        "SD_SCHUL_CODE": None,
        "SCHUL_NM": sc,
        "SCHUL_KND_SC_NM": None,
        "LCTN_SC_NM": None,
        "FOND_SC_NM": None,
    }
    res = requests.get(url=scu, params=para, verify=False, json=True)
    res.encoding = "UTF-8"
    rj = res.json()
    try:
        a = rj["schoolInfo"][1]["row"][n]["LCTN_SC_NM"]
    except:
        a = "없는 학교에요"
        return a
    return {
        "교육청":rj["schoolInfo"][1]["row"][n]["ATPT_OFCDC_SC_NM"],
        "지역":rj["schoolInfo"][1]["row"][n]["LCTN_SC_NM"],
        "주소":rj["schoolInfo"][1]["row"][n]["ORG_RDNMA"],
        "교육지원청":rj["schoolInfo"][1]["row"][n]["JU_ORG_NM"],
        "한글이름":rj["schoolInfo"][1]["row"][n]["SCHUL_NM"],
        "영어이름":rj["schoolInfo"][1]["row"][n]["ENG_SCHUL_NM"],
        "전화":rj["schoolInfo"][1]["row"][n]["ORG_TELNO"],
        "팩스":rj["schoolInfo"][1]["row"][n]["ORG_FAXNO"],
        "사이트":rj["schoolInfo"][1]["row"][n]["HMPG_ADRES"],
        "공학":rj["schoolInfo"][1]["row"][n]["COEDU_SC_NM"],
        "우편번호":rj["schoolInfo"][1]["row"][n]["ORG_RDNZC"],
        "학교코드":rj["schoolInfo"][1]["row"][n]["SD_SCHUL_CODE"],
        "설립일":rj["schoolInfo"][1]["row"][n]["FOND_YMD"]
    }

def get_diet(date,sc,n=0):
    scu = "https://open.neis.go.kr/hub/schoolInfo"
    para = {
        "KEY": None,
        "Type": "json",
        "pIndex": None,
        "pSize": None,
        "ATPT_OFCDDC_SC_CODE": None,
        "SD_SCHUL_CODE": None,
        "SCHUL_NM": sc,
        "SCHUL_KND_SC_NM": None,
        "LCTN_SC_NM": None,
        "FOND_SC_NM": None,
    }
    res = requests.get(url=scu, params=para, verify=False, json=True)
    res.encoding = "UTF-8"
    rj = res.json()
    try:
        sccode = rj["schoolInfo"][1]["row"][n]["SD_SCHUL_CODE"]
        gccode = rj["schoolInfo"][1]["row"][n]["ATPT_OFCDC_SC_CODE"]
    except:
        meal = "급식이 없어요"
        return meal
    mscu = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    mscu = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY=&Type=json&pIndex=1&pSize=100&ATPT_OFCDC_SC_CODE={gccode}&SD_SCHUL_CODE={sccode}"
    mpara = {
        "KEY": "",
        "Type": "json",
        "pIndex":1,
        "pSize":100,
        "ATPT_OFCDDC_SC_CODE": gccode,
        "SD_SCHUL_CODE": sccode,
        "MLSV_YMD": date
    }
    mres = requests.get(url=mscu, params=mpara, verify=False, json=True)
    mres.encoding = "UTF-8"
    mrj = mres.json()
    try:
        meal = mrj["mealServiceDietInfo"][1]["row"][0]["DDISH_NM"].replace("<br/>","\n")
    except:
        meal = "급식이 없어요"
    return meal

class SchoolApi:

    params = {
        "KEY": "",
        "Type": "json",
    }

    schoolinfo = {}

    base_url = "https://open.neis.go.kr/hub/"
    def __init__(self, sub_url, params):
        self.sub_url = sub_url
        self.params = params
    def get_data(self):
        URL = SchoolApi.base_url + self.sub_url
        self.params.update(SchoolApi.params)
        self.params.update(SchoolApi.schoolinfo)
        response = requests.get(URL, params=self.params)

        try:
            j_response = json.loads(response.text)[self.sub_url]
            if j_response[0]["head"][0]["list_total_count"] == 1:
                return j_response[1]["row"][0]
            else:
                return j_response[1]["row"]
        except:
            print("찾는 데이터가 없습니다.")
            return response.text
    def meal(self):
        data = self.get_data()
        try:
            string = "<조식>\n"+data[0]["DDISH_NM"].replace("<br/>", "\n")+"\n\n"
            string+= "<중식>\n"+data[1]["DDISH_NM"].replace("<br/>", "\n")+"\n\n"
            string += "<석식>\n" + data[2]["DDISH_NM"].replace("<br/>", "\n")
            characters = "1234567890./-*"
            for x in range(len(characters)):
                string = string.replace(characters[x],"")
            return string
        except:
            return "오늘은 급식이 없습니다."
    def time(self):
        data = self.get_data()
        string = ""
        try:
            for i in data:
                string += i["ITRT_CNTNT"] + "\n"
            return string
        except:
            return "오늘은 시간표가 없습니다."

    def schedule(self):
        data = self.get_data()
        try:
            return "오늘은 "+data["EVENT_NM"]+"이(가) 있습니다."
        except:
            return "x"

    def get_school_info(self):
        data = self.get_data()
        try:
            SchoolApi.schoolinfo = {
            "ATPT_OFCDC_SC_CODE": data["ATPT_OFCDC_SC_CODE"],
            "SD_SCHUL_CODE": data["SD_SCHUL_CODE"]
            }
        except:
            print("학교를 못 찾겠어요")


@application.route("/webhook/", methods=["POST"])
def webhook():
    global a
    request_data = json.loads(request.get_data(), encoding='utf-8')
    a[request_data['user']] = request_data['result']['choices'][0]['message']['content']
    return 'OK'
@application.route("/question", methods=["POST"])
def get_question():
    global a
    request_data = json.loads(request.get_data(), encoding='utf-8')
    response = {"version": "2.0", "template": {"outputs": [{
        "simpleText": {"text": f'질문을 받았습니다. "답변"을 입력하셔서 답변을 보실 수 있어요'}
    }]}}
    try:
        del a[request_data['userRequest']['user']['id']]
    except:
        pass
    a[request_data['userRequest']['user']['id']] = '아직 AI가 처리중이에요. 다시 답변을 입력 해 주세요'
    try:
        api = requests.post('https://api.asyncia.com/v1/api/request/', json={
            "apikey": "",
            "messages" :[{"role": "user", "content": request_data['action']['params']['question']}],
            "userdata": [["user", request_data['userRequest']['user']['id']]]},
            headers={"apikey":""}, timeout=0.3)
    except requests.exceptions.ReadTimeout:
        pass
    with open("bot.log", "a+") as f:
        f.write(f"\n\n\n\n\n{request_data['userRequest']['user']['id']} : chat gpt 명령어를 입력함\n{request_data['action']['params']['question']}")
    return jsonify(response)
@application.route("/ans", methods=["POST"])
def hello2():
    request_data = json.loads(request.get_data(), encoding='utf-8')
    response = { "version": "2.0", "template": { "outputs": [{
        "simpleText": {"text": f"{a.get(request_data['userRequest']['user']['id'], '질문을 하신적이 없어보여요. 질문부터 해주세요')}"}
    }]}}
    with open("bot.log", "a+") as f:
        f.write(f"\n\n\n\n\n{request_data['userRequest']['user']['id']} : 답변 명령어를 입력함\n{a.get(request_data['userRequest']['user']['id'], '질문을 하신적이 없어보여요. 질문부터 해주세요')}")
    return jsonify(response)

@application.route("/meal",methods=["POST"])
def meal():
    rd = json.loads(request.get_data(),encoding='utf-8')
    response = { "version": "2.0", "template": { "outputs": [{
        "simpleText": {"text": f"현재 점검중"}
    }]}}
    #return jsonify(response)
    q = rd['action']['params']['question'].replace(" ","")
    n = q.split("#")
    if len(n) == 1:
        n.append(1)
    reg = get_school_info(n[0],int(n[1])-1)
    if reg == "없는 학교에요":
        response = { "version": "2.0", "template": { "outputs": [{
            "simpleText": {"text": f"없는 학교에요"}
        }]}}
        return jsonify(response)
    diet = f"이번주 {reg['지역']} {reg['한글이름']} 급식 정보입니다"
    today = datetime.datetime.today()
    last_monday = today - datetime.timedelta(days = today.weekday())
    for i in range(5):
        gi = (last_monday + datetime.timedelta(days = i)).strftime("%Y%m%d")
        diet = f"{diet}\n\n[ {(last_monday + datetime.timedelta(days = i)).strftime('%Y년 %m월 %d일')} {weekday[str(i+2)]} ]\n{get_diet(gi,n[0],int(n[1])-1)}"
    response = { "version": "2.0", "template": { "outputs": [{
        "simpleText": {"text": diet}
    }]}}
    with open("bot.log", "a+") as f:
        f.write(f"\n\n\n\n\n{rd['userRequest']['user']['id']} : 급식 명령어를 입력함\n{q}\n{diet}")
    return jsonify(response)

@application.route("/scinf",methods=["POST"])
def scinf():
    rd = json.loads(request.get_data(),encoding='utf-8')
    if rd['action']['params']['question'] != "학교이름":
        response = { "version": "2.0", "template": { "outputs": [{
        "simpleText": {"text": f"현재 경기도 교육청 일부 학교만 지원하고 있습니다."}
    }]}}
        with open("bot.log", "a+") as f:
            f.write(f"\n\n\n\n\n{rd['userRequest']['user']['id']} : 오늘 명령어를 사용함 (다른학교 입력해 접근거부)")
        return jsonify(response)
    params = {
        "SCHUL_NM": rd['action']['params']['question'] + "학교"
    }
    SchoolApi("schoolInfo", params).get_school_info()
    msg=""
    params = {"MLSV_YMD": dt.now().strftime("%Y%m%d")}
    msg+="[ 오늘의 급식 ]\n"
    msg+=SchoolApi("mealServiceDietInfo", params).meal()
    params = {"GRADE": "1", "CLASS_NM": "3", "ALL_TI_YMD": dt.now().strftime("%Y%m%d")}
    msg+="\n[ 오늘의 시간표 ]\n"
    msg+=SchoolApi("hisTimetable", params).time()
    if(SchoolApi("SchoolSchedule", params).schedule()!="x"):
        msg+="[ 오늘의 학사일정 ]\n"
        msg+=SchoolApi("SchoolSchedule", params).schedule()
    response = { "version": "2.0", "template": { "outputs": [{
        "simpleText": {"text": msg}
    }]}}
    with open("bot.log", "a+") as f:
        f.write(f"\n\n\n\n\n{rd['userRequest']['user']['id']} : 오늘 명령어를 사용함\n{msg}")
    return jsonify(response)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=80, debug=True)
