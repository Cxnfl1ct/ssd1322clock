from luma.core.interface.serial import spi
from luma.core.render import canvas
from PIL import ImageFont
from luma.oled.device import ssd1322
import time, os
import guitypes, config

serial = spi(device=0, port=0)
device = ssd1322(serial, 256, 64, 2, "RGB", "full_frame")

shadow = config.shadow
drawBg = config.drawBackground
background = config.background
colorFg = config.colorForeground
colorBg = config.colorBackground
colorBg2 = config.colorBackground2
colon = config.colonSign
clockX = config.clockX
clockY = config.clockY
colonX = config.colonX
colonY = config.colonY
colonSpace1 = config.colonSpace1
clockSpace1 = config.clockSpace1
clockSpace2 = config.clockSpace2
tz = config.timezone
font, fontsize = (config.font, config.fontsize)

if font != None:
    font = ImageFont.truetype(font, fontsize)

i = 0

def init():
    device.clear()
    device.show()

def get_aligning(mode, val):
    if mode == 0:
        return 0
    if mode == 1:
        return val // 2
    if mode == 2:
        return val

def get_decode_time():
    epoch = time.time() // 1
    epochday = epoch % 86400
    h  = epochday // 3600
    t1 = epochday %  3600
    m  = t1 // 60
    s  = t1 %  60
    return h, m, s

def zeroFill(num, zerocnt):
    zerostr = ""
    finalstr = ""
    numlen = len(str(num))
    zerolen = zerocnt - numlen

    if zerolen <= 0:
        return num

    for i in range(zerolen):
        zerostr = zerostr + "0"

    finalstr = zerostr + str(num)
    return finalstr

def localizeTime(hr, mn, sc):
    h, m, mr, acc = (0, 0, 0, 0)

    if tz % 1 == 0.5:
        mr = mn + 30
    else:
        mr = mn

    m = mr % 60
    acc = mr // 60
    h = (hr + (tz // 1) ) + acc % 24

    return int(h), int(m), int(sc // 1)

def drawbg(canv, color, color2):
    cntx = 256 // 3
    for i in range(cntx):
        canv.line([(i*5-128, 64), (i*5-64, 0)], fill=color, width=1)
        canv.line([(i*5, 65), (i*5-64, 1)], fill=color2, width=1)


def drawText(x, y, size, txt, color, canv, shadow, alignx, aligny, fnt):
    if shadow == True:
        drawText(x+1, y+1, size, txt, 0, canv, False, alignx, aligny, fnt)

    a, b, c, d = canv.textbbox((x, y), align="center", text=txt, font_size=size, font=fnt)
    sx = c-a
    sy = d-b
    px = get_aligning(alignx, sx)
    py = get_aligning(aligny, sy)
    canv.text((x-px, y-py), align="center", text=txt, fill=color, font_size=size, font=fnt)

def getClockCoords(clockx, clsp1, clsp2, colonx, cosp1):
    return (clockx, clockx+clsp1, clockx+clsp1+clsp2, colonx, colonx+cosp1)

hs, ms, ss = ("", "", "")
init()

while True:
    try:
        h, m, s = get_decode_time()
        hl, ml, sl = localizeTime(h, m, s)

        hs = str(zeroFill(hl, 2))
        ms = str(zeroFill(ml, 2))
        ss = str(zeroFill(sl, 2))

        with canvas(device) as draw:
            if drawBg:
                if background == 1:
                    drawbg(draw, colorBg, colorBg2)
                elif background == 2:
                    draw.rectangle(device.bounding_box, outline=colorBg2, fill=colorBg, width=3)

            cx1, cx2, cx3, clx1, clx2 = getClockCoords(clockX, clockSpace1, clockSpace2, colonX, colonSpace1)
            drawText(cx1, clockY, fontsize, hs, colorFg, draw, shadow, 1, 1, font)
            drawText(cx2, clockY, fontsize, ms, colorFg, draw, shadow, 1, 1, font)
            drawText(cx3, clockY, fontsize, ss, colorFg, draw, shadow, 1, 1, font)
            drawText(clx1, colonY, fontsize, colon, colorFg, draw, shadow, 1, 1, font)
            drawText(clx2, colonY, fontsize, colon, colorFg, draw, shadow, 1, 1, font)

            time.sleep(0.1)
    except KeyboardInterrupt:
        exit()

time.sleep(120)
