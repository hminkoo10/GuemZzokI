from flask import Flask, jsonify, request
import requests,random,json,datetime,urllib3
from bs4 import BeautifulSoup
from twilio.rest import Client

pnt = {}
TWILIO_ACCOUNT_SID = '비공개'
TWILIO_AUTH_TOKEN = '비공개'
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
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
    mscu = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY=비공개&Type=json&pIndex=1&pSize=100&ATPT_OFCDC_SC_CODE={gccode}&SD_SCHUL_CODE={sccode}"
    mpara = {
        "KEY": "비공개",
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

def get_time(date,sc,grade,class_,n=0):
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
        meal = "시간표가 없어요"
        return meal
    if rj["schoolInfo"][1]["row"][n]["SCHUL_NM"].endswith("초등학교"):
        mscu = f"https://open.neis.go.kr/hub/elsTimetable?KEY=비공개&Type=json&pIndex=1&pSize=100&ATPT_OFCDC_SC_CODE={gccode}&SD_SCHUL_CODE={sccode}"
        tb = "elsTimetable"
    elif rj["schoolInfo"][1]["row"][n]["SCHUL_NM"].endswith("중학교"):
        mscu = f"https://open.neis.go.kr/hub/misTimetable?KEY=비공개&Type=json&pIndex=1&pSize=100&ATPT_OFCDC_SC_CODE={gccode}&SD_SCHUL_CODE={sccode}"
        tb = "misTimetable"
    elif rj["schoolInfo"][1]["row"][n]["SCHUL_NM"].endswith("고등학교"):
        mscu = f"https://open.neis.go.kr/hub/hisTimetable?KEY=비공개&Type=json&pIndex=1&pSize=100&ATPT_OFCDC_SC_CODE={gccode}&SD_SCHUL_CODE={sccode}"
        tb = "hisTimetable"
    mpara = {
        "KEY": "비공개",
        "Type": "json",
        "pIndex":1,
        "pSize":100,
        "ATPT_OFCDDC_SC_CODE": gccode,
        "SD_SCHUL_CODE": sccode,
        "TI_FROM_YMD": date,
        "TI_TO_YMD": date,
        "GRADE": grade,
        "CLASS_NM": class_
    }
    mres = requests.get(url=mscu, params=mpara, verify=False, json=True)
    mres.encoding = "UTF-8"
    mrj = mres.json()
    try:
        tt = ""
        t = mrj[tb][0]["head"][0]["list_total_count"]
        for i in range(t):
            tn = mrj[tb][1]["row"][i]["ITRT_CNTNT"].replace("-","")
            tt += f"{i+1}교시 : {tn}\n"
    except Exception as e:
        return str(e)
    return tt

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
            "apikey": "비공개",
            "messages" :[{"role": "user", "content": request_data['action']['params']['question']}],
            "userdata": [["user", request_data['userRequest']['user']['id']]]},
            headers={"apikey":"비공개"}, timeout=0.3)
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

@application.route("/time",methods=["POST"])
def time():
    rd = json.loads(request.get_data(),encoding='utf-8')
    response = { "version": "2.0", "template": { "outputs": [{
        "simpleText": {"text": f"현재 점검중"}
    }]}}
    #return jsonify(response)
    q = rd['action']['params']['question'].replace(" ","")
    n = q.split("#")
    n = q.split("#")
    c = rd['action']['params']['class'].replace(" ","")
    try:
        c1 = c.split("-")[0]
        c2 = c.split("-")[1]
    except:
        response = { "version": "2.0", "template": { "outputs": [{
            "simpleText": {"text": f"학년/반을 정확히 -로 구분해서 말해주세요"}
        }]}}
        return jsonify(response)
    if len(n) == 1:
        n.append(1)
    reg = get_school_info(n[0],int(n[1])-1)
    if reg == "없는 학교에요":
        response = { "version": "2.0", "template": { "outputs": [{
            "simpleText": {"text": f"없는 학교에요"}
        }]}}
        return jsonify(response)
    diet = f"이번주 {reg['지역']} {reg['한글이름']} 시간표입니다"
    today = datetime.datetime.today()
    last_monday = today - datetime.timedelta(days = today.weekday())
    for i in range(5):
        gi = (last_monday + datetime.timedelta(days = i)).strftime("%Y%m%d")
        diet = f"{diet}\n\n[ {(last_monday + datetime.timedelta(days = i)).strftime('%Y년 %m월 %d일')} {weekday[str(i+2)]} ]\n{get_time(gi,n[0],c1,c2,int(n[1])-1)}"
    response = { "version": "2.0", "template": { "outputs": [{
        "simpleText": {"text": diet}
    }]}}
    with open("bot.log", "a+") as f:
        f.write(f"\n\n\n\n\n{rd['userRequest']['user']['id']} : 시간표 명령어를 입력함\n{q} {c}\n{diet}")
    return jsonify(response)

@application.route("/scinf",methods=["POST"])
def scinf():
    try:
        rd = json.loads(request.get_data(),encoding='utf-8')
        q = rd['action']['params']['question'].replace(" ","")
        n = q.split("#")
        c = rd['action']['params']['class'].replace(" ","")
        try:
            c1 = c.split("-")[0]
            c2 = c.split("-")[1]
        except:
            response = { "version": "2.0", "template": { "outputs": [{
                "simpleText": {"text": f"학년/반을 정확히 -로 구분해서 말해주세요"}
            }]}}
            return jsonify(response)
        if len(n) == 1:
            n.append(1)
        reg = get_school_info(n[0],int(n[1])-1)
        if reg == "없는 학교에요":
            response = { "version": "2.0", "template": { "outputs": [{
                "simpleText": {"text": f"없는 학교에요"}
            }]}}
            return jsonify(response)
        gi = datetime.datetime.now().strftime("%Y%m%d")
        msg=""
        msg+="[ 오늘의 급식 ]\n"
        msg+=get_diet(gi,n[0],int(n[1])-1)
        msg += "\n"
        msg+="\n[ 오늘의 시간표 ]\n"
        msg+=get_time(gi,n[0],c1,c2,int(n[1])-1)
        #if(SchoolApi("SchoolSchedule", params).schedule()!="x"):
        #    msg+="[ 오늘의 학사일정 ]\n"
        #    msg+=SchoolApi("SchoolSchedule", params).schedule()
        response = { "version": "2.0", "template": { "outputs": [{
            "simpleText": {"text": msg}
        }]}}
        with open("bot.log", "a+") as f:
            f.write(f"\n\n\n\n\n{rd['userRequest']['user']['id']} : 오늘 명령어를 사용함\n{msg}")
        return jsonify(response)
    except Exception as e:
        response = { "version": "2.0", "template": { "outputs": [{
            "simpleText": {"text": str(e)}
        }]}}
        return jsonify(response)

@application.route("/register",methods=["POST"])
def register():
    rd = json.loads(request.get_data(),encoding='utf-8')
    response = { "version": "2.0", "template": { "outputs": [{
            "simpleText": {"text": "이 기능은 현재 점검중입니다"}
        }]}}
    return jsonify(response)
    if rd['userRequest']['user']['id'] in pnt.keys():
        response = { "version": "2.0", "template": { "outputs": [{
            "simpleText": {"text": "이미 가입 요청을 했습니다\n문의 : https://open.kakao.com/me/hyunminkoo"}
        }]}}
        with open("bot.log", "a+") as f:
            f.write(f"\n\n\n\n\n{rd['userRequest']['user']['id']} : 가입 재요청 했으므로 입구컷")
        return jsonify(response)
    n = '\n금쪽이 가입 인증번호\n'
    for i in range(8):
        n += str(random.randint(0,9))
    client.messages.create(
        to=f"+82{rd['action']['params']['phone']}",
        from_="비공개",
        body=n
    )
    pnt[rd['userRequest']['user']['id']]  = (n,rd['action']['params']['phone'],rd['action']['params']['name'])
    response = { "version": "2.0", "template": { "outputs": [{
        "simpleText": {"text": "휴대전화로 인증번호 8자리를 보내드렸어요! '인증' 명령어로 인증번호를 입력 해 주세요!"}
    }]}}
    with open("bot.log", "a+") as f:
        f.write(f"\n\n\n\n\n{rd['userRequest']['user']['id']} : 가입신청함\n이름 : {rd['action']['params']['name']}\n전화번호 : {rd['action']['params']['phone']}")
    return jsonify(response)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=80, debug=False)
