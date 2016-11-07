# -*- coding=utf-8 -*-

'''
获取网页图片，识别图片文字，匹配字典。
'''

import os
import json
import time
import jieba
import Queue
import urllib
import hashlib
import urllib2
import requests
import urlparse
import tldextract
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from selenium import webdriver
from shutil import rmtree
import ImageProcessing_     #TODO
import sensitive_words


class OCR():
    def __init__(self):
        pass
    
    def getScreenshot(self,url):
        save_to_file = 'screenshot.jpg'
        access_key = "b1da900243d8551000dabfa9074491bf"
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


    def extractImagesFromSource(self,url,src):
        out_folder = 'imgDL'
        image_list = []
        ext = tldextract.extract(url)
        pool = ThreadPool(processes=10)     #多线程下载
        q = Queue.Queue()                   #多线程下载

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


        soup = BeautifulSoup(src, 'html.parser')     
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
                print "Some error between line 92-100 when getting ",image,": ",e
                continue
            try:
                valid_suffix = ['.jpg','.png','.gif','.bmp','.svg']
                for i in valid_suffix:
                    if image_url.endswith(i):
                        #print image_url
                        async_result = pool.apply_async(downloadToFile, (image_url,filePath)) 
                        q.put((filePath,async_result))
                        image_list.append(filePath)
            except Exception as e:
                print "download Image Exception : ",e
                pass
                        
        while not q.empty():
                c = q.get()
                filePath=c[0]
                size = c[1].get()
                print (filePath,size)
                if size < 10000 or size > 5242880:      # 删除不合格的文件
                    os.unlink(filePath)
                    image_list.remove(filePath)

        return set(image_list)


    def extractWords(self,filePath):
       # print "extracting word from :",filePath
        default_inputfile = filePath
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
        try:
            imageurl = tempdict['imageUploadResultList'][0]['imageUrl']
        except:
            pass
        else:
            detection_url = 'http://aligreen.alibaba.com/rpc/image/detect.json'
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
            print "type of final >> ",type(final_list)
            print "final_list >> ",final_list
            return set(final_list)

    def categorizeResult(self, target):
        c = {i:[] for i in sensitive_words.kd}
       # print "Final Keywords:",target
        for i in sensitive_words.kd:
            for j in target:
                for t in sensitive_words.kd[i]:
                    if j == t.decode('utf-8'):
                        c[i].append(j)
        biggest_size = 0
        category = u'未检出异常'
        for l in c:
            if len(c[l])> biggest_size:
                category=l.decode('utf-8')
        #print category
        return category

    def run(self,url,src):
        ocr_result = set([])
        li = self.extractImagesFromSource(url,src)
        for image in li:
            extracted = self.extractWords(image)
            print "current Image >> ",image
            print "current ocr_Result >> ", type(ocr_result),ocr_result
            print "current extracted >> ", type(extracted),extracted
            ocr_result = ocr_result | extracted
        return self.categorizeResult(ocr_result)
    
    def clean(self,url):
        out_folder = 'imgDL'
        ext = tldextract.extract(url)
        folder_to_save = ext[1]
        rmtree(os.path.join(out_folder,folder_to_save))


if __name__ == '__main__':
    url="http://hjt2hjm.hhhtgs.gov.cn/xinwen9/20161106/43917657/sitemap.xml"
    url="http://www.s368.net"
    body = urllib.urlopen(url).read()
    cur = OCR()
    print cur.run(url,body)
    cur.clean(url)
