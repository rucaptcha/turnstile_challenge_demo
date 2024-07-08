import os
from actual_proxys import *      # here are your proxies
from seleniumbase import Driver
from twocaptcha import TwoCaptcha  # pip3 install 2captcha-python


my_key = os.environ["APIKEY"]  # your APIKEY 2CAPTCHA
solver = TwoCaptcha(my_key)
proxy = proxy0 #proxy format: "login:password@ip:port"
agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
driver = Driver(uc=True, proxy=False, headless=False, agent=agent, locale_code='en', devtools=False)
try:
    url = "https://2captcha.com/ru/demo/cloudflare-turnstile"
    driver.open(url)
    print("Solve captcha, wait...")
    sitekey = "0x4AAAAAAAVrOwQWPlm3Bnr5"
    result = solver.turnstile(sitekey=sitekey, url=url, useragent=agent,
                                 # proxy={'type': 'HTTPS',
                                 #        'uri': proxy}
                              )
    print("Token received")
    driver.execute_script("document.getElementsByName('cf-turnstile-response')[0].value = arguments[0];", result['code'])  # insert the token into this element
    # driver.execute_script("document.getElementsByName('g-recaptcha-response')[0].value = arguments[0];", result['code'])  # and this one too
    # driver.execute_script("document.getElementsByTagName('form')[0].submit();")  # send a form with data
    driver.sleep(30)
except Exception as e:
    print(e)
finally:
    driver.close()
    driver.quit()


