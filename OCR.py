# -*- coding=utf-8 -*-
import os
import json
import time
import jieba
import urllib
import hashlib
import urllib2
import requests
import urlparse
import tldextract
from bs4 import BeautifulSoup
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from selenium import webdriver
from shutil import rmtree
import ImageProcessing_
import sensitive_words


class OCR():
    def __init__(self):
        pass
    
    def getScreenshot(self,url):        #TODO replace this with a solely-project-wise api account.
        save_to_file = 'screenshot.jpg'
        access_key = ""
        viewport_big = '1440x900'
        viewport_small = '414x736'
        is_fullpage = '1'
        output_format = 'jpg'
        def calcSecret(target):
            a = hashlib.md5()
            a.update(target+"mountainlion")
            return a.hexdigest()
        secret_key = calcSecret(url)
        screenshot_url = "http://api.screenshotlayer.com/api/capture?access_key="+access_key+"&secret_key="+secret_key+"&url="+urllib.quote_plus(url)+"&viewport="+viewport_small+"&fullpage="+is_fullpage+"&format="+output_format
        return screenshot_url

    def extractImagesFromPage(self,url):        # 内有相对路径
        out_folder = './imgDL'
        image_list = []
        ext = tldextract.extract(url)
        def downloadToFile(url,targetPath,cookies=None):
            print "Entering downloadToFile, loadtimeout=10,fetching...",url
            session = requests.Session()
            if cookies:
                for cookie in cookies: 
                    session.cookies.set(cookie['name'], cookie['value'])
            response = session.get(url,timeout=(5,10))    # connect_timeout, load_timeout
            roughsize = 0
            with open(targetPath,'wb') as fd:   # using b(binary mode) to write image content.
                for chunk in response.iter_content(1024):
                    roughsize += 1024
                    if roughsize > 5242880:
                        break
                    fd.write(chunk)             # 分片写入
            return roughsize

        def fetchSource(url):
            print "Entering fetchSource, loadtimeout=30, fetching...",url
            ext = tldextract.extract(url)
            domain = '.'.join(ext)
            headers = {
                'Host':domain,
                'Accept':'*/*',
                'Cache-Control':'max-age=0',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
            }
            service_arglist=[
                '--load-images=no',
                '--disk-cache=no',
                '--ignore-ssl-errors=true'
            ]
            for key, value in headers.iteritems():
                    webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value
            driver = webdriver.PhantomJS('/home/v/Installers/phantomjs',service_args=service_arglist)
            driver.implicitly_wait(10)
            driver.set_page_load_timeout(30)   ##设置超时时间
            driver.set_window_size(1440, 900)
            try:
                driver.get(url)                 # get url source
                src = driver.page_source
            except Exception,e:
                print "When getting url, exception happened:",e
                return 'Error'
            driver.quit()
            return src

        soup = BeautifulSoup(fetchSource(url), 'html.parser')     # used fetchSource
        folder_to_save = ext[1]
        outFolderPath = os.path.join(out_folder,folder_to_save)
        if not os.path.exists(outFolderPath):
            os.makedirs(outFolderPath)
        for image in soup.findAll("img"):
            try:
                image_url = urlparse.urljoin(url, image['src'])
                if image_url in image_list:
                    continue
                temp1 = "_".join(image["src"].split("/"))
                m = hashlib.md5()
                m.update(temp1)
                filename=m.hexdigest()+image["src"].split("/")[-1]
                folder_to_save = ext[1]
                filePath = os.path.join(out_folder,folder_to_save, filename)
            except Exception as e:
                #print "Some error between line 92-100 when getting ",image,": ",e
                continue
            try:
                size = downloadToFile(image_url,filePath)      # used downloadToFile
                image_list.append(filePath)
                if size < 10000 or size > 5242880:      # 删除不合格的文件
                    os.unlink(filePath)
                    image_list.remove(filePath)
            except Exception as e:
                print "download Image Exception : ",e
                pass
        if image_list == []:
            filePath = os.path.join(out_folder,folder_to_save,'screenshot.jpg')
            downloadToFile(self.getScreenshot(url),filePath)
            image_list.append(filePath)
        return set(image_list)

    def extractWords(self,filePath):
        print "extracting word from :",filePath
        default_inputfile = filePath
        datagen, headers = multipart_encode({"imageFile": open(default_inputfile, "rb")})
        headers['Host']='1'
        headers['Connection']='keep-alive'
        headers['Accept']='application/json, text/javascript, */*; q=0.01'
        headers['Origin']='http://aligreen.alibaba.com'
        headers['X-Requested-With']='XMLHttpRequest'
        headers['Accept-Encoding']='gzip, deflate'
        headers['Accept-Language']='zh-CN,zh;q=0.8'
        headers['User-Agent']='Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
        register_openers()
        request = urllib2.Request("http://1.json", datagen, headers)
        upload_result = urllib2.urlopen(request).read()
        #print upload_result
        tempdict = json.loads(upload_result)
        imageurl = tempdict['imageUploadResultList'][0]['imageUrl']
        detection_url = 'http://2.json'
        payload = {'imageUrls[]': imageurl, 'scene': 'ocr'}
        headers = {'Host':'aligreen.alibaba.com','Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Content-Length': '2'}
        r = requests.post(detection_url,data=payload)
        #print r.text
        try:
            sentence = json.loads(r.text)[0]['images'][0]['ocr']['text'][0]
        except:
            return set([])
        temp = '/'.join(jieba.cut(sentence))
        words = temp.split("/"),type(temp.split("/"))
        final_list = []
        for i in words[0]:
            if len(i) <= 1:
                continue
            if i in final_list:
                continue
            final_list.append(i)
        return set(final_list)

    def categorizeResult(self, target):
        c = {i:[] for i in sensitive_words.kd}
        print "Final Keywords:",target
        for i in sensitive_words.kd:
            for j in target:
                for t in sensitive_words.kd[i]:
                    if j == t.decode('utf-8'):
                        c[i].append(j)
        biggest_size = 0
        category = u''
        for l in c:
            if len(c[l])> biggest_size:
                biggest=l.decode('utf-8')
        print biggest
        return category

    def run(self,url):
        ocr_result = set([])
        li = self.extractImagesFromPage(url)
        for image in li:
            extracted = self.extractWords(image)
            ocr_result = ocr_result | extracted
        return self.categorizeResult(ocr_result)
    
    def clean(self,url):
        out_folder = './imgDL'
        ext = tldextract.extract(url)
        folder_to_save = ext[1]
        rmtree(os.path.join(out_folder,folder_to_save))


if __name__ == '__main__':
    a = OCR()
    print a.run('http://1.net')
    a.clean('http://1.net')
