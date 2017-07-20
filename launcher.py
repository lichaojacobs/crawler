# -*- coding: utf-8 -*-
import urllib2
import re
import rsa
import cookielib
import base64
import json
import urllib
import binascii
from lxml import etree
import json


# 用于模拟登陆新浪微博
class launcher():
    cookieContainer = None
    _headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"
    }

    def __init__(self, username, password):
        self.password = password
        self.username = username

    def get_prelogin_args(self):

        '''
        该函数用于模拟预登录过程,并获取服务器返回的 nonce , servertime , pub_key 等信息
        '''
        json_pattern = re.compile('\((.*)\)')
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&' + self.get_encrypted_name() + '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)'
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            raw_data = response.read().decode('utf-8')
            print "get_prelogin_args" + raw_data;
            json_data = json_pattern.search(raw_data).group(1)
            data = json.loads(json_data)
            return data
        except urllib2.HTTPError as e:
            print("%d" % e.code)
            return None

    def get_encrypted_pw(self, data):
        rsa_e = 65537  # 0x10001
        pw_string = str(data['servertime']) + '\t' + str(data['nonce']) + '\n' + str(self.password)
        key = rsa.PublicKey(int(data['pubkey'], 16), rsa_e)
        pw_encypted = rsa.encrypt(pw_string.encode('utf-8'), key)
        self.password = ''  # 清空password
        passwd = binascii.b2a_hex(pw_encypted)
        print(passwd)
        return passwd

    def get_encrypted_name(self):
        username_urllike = urllib.quote(self.username)
        byteStr = bytes(username_urllike)
        byteStrEncod = byteStr.encode(encoding="utf-8")
        username_encrypted = base64.b64encode(byteStrEncod)
        return username_encrypted.decode('utf-8')

    def enableCookies(self):
        # 建立一个cookies 容器
        self.cookieContainer = cookielib.MozillaCookieJar("/Users/lichao/desktop/weibo/cookie/cookie.txt");
        # ckjar=cookielib.MozillaCookieJar("/Users/Apple/Desktop/cookie.txt")
        # 将一个cookies容器和一个HTTP的cookie的处理器绑定
        cookie_support = urllib2.HTTPCookieProcessor(self.cookieContainer)
        # 创建一个opener,设置一个handler用于处理http的url打开
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        # 安装opener，此后调用urlopen()时会使用安装过的opener对象
        # proxy_handler = urllib2.ProxyHandler({"http": 'http://localhost:5000'})
        # opener=urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)

    def loadCookies(self):
        # 创建MozillaCookieJar实例对象
        cookie = cookielib.MozillaCookieJar()
        # 从文件中读取cookie内容到变量
        cookie.load('/Users/lichao/desktop/weibo/cookie/cookie.txt', ignore_discard=True, ignore_expires=True)
        # 利用urllib2的build_opener方法创建一个opener
        proxy_handler = urllib2.ProxyHandler({"http": 'http://localhost:5000'})
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), proxy_handler)
        urllib2.install_opener(opener)

    def build_post_data(self, raw):
        post_data = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "useticket": "1",
            "pagerefer": "http://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=http%3A%2F%2Fweibo.com%2F&domain=.weibo.com&ua=php-sso_sdk_client-0.6.14",
            "vsnf": "1",
            "su": self.get_encrypted_name(),
            "service": "miniblog",
            "servertime": raw['servertime'],
            "nonce": raw['nonce'],
            "pwencode": "rsa2",
            "rsakv": raw['rsakv'],
            "sp": self.get_encrypted_pw(raw),
            "sr": "1280*800",
            "encoding": "UTF-8",
            "prelt": "77",
            "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype": "META"
        }
        data = urllib.urlencode(post_data).encode('utf-8')
        return data

    def login(self):
        url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        self.enableCookies()
        data = self.get_prelogin_args()
        post_data = self.build_post_data(data)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"
        }
        try:
            request = urllib2.Request(url=url, data=post_data, headers=headers)
            response = urllib2.urlopen(request)
            html = response.read().decode('GBK')
            # print(html)
        except urllib2.HTTPError as e:
            print(e.code)

        p = re.compile('location\.replace\(\'(.*?)\'\)')
        p2 = re.compile(r'"userdomain":"(.*?)"')

        try:
            login_url = p.search(html).group(1)
            print(login_url)
            request = urllib2.Request(login_url)
            response = urllib2.urlopen(request)
            page = response.read().decode('utf-8')
            print(page)
            login_url = 'http://weibo.com/' + p2.search(page).group(1)
            request = urllib2.Request(login_url)
            response = urllib2.urlopen(request)
            final = response.read().decode('utf-8')

            print("Login success!")
            self.cookieContainer.save(ignore_discard=True, ignore_expires=True)
        except Exception, e:
            print('Login error!')
            print e
            return 0

    def showOneRumor(self, url):
        try:
            # cookie = cookielib.MozillaCookieJar()
            # 从文件中读取cookie内容到变量
            # cookie.load('/Users/apple/desktop/weibo/cookie/cookie.txt', ignore_discard=True, ignore_expires=True)
            # 利用urllib2的build_opener方法创建一个opener
            # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
            request = urllib2.Request(url);
            response = urllib2.urlopen(request);
            html = response.read().decode('utf-8')
            print html
        except urllib2.HTTPError as e:
            print e.code;
            return 0
