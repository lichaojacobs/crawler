# -*- coding: utf-8 -*-
import io
import json
import sys
import urllib2

from lxml import etree

reload(sys)
sys.setdefaultencoding('utf-8')


class LauncherForMobile():
    _header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36",
        "Cookie": "ALF=1502988115; SCF=Ar5UfkXoZ0iG9eqd8aHuycbamrDcEaONHoKoPz3Za6PddtHso0iMpAoewEX8PtJl9P-JkPrC4YX9nVXJQkwwO3c.; SUB=_2A250akoDDeRhGeVP61MX9yzKyT-IHXVXlVZLrDV6PUJbktANLXDDkW2CFl2MQbkjShlsIijK-RjnRj7t6Q..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhPUuFTXg4zll8rx_8Ap-XA5JpX5o2p5NHD95Q0eK5pSoMESoz0Ws4DqcjUCHBLxKML1K.LB.BLxK-L1K5L1heLxKML1KBLBoMt; SUHB=0FQbA4zhNlxY9F; SSOLoginState=1500396115; _T_WM=7f0ce7abef316b03c8497584623fd57c"
    }

    # show user's profile
    def showSomeBlogs(self, url, cookiePath, savePath):
        try:
            self.loadCookie(cookiePath)
            request = urllib2.Request(url=url, headers=self._header)
            response = urllib2.urlopen(request)
            html = response.read()
            selector = etree.HTML(html)
            weibos = selector.xpath('//div[@class="c"]')
            if (len(weibos) == 0):
                print "invalid login"
                return
                # remove settings elements
            weibos.pop()
            weibos.pop()
            weiboResults = []
            for weibo in weibos:
                # analytics some properties
                if (len(weibo.xpath('./div/span[@class="ctt"]')) != 0):
                    text = weibo.xpath('./div/span[@class="ctt"]')[0]
                    info = text.xpath('string(.)')
                    # 正文
                    resultText = info.replace("\n", '').replace(" ", "")
                    # 转发
                    transmitNode = weibo.xpath('./div[last()]/span[2]')
                    transmit = ""
                    if (transmitNode != None and len(transmitNode) != 0):
                        transmit = weibo.xpath('./div[last()]/span[2]')[0].xpath('string(.)')
                    # 评论
                    comment = weibo.xpath('./div[last()]/a[@class="cc"]')
                    if (comment != None and len(comment) != 0):
                        comment = weibo.xpath('./div[last()]/a[@class="cc"]')[0].xpath('string(.)')
                        weiboResults.append({"text": resultText, "transimit": transmit, "comment": comment});

                # auto like
                try:
                    if (len(weibo.xpath('./div[last()]/span[@class="cmt"]')) == 0):
                        likeUrl = str(weibo.xpath('./div[last()]/a[last()-3]/@href')[0])
                        responseText = self.commonRequest(likeUrl)
                        print "auto like http result {0}".format(responseText)
                except urllib2.HTTPError as e:
                    print e

            # print result
            # jsonText = json.dumps(weiboResults, ensure_ascii=False)
            print "{0} hot twitters in total".format(str(len(weiboResults)))
            self.writeJsonToFile(weiboResults, savePath)

        except urllib2.HTTPError as e:
            print e

    def loadCookie(self, path):
        with open(path, 'r') as f:
            cookie = f.read()
            self._header["Cookie"] = cookie

    def commonRequest(self, url):
        request = urllib2.Request(url=url, headers=self._header)
        response = urllib2.urlopen(request)
        return response.read()

    def writeJsonToFile(self, results, filepath):
        with io.open(filepath, 'w', encoding='utf8') as file_object:
            file_object.write(json.dumps(results, ensure_ascii=False).decode("utf8"))

            # hot twitters
            # def showHotBlogs(self, url):
            #     try:
            #         request = urllib2.Request(url=url, headers=self._header)
            #         response = urllib2.urlopen(request)
            #         html = response.read()
            #         selector = etree.HTML(html)
            #         # 获取页面控件
            #         pageNum = int(selector.xpath('//input[@name="mp"]')[0].attrib['value']);
            #         util = utils();
            #         weiboResults = [];
            #         for page in range(1, pageNum + 1):
            #             url = url + "?page=" + str(page);
            #             response = urllib2.urlopen(request)
            #             html = response.read()
            #             util.analysisHtml(html, weiboResults);
            #         # print result
            #         jsonText = json.dumps(weiboResults, ensure_ascii=False)
            #         print jsonText
            #     except urllib2.HTTPError as e:
            #         print (e.code)


if __name__ == "__main__":
    lanunch = LauncherForMobile();
    lanunch.showSomeBlogs("https://weibo.cn/u/1971787603", "/Users/lichao/Desktop/weibo/cookie/cookie.txt",
                          "/Users/lichao/Desktop/weibo/result.json");
