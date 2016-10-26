# coding=utf-8
import os
import urlparse
import tldextract
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

domain = 'http://www.dd164.com'
print 0

headers = { 'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'en-US,en;q=0.8',
    'Cache-Control':'max-age=0',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
}
for key, value in headers.iteritems():
        webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value

driver = webdriver.PhantomJS('/home/v/Installers/phantomjs',service_args=['--load-images=no','--disk-cache=no','--proxy=10.0.3.33:8888','--proxy-type=http','--ignore-ssl-errors=true'])
#driver = webdriver.PhantomJS('/home/v/Installers/phantomjs',service_args=['--load-images=yes','--disk-cache=no','--ignore-ssl-errors=true'])

driver.get(domain)
print 1
#driver.implicitly_wait(60)
driver.set_page_load_timeout(60)  ##设置超时时间
driver.set_window_size(1440, 900)
print 2
src = driver.page_source
#print src
soup = BeautifulSoup(src, 'html.parser')
parsed = list(urlparse.urlparse(domain))
out_folder = './imgDL'



for image in soup.findAll("img"):
    print "Image: %(src)s" % image
    image_url = urlparse.urljoin(domain, image['src'])
    filename = image["src"].split("/")[-1]
    domainFolder = tldextract.extract(domain)[1]
    outFilePath = os.path.join(out_folder,domainFolder, filename)
    outFolderPath = os.path.join(out_folder,domainFolder)
    if not os.path.exists(outFolderPath):
        os.makedirs(outFolderPath)
    
    session = requests.Session()
    cookies = driver.get_cookies()
    for cookie in cookies: 
        session.cookies.set(cookie['name'], cookie['value'])
    response = session.get(image_url)
    with open(outFilePath,'w') as d:
        d.write(response.content)
driver.quit()

# a = set([u'娱乐城','葡京','c'])
# b = set([])
# with open('OCR/sensitive_words.txt','r') as f:
#     for i in f.readlines():
#         b.add(i)
# print a.intersection(b)