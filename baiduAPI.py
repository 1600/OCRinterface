# -*- coding=utf-8 -*-

from Crypto.Hash import HMAC, SHA256
import time

ak = '409c17537b9b4b37aab4a5fc8a550383'
sk = '05989fc6ee9a47e9b715eec9d046629d'
canonical_header = '''
POST /v1/recognize/text HTTP/1.1
accept-encoding: gzip, deflate
x-bce-date: {0}
connection: keep-alive
accept: */*
host: ocr.bj.baidubce.com
content-type: application/json
'''
# authorization: bce-auth-v1/46bd9968a6194b4bbdf0341f2286ccce/2015-03-24T13:02:00Z/1800/host;x-bce-date/994014d96b0eb26578e039fa053a4f9003425da4bfedf33f4790882fb4c54903

timepoint = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def hmac_sha256(key, msg):
    # hash_obj = HMAC.new(key=key, msg=msg, digestmod=SHA256)
    # return hash_obj.hexdigest()
    b = HMAC.new(key, digestmod=SHA256)
    #b.update(b'secret text')
    b.update(msg)
    print b.hexdigest()
    return b.hexdigest()

def getCanonicalReq():
    t = canonical_header.format(timepoint)
    return t

def getSigningKey():
    a = 'bce-auth-v1/{0}/{1}/1800'
    a = a.format(ak,timepoint)
    return hmac_sha256(sk,a)

def getSignature():
    return hmac_sha256(getSigningKey(),getCanonicalReq())

def getAuthString():
    z = '''authorization: bce-auth-v1/{0}/{1}/1800/host;x-bce-date/{2}'''
    z = z.format(ak,timepoint,getSignature())
    return z

def finalizeHeader():
    y = getCanonicalReq()
    x = getAuthString()
    return y+x

print finalizeHeader()