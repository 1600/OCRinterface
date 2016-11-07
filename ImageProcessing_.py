import os
from PIL import Image

def bConvert(li):
    for i in li:
        try:
            print i
            convertToJPG(i)
        except Exception as e:
            print "convert error >> ",e
            pass


def convertToJPG(file):
    im = Image.open(file)
    try:
        print "try RGB"
        bg = Image.new("RGB", im.size, (255,255,255))
        bg.paste(im,im)
    except:
        print "try RGBA"
        bg = Image.new("RGBA", im.size, (255,255,255,255))
        bg.paste(im,(0,0),im)
    bg.save(file+'.jpg')
    os.unlink(file)
