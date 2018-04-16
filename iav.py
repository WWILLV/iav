# -*- coding: UTF-8 -*-
__author__ = 'WILL_V'
import urllib.request
import urllib.parse
import json
import re
import sys,getopt
from bs4 import BeautifulSoup

proxy_addr = "127.0.0.1:10808"

def getPreview(avid):
    '''avgle.com获取预览视频'''
    AVGLE_SEARCH_JAV_API_URL = 'https://api.avgle.com/v1/jav/{}/{}?limit={}'
    url = AVGLE_SEARCH_JAV_API_URL
    query = avid
    page = 0
    limit = 2
    proxy = urllib.request.ProxyHandler({'https': proxy_addr})
    opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    response = json.loads(
        urllib.request.urlopen(url.format(urllib.parse.quote_plus(query), page, limit)).read().decode())
    # print(response)
    if response['success']:
        videos = response['response']['videos']
        print("avgle返回的videos为：")
        if (videos!=[]):
            print(videos[0]["title"])
            return videos[0]["preview_video_url"]
        else:
            return "SUCCESS,BUT NOT GET"
    else:
        return "FAIL"

def btso(avid):
    '''获取btso的磁力链接'''
    url = 'https://btso.pw/search/'+avid
    proxy = urllib.request.ProxyHandler({'https': proxy_addr})
    opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    opener.addheaders = [
        ('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36')
    ]
    urllib.request.install_opener(opener)
    soup=BeautifulSoup(urllib.request.urlopen(url).read().decode('utf-8'),'lxml')
    listAll=soup.prettify()
    pattern = re.compile(r'https://btso.pw/magnet/detail/hash/.*?" title=".*?"')
    match = pattern.findall(listAll)
    if match:
        print('以下数据来自btso.pw：')
        for i in match:
            i=i.replace('https://btso.pw/magnet/detail/hash/','magnet:?xt=urn:btih:')
            print(i.replace('" ',' '))
    else:
        print('没有在btso.pw发现',avid,'的数据')

''' javbus获取磁力链接的ajax请求
GET /ajax/uncledatoolsbyajax.php?gid=26445925072&lang=zh&img=https://pics.javbus.com/cover/4lqn_b.jpg&uc=0&floor=653 HTTP/1.1
Host: www.javbus.com
Connection: close
Accept: */*
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36
Referer: https://www.javbus.com/HODV-21033
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,zh-TW;q=0.8
Cookie: 

'''

def getAjax(avid):
    '''获取javbus的ajax'''

    url='https://www.javbus.com/'+avid
    proxy = urllib.request.ProxyHandler({'https': proxy_addr})
    opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    opener.addheaders = [
        ('User-Agent',
         'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'),
        ('Host','www.javbus.com'),
        ('Connection','close'),
        ('X-Requested-With','XMLHttpRequest'),
        ('Referer',url)
    ]
    urllib.request.install_opener(opener)
    soup = BeautifulSoup(urllib.request.urlopen(url).read().decode('utf-8'), 'lxml')
    html=soup.prettify()

    '''获取img'''
    img_pattern = re.compile(r"var img = '.*?'")
    match = img_pattern.findall(html)
    img=match[0].replace("var img = '","").replace("'","")
    print('封面为',img)

    '''获取uc'''
    uc_pattern = re.compile(r"var uc = .*?;")
    match = uc_pattern.findall(html)
    uc = match[0].replace("var uc = ", "").replace(";","")

    '''获取gid'''
    gid_pattern = re.compile(r"var gid = .*?;")
    match = gid_pattern.findall(html)
    gid = match[0].replace("var gid = ", "").replace(";","")

    '''获取ajax'''
    ajax="https://www.javbus.com/ajax/uncledatoolsbyajax.php?gid="+gid+"&lang=zh&img="+img+"&uc="+uc
    return ajax

def javbus(avid):
    '''获取javbus的磁力链接'''

    url=getAjax(avid)
    proxy = urllib.request.ProxyHandler({'https': proxy_addr})
    opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    opener.addheaders = [
        ('User-Agent',
         'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'),
        ('Host','www.javbus.com'),
        ('Connection','close'),
        ('X-Requested-With','XMLHttpRequest'),
        ('Referer',url)
    ]
    urllib.request.install_opener(opener)
    soup = BeautifulSoup(urllib.request.urlopen(url).read().decode('utf-8'), 'lxml')

    avdist={'title':'','magnet':'','size':'','date':''}

    for tr in soup.find_all('tr'):
        i=0
        for td in tr:
            if(td.string):
                continue
            i=i+1
            avdist['magnet']=td.a['href']
            if (i%3 == 1):
                avdist['title'] = td.a.text.replace(" ", "").replace("\t", "").replace("\r\n","")
            if (i%3 == 2):
                avdist['size'] = td.a.text.replace(" ", "").replace("\t", "").replace("\r\n","")
            if (i%3 == 0):
                avdist['date'] = td.a.text.replace(" ", "").replace("\t", "").replace("\r\n","")
        print(avdist)

def main(argv):
    print('搜索注意按标准书写番号（如BGN-044）\n')
    try:
        opts, args = getopt.getopt(argv, "hb:s:v:", ["javbus=", "bt=","vp=="])
    except getopt.GetoptError:
        print('''
        搜索注意按标准书写番号（如BGN-044）
        注意扶梯子
        在Javbus上搜索（返回字典）iav.py -b 番号
        在btso上搜索（返回磁链）iav.py -s 番号
        在avgle上搜索预览视频 iav.py -v 番号
        ''')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('''
            搜索注意按标准书写番号（如BGN-044）
            注意扶梯子
            在Javbus上搜索（返回字典）iav.py -b 番号
            在btso上搜索（返回磁链）iav.py -s 番号
            在avgle上搜索预览视频 iav.py -v 番号
            ''')
            sys.exit()
        elif opt in ("-b", "--javbus"):
            avid = arg
            javbus(avid)
        elif opt in ("-s", "--bt"):
            avid = arg
            btso(avid)
        elif opt in ("-v", "--vp"):
            avid = arg
            print(getPreview(avid))

if __name__ == '__main__':
    main(sys.argv[1:])