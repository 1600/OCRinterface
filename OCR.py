# -*- coding=utf-8 -*-
import os
import json
import time
import jieba
import urllib
import hashlib
import urllib2
import requests
import tldextract
from bs4 import BeautifulSoup
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from selenium import webdriver
from PIL import Image

class OCR():
    def __init__(self):
        pass
    
    def getScreenshot(self):
        target = 'http://www.10xxoo.com/'
        save_to_file = 'screenshot.jpg'
        access_key = "b1da900243d8551000dabfa9074491bf"
        viewport = '1440x900'
        is_fullpage = '1'
        output_format = 'jpg'
        def calcSecret(target):
            a = hashlib.md5()
            a.update(target+"mountainlion")
            return a.hexdigest()
        secret_key = calcSecret(target)
        urllib.urlretrieve("http://api.screenshotlayer.com/api/capture?access_key="+access_key+"&secret_key="+secret_key+"&url="+urllib.quote_plus(target)+"&viewport="+viewport+"&fullpage="+is_fullpage+"&format="+output_format,save_to_file)
        return save_to_file
    
    def getImageFile(self,domain):
        driver = webdriver.PhantomJS('/home/v/Installers/phantomjs',service_args=['--load-images=yes','--disk-cache=no'])
        driver.get(domain)
        driver.implicitly_wait(60)
        driver.set_page_load_timeout(60)  ##设置超时时间
        driver.set_window_size(1440, 900)
        driver.save_screenshot('out.png')
        driver.quit()
    
    def extractImages(self,domain):
        driver = webdriver.PhantomJS('/home/v/Installers/phantomjs',service_args=['--load-images=yes','--disk-cache=no'])
        driver.get(domain)
        driver.implicitly_wait(60)
        driver.set_page_load_timeout(60)  ##设置超时时间
        driver.set_window_size(1440, 900)
        with open(tldextract.extract(domain)[1]+'.html','w') as f:
            f.write(driver.page_source.encode('utf-8'))

        driver.set_page_load_timeout(60)  ##设置超时时间
        driver.set_window_size(1440, 900)
        driver.save_screenshot('out.png')
        driver.quit()

    def PNGtoJPG(self,file):
        # generate an 'out.jpg'
        im = Image.open(file)
        bg = Image.new("RGB", im.size, (255,255,255))
        bg.paste(im,im)
        bg.save('out.jpg')
        os.remove(file)
    
    def extractWords(self):
        default_inputfile = 'out.jpg'
        datagen, headers = multipart_encode({"imageFile": open(default_inputfile, "rb")})
        headers['Host']='aligreen.alibaba.com'
        headers['Connection']='keep-alive'
        headers['Accept']='application/json, text/javascript, */*; q=0.01'
        headers['Origin']='http://aligreen.alibaba.com'
        headers['X-Requested-With']='XMLHttpRequest'
        headers['Accept-Encoding']='gzip, deflate'
        headers['Accept-Language']='zh-CN,zh;q=0.8'
        headers['Cookie']='cna=6c9rEM7A8W0CAbeB2ukCuutX; l=AmtrPA8gwLaNmLmcW7nvXzBMe4VXhn8C; isg=Am9vM74Oa-OMeG_fwI48Af5s_oMVAuQaV5JRi4H-DV7l0I7SieBphhXGJHeU'
        headers['User-Agent']='Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
        register_openers()
        request = urllib2.Request("http://aligreen.alibaba.com/rpc/image/upload_image.json", datagen, headers)
        upload_result = urllib2.urlopen(request).read()
        print upload_result
        tempdict = json.loads(upload_result)
        imageurl = tempdict['imageUploadResultList'][0]['imageUrl']
        # Detection-----------------------------------------------------------
        detection_url = 'http://aligreen.alibaba.com/rpc/image/detect.json'
        payload = {'imageUrls[]': imageurl, 'scene': 'ocr'}
        headers = {'Host':'aligreen.alibaba.com','Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Content-Length': '2'}
        r = requests.post(detection_url,data=payload)
        print "r.text:--------------"
        print r.text
        sentence = json.loads(r.text)[0]['images'][0]['ocr']['text'][0]
        temp = '/'.join(jieba.cut(sentence))
        words = temp.split("/"),type(temp.split("/"))
        print words
        return words

    def categorizeResult(self, target):
        a = set(target)
        b = set([])
        with open('sensitive_words.txt','r') as f:
            for i in f.readlines():
                b += i
        print len(a.intersection(b))
        



if __name__ == '__main__':
    #time.sleep(0.1)
    #OCR().extractWords()
    # OCR().getScreenshot()
    # OCR().categorizeResult()
    a = OCR()
    a.extractImages('http://github.com')