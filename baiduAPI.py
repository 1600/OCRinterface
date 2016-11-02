# -*- coding=utf-8 -*-

from Crypto.Hash import HMAC, SHA256
import time

ak = ''
sk = ''
canonical_header = '''
POST /v1/recognize/text HTTP/1.1
accept-encoding: gzip, deflate
x-bce-date: {0}
connection: keep-alive
accept: */*
host: ocr.bj.baidubce.com
content-type: application/json
'''

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
