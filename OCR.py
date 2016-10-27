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
from PIL import Image

class OCR():
    def __init__(self):
        pass
    
    def getScreenshot(self,url):
        # target = 'http://www.10xxoo.com/'
        target = url
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
    
    def getScreenShot(self,domain):
        driver = webdriver.PhantomJS('/home/v/Installers/phantomjs',service_args=['--load-images=yes','--disk-cache=no'])
        driver.get(domain)
        driver.implicitly_wait(60)
        driver.set_page_load_timeout(60)  ##设置超时时间
        driver.set_window_size(1440, 900)
        driver.save_screenshot('out.png')
        driver.quit()
    
    def extractImagesFromPage(self,url):        # 内有相对路径
        out_folder = './imgDL'
        # url = 'https://www.dd164.com'

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
        driver.set_page_load_timeout(50)  ##设置超时时间
        driver.set_window_size(1440, 900)
        try:
            driver.get(url)
        except Exception,e:
            print "When getting url, exception happened:",e
            driver.save_screenshot('getURLexception.png')
        src = driver.page_source
        soup = BeautifulSoup(src, 'html.parser')

        folder_to_save = ext[1]
        outFolderPath = os.path.join(out_folder,folder_to_save)
        if not os.path.exists(outFolderPath):
            os.makedirs(outFolderPath)
        for image in soup.findAll("img"):
            try:
                image_url = urlparse.urljoin(url, image['src'])
                print "image_url >> ",image_url
                temp1 = "_".join(image["src"].split("/"))
                m = hashlib.md5()
                m.update(temp1)
                filename=m.hexdigest()+image["src"].split("/")[-1]
                print filename
                folder_to_save = ext[1]
                OutFilePath = os.path.join(out_folder,folder_to_save, filename)
            except Exception as e:
                print "Some error between line 66-74 when getting ",image,": ",e
                pass
            try:
                session = requests.Session()
                cookies = driver.get_cookies()
                for cookie in cookies: 
                    session.cookies.set(cookie['name'], cookie['value'])
                response = session.get(image_url,timeout=(5,10))    # connect_timeout, load_timeout
                roughsize = 0
                print "saving url:",image_url
                with open(OutFilePath,'wb') as fd:   # using b(binary mode) to write image content.
                    for chunk in response.iter_content(1024):
                        roughsize += 1024
                        if roughsize > 5242880:
                            break
                        fd.write(chunk)             # 分片写入
                if roughsize < 10000 or roughsize > 5242880:
                    os.unlink(OutFilePath)
                    print filename ," roughsize is: ",roughsize," not qualified, deleted."
            except Exception as e:
                print "Get Image Exception : ",e
                pass
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
    a.extractImagesFromPage('http://www.qgs-china.com')