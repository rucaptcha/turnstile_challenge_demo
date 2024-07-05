import json
import os
import re
import requests
from seleniumbase import Driver
from actual_proxy import *


my_key = os.environ["APIKEY"]
proxy = proxy1      #proxy format: "login:password@ip:port"

def intercept(driver):
    driver.execute_script(""" 
    console.clear = () => console.log('Console was cleared')
    const i = setInterval(()=>{
    if (window.turnstile)
     console.log('success!!')
     {clearInterval(i)
         window.turnstile.render = (a,b) => {
          let params = {
                sitekey: b.sitekey,
                pageurl: window.location.href,
                data: b.cData,
                pagedata: b.chlPageData,
                action: b.action,
                userAgent: navigator.userAgent,
                json: 1
            }
            console.log('intercepted-params:' + JSON.stringify(params))
            window.cfCallback = b.callback
            return        } 
    }
},50)    
""")  # ЗДЕСЬ ПАРАМЕТРЫ УЖЕ ВЫВЕДЕНЫ В КОНСОЛЬ БРАУЗЕРА А ТАКЖЕ ПЕРЕОПРЕДЕЛЕНА CALLBACK-ФУНКЦИЯ
    driver.sleep(1)
    logs = driver.get_log("browser")  # ЗДЕСЬ В КОДЕ НИЖЕ МЫ ОТЛАВЛИВАЕМ НУЖНУЮ ИНФОРМАЦИЮ (НАШИ ПАРАМЕТРЫ) ИЗ КОНСОЛИ БРАУЗЕРА
    for log in logs:
        if log['level'] == 'INFO':
            if "intercepted-params:" in log["message"]:
                log_entry = log["message"].encode('utf-8').decode('unicode_escape')
                match = re.search(r'"intercepted-params:({.*?})"', log_entry)
                json_string = match.group(1)
                params = json.loads(json_string)
                return params

agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
driver = Driver(uc=True, log_cdp=True, headless=False, no_sandbox=True, agent=agent, proxy=proxy)#НАСТРОЙКА ДРАЙВЕРА ДЛЯ РАБОТЫ В БЕЗГОЛОВОМ РЕЖИМЕ
url = "https://2captcha.com/ru/demo/cloudflare-turnstile-challenge"
driver.open(url)
try:
    driver.find_element("#AYJX7")  # ПРОВЕРЯЕМ, ВЫПАДАЕТ ЛИ ТУРНИКЕТ НА ДАННОМ САЙТЕ
except:
    print("Турникета нет ...")
else:
    print("Решаем капчу...")
    driver.refresh()
    params = intercept(driver)  # ФУНКЦИЯ ПЕРЕХВАТА ПАРАМЕТРОВ
    print(params)
    data0 = {"key": my_key,
            "method": "turnstile",
            "sitekey": params["sitekey"],
            "action": params["action"],
            "data": params["data"],
            "pagedata": params["pagedata"],
            "useragent": agent,
            "json": 1,
            "pageurl": params["pageurl"],
            }
    response = requests.post(f"https://2captcha.com/in.php?", data=data0)  # ОТПРАВЛЯЕМ ЗАПРОС НА 2CAPTCHA
    print("Запрос отправлен", response.text)
    s = response.json()["request"]
    driver.sleep(15)
    while True:
        solu = requests.get(f"https://2captcha.com/res.php?key={my_key}&action=get&json=1&id={s}").json()
        if solu["request"] == "CAPCHA_NOT_READY":
            print(solu["request"])
            driver.sleep(8)
        elif "ERROR" in solu["request"]:
            print(solu["request"])
            driver.close()
            driver.quit()
        else:
            break
    for key, value in solu.items():
        print(key, ": ", value)
    token = solu['request']
    try:
        driver.execute_script(f" cfCallback('{token}');")  # ВЫЗЫВАЕМ НАШУ CALLBACK-ФУНКЦИЮ
        driver.sleep(15)
    except Exception as e:
        print(e)
finally:
    driver.quit()
