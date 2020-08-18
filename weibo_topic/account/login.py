
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import pymongo
# from db_utils import insert_cookie

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

mongodb = pymongo.MongoClient('127.0.0.1', 27017)
account_collection = mongodb['weibo']['account']


class WeiboLogin():
    def __init__(self, username, password):
        self.url = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https://weibo.cn/'
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        mobile_emulation = {"deviceMetrics": {"width": 1050, "height": 840, "pixelRatio": 3.0},
                            "userAgent": user_agent}

        self.browser  = webdriver.Edge("C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe")
        self.username = username
        self.password = password


    def login(self):
        """
        open login page and login
        :return: None
        """
        self.browser.get(self.url)
        wait = WebDriverWait(self.browser, 5)
        username = wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))
        submit = wait.until(EC.element_to_be_clickable((By.ID, 'loginAction')))
        username.send_keys(self.username)
        password.send_keys(self.password)
        submit.click()

    def run(self):
        try:
            self.login()
            WebDriverWait(self.browser, 20).until(
                EC.title_is('我的首页')
            )
            cookies = self.browser.get_cookies()
            cookie = [item["name"] + "=" + item["value"] for item in cookies]
            cookie_str = '; '.join(item for item in cookie)
            return cookie_str
        except Exception as e:
            logging.error(str(traceback.format_exc()))
        finally:
            self.browser.quit()
        return None


def main():
    with open('account.txt', 'r') as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        username, password = line.split('----')
        logging.info('username:{},password:{}'.format(username,password))
        logging.info('=' * 30)
        logging.info(f'start fetching cookie [{username}]')
        cookie_str = WeiboLogin(username, password).run()
        if not cookie_str:
            continue
        logging.info(f'cookie: {cookie_str}')
        cookie_item = {
            'username':username,
            'password':password,
            'cookie':cookie_str
        }
        account_collection.insert_one(cookie_item)
        # insert_cookie(username, password, cookie_str)


if __name__ == '__main__':
    main()
    # browser = webdriver.Edge("C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe")
