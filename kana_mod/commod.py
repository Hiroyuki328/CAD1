import math, re, collections
import numpy as np
import unicodedata

dic = {}    # 部材ディクショナリ作成
dic0 = {}
keylst = []
dats = []
f = open("C:/jww/見積諸元データ/見積諸元データ.txt")
dats = f.readlines()
f.close()
for ele in dats:
    if len(ele) > 1:
        dat = ele.rstrip("\n").split(" = ")
        dic0 = {dat[0]: dat[1]}
        dic = {**dic, **dic0}
window_vol = len([ke for ke in dic.keys() if ("窓" in ke)])     # 建具連番数量
turido_vol = len([ke for ke in dic.keys() if ("吊り戸" in ke)])
shutter_vol = len([ke for ke in dic.keys() if ("軽量シャッター" in ke)])
idoushutter_vol = len([ke for ke in dic.keys() if ("移動中柱付きシャッター" in ke)])
door_vol = len([ke for ke in dic.keys() if ("框ドア" in ke)])
OS_vol = len([ke for ke in dic.keys() if ("オーバースライダー" in ke)])

xlen = float(dic["妻方向柱芯全長"])
ylen = float(dic["軒方向柱芯全長"])
nh = float(dic["軒高"])
slp = dic["屋根勾配"].split("/")
slope = float(slp[0])/float(slp[1])
ybrsnum = float(dic["屋根ブレース段数"])

c1 = dic["柱"]
g1 = dic["梁"]
m1 = dic["間柱"]
b1 = dic["入口梁"]
j1 = dic["継梁"]
nk = dic["軒先"]
h1 = dic["方杖"]
ybrs = dic["屋根ﾌﾞﾚｰｽ"]
kbrs = dic["壁ﾌﾞﾚｰｽ"]
moya = dic["母屋"]
dobuti = dic["胴縁"]

base = dic["基礎"]
yuka = dic["床"]
yane = dic["屋根"]
kabe = dic["壁"]
try:
    sitaji = dic["屋根下地"]
except KeyError:
    sitaji = "なし"
    sitaji_t = 0

if sitaji == "なし":
    sitaji_t = 0
else:
    sitaji_t = float(dic["屋根下地厚"])
h1pos = float(dic["方杖位置"])
tnt = float(dic["C1天板厚"])
base_t = float(dic["BPL厚"])
nokilen = float(dic["軒先長"])
yane_t = float(dic["屋根材厚"])
kabe_t = float(dic["壁材厚"])
gl = float(dic["G.L"])
fl = float(dic["F.L"])
moyapitch = float(dic["母屋ピッチ"])
dobutipitch = float(dic["胴縁ピッチ"])
pitch = float(dic["壁ハッチングピッチ"])
ypitch = float(dic["屋根ハッチングピッチ"])
moyaclr = float(dic["母屋浮かし長"])
dobuticlr = float(dic["胴縁浮かし長"])
#--------------------
r = math.atan(slope)
mc = list(map(float, c1[2:].split("x")))
mg = list(map(float, g1[2:].split("x")))
mn = list(map(float, nk[2:].split("x")))
mm = list(map(float, m1[2:].split("x")))
mmoya = list(map(float, moya[2:].split("x")))
mdobuti = list(map(float, dobuti[2:].split("x")))
if base[:2] == "束石":
    basespec = base.split(",")[1]
    mbase = list(map(lambda i: float(i[1:]), basespec.split("x")))
    kisoh = mbase[1]
    base = base.replace(",", "")
    pass
else:   # 布基礎
    basespec = base.split(",")[1]
    mbase = list(map(lambda i: float(i[1:]), basespec.split("x")))
    kisoh = mbase[1] + mbase[3]
    base = "布基礎"

cw = mc[0]; cd = mc[1]
gw = mg[0]; gd = mg[1]
nw = mn[0]; ng = mn[1]
mw = mm[0]; md = mm[1]
if moya[0] == "木":
    moyaw = mmoya[0]; moyah = mmoya[1]
else:
    moyaw = mmoya[1]; moyah = mmoya[0]    
if dobuti[0] == "木":
    dobutiw = mdobuti[0]; dobutih = mdobuti[1]
else:
    dobutiw = mdobuti[1]; dobutih = mdobuti[0]

hafuyakuw = [220, 230] if moyaw + nw + sitaji_t > 181 else [180, 190]
hafut = 24 if moyaw + nw + sitaji_t > 181 else 18
ry = cw/2 * math.tan(r)
grw = gw/2/math.cos(r)
crw = cw/1/math.cos(r)
nrw = nw/1/math.cos(r)
dtn = tnt*math.sin(r)
initP = []
endP = []
talst = [0]; tblst = [0]; t1lst = [0]; telst = [0]
#---------------------------

def torilist(toriname): # 各通り芯間内訳
    tlist = [0]; intg = 0
    eles = dic[toriname].split(",")
    for ele in eles:
        if ("x" in ele):
            el = ele.split("x")
            cnt = int(el[1])
            lth = int(el[0])
            while cnt > 0:
                intg = intg + lth
                tlist.append(intg)
                cnt -= 1
        else:
            intg = intg + int(ele)
            tlist.append(intg)
    return tlist

toriA = torilist("柱芯間A通り")
toriB = torilist("柱芯間B通り")
tori1 = torilist("柱芯間1通り")
toriE = torilist("柱芯間E通り")
toriNum = torilist("通り番付")
torivol = len(toriNum)

figs = []
figs2 = []
figs3 = []
f = open("C:/jww/部材リスト/鋼材データ.txt")
figs = f.readlines()
f.close()
f = open("C:/jww/部材リスト/図形_スプライスWPL.txt")
figs2 = f.readlines()
f.close()
figs += figs2
f = open("C:/jww/部材リスト/図形_スプライスFPL.txt")
figs3 = f.readlines()
f.close()
figs += figs3
f = open("C:/jww/部材リスト/建具図形.txt")
tategufigs = f.readlines()
f.close()
figs += tategufigs
f = open("C:/jww/部材リスト/図面枠A3.txt")
A3figs = f.readlines()
f.close()
figs += A3figs

def getFig(figname):
    for fname in figs:
        if fname == figname:
            idx = int(figs.index(fname) + 2)
            elements = []
            while figs[idx] != "\n":
                cmd = "L" if figs[idx][0]==" " else ""
                elements.append(cmd + figs[idx])
                idx = idx + 1
            return elements   

def putObj(ly, lst, elements, initP, rotP, rot):
#（図形要素、図形基準の配置点、図中座標上の回転中心点、回転角）
    x0 = initP[0]; y0 = initP[1]
    px = rotP[0]; py = rotP[1]
    lst.append(ly+"\n")
    for ele in elements:
        if ele[1] == "h":
            el = ele.split("_")
        else:
            el = ele.split()

        if el[0] == "L":
            x1 = float(el[1]); y1 = float(el[2])
            x2 = float(el[3]); y2 = float(el[4])
            if len(el) > 5:
                lst.append(el[5]+"\n")
                lst.append(el[6]+"\n")
            rx1 = (x1+px) * math.cos(rot) - (y1+py) * math.sin(rot) + x0
            ry1 = (x1+px) * math.sin(rot) + (y1+py) * math.cos(rot) + y0
            rx2 = (x2+px) * math.cos(rot) - (y2+py) * math.sin(rot) + x0
            ry2 = (x2+px) * math.sin(rot) + (y2+py) * math.cos(rot) + y0
            line = "L {} {} {} {}\n".format(str(rx1), str(ry1), str(rx2), str(ry2)); lst.append(line)  
        else:
            if el[0] == "ci":
                x1 = float(el[1]); y1 = float(el[2])
                rlen = float(el[3])
                rx1 = (x1+px) * math.cos(rot) - (y1+py) * math.sin(rot) + x0
                ry1 = (x1+px) * math.sin(rot) + (y1+py) * math.cos(rot) + y0
                if len(el) <= 6:    # 円
                    if len(el) == 6:
                        lst.append(el[4]+"\n")
                        lst.append(el[5]+"\n")                    
                    line = "{} {} {} {}\n".format("ci", str(rx1), str(ry1), str(rlen)); lst.append(line)
                else:   #　arc
                    if len(el) == 10:
                        lst.append(el[8]+"\n")
                        lst.append(el[9]+"\n")                    
                    stdeg = float(el[4]) + rot * 180 / math.pi
                    eddeg = float(el[5]) + rot * 180 / math.pi
                    line = "{} {} {} {} {} {} {} {}\n".format("ci", str(rx1), str(ry1), str(rlen), str(stdeg), str(eddeg), el[6], el[7]); lst.append(line)                    
            if el[0] == "ch":   # 文字列
                x1 = float(el[1]); y1 = float(el[2]); dx = float(el[3]); dy = float(el[4]); strg = el[5]
                rx1 = (x1+px) * math.cos(rot) - (y1+py) * math.sin(rot) + x0
                ry1 = (x1+px) * math.sin(rot) + (y1+py) * math.cos(rot) + y0
                rx2 = (dx+px) * math.cos(rot) - (dy+py) * math.sin(rot) + x0
                ry2 = (dx+px) * math.sin(rot) + (dy+py) * math.cos(rot) + y0
                lst.append("ch_{}_{}_{}_{}_{}\n".format(str(rx1), str(ry1), str(rx2), str(ry2), strg))

            if len(ele) < 6 or ele[0:2] == "cn":    # 単発コマンド
                lst.append(ele)


def addBox(lst, p1, p2, p3, p4):
    n1 = np.array(p1); n2 = np.array(p2); n3 = np.array(p3); n4 = np.array(p4)
    pb1 = n1; pb2 = n2; pt1 = n3; pt2 = n4
    line = "L {} {} {} {}\n".format(pb1[0], pb1[1], pb2[0], pb2[1]); lst.append(line)
    line = "L {} {} {} {}\n".format(pb1[0], pb1[1], pt1[0], pt1[1]); lst.append(line)
    line = "L {} {} {} {}\n".format(pt2[0], pt2[1], pt1[0], pt1[1]); lst.append(line)
    line = "L {} {} {} {}\n".format(pt2[0], pt2[1], pb2[0], pb2[1]); lst.append(line)
def addLine(lst, p1, p2):
    n1 = np.array(p1); n2 = np.array(p2)
    pb1 = n1; pb2 = n2    
    line = "L {} {} {} {}\n".format(pb1[0], pb1[1], pb2[0], pb2[1]); lst.append(line)
def addflg(lst, p1, p2, p3, p4):
    n1 = np.array(p1); n2 = np.array(p2); n3 = np.array(p3); n4 = np.array(p4)
    pb1 = n1; pb2 = n2; pt1 = n3; pt2 = n4    
    line = "L {} {} {} {}\n".format(pb1[0], pb1[1], pb2[0], pb2[1]); lst.append(line)
    line = "L {} {} {} {}\n".format(pt1[0], pt1[1], pt2[0], pt2[1]); lst.append(line)
def addcircle(lst, x, y, r):
    lst.append("{} {} {} {}\n".format("ci", str(x), str(y), str(r)))

def addpoint(lst, p1):
    n1 = np.array(p1)
    pb1 = n1    
    line = "pt {} {}\n".format(pb1[0], pb1[1]); lst.append(line)    
def addstring(lst, p1, p2, strg, cn, cc):
    lst.append(cc)
    if cc == "cc1\n":
        x = (p1[0] + p2[0]) / 2; y = (p1[1] + p2[1]) / 2
    else:
        x = p1[0]; y = p1[1]
    x1 = x; y1 = y
    dx = p2[0] - p1[0]; dy = p2[1] - p1[1]
    lst.append(cn)
    line = "ch_{}_{}_{}_{}_{}\n".format(x1, y1, dx, dy, strg); lst.append(line)
def addBalloon(lst, p1, p2, strgs, cn, cc, scale):
    lst.append("lc1\n")    #線色:青
    lst.append("lt1\n")
    lst.append("ly1\n")
    lst.append("lg8\n")
    n1 = np.array(p1); n2 = np.array(p2)
    pb1 = n1; pb2 = n2
    line = "L {} {} {} {}\n".format(pb1[0], pb1[1], pb2[0], pb2[1]); lst.append(line)
    line = "L {} {} {} {}\n".format(pb2[0], pb2[1]+ 160/40 * scale *(len(strgs)-1), pb2[0], pb2[1]); lst.append(line)
    dirx = 1 if p2[0] > p1[0] else -1
    diry = 1 if p2[1] > p1[1] else -1    
    cnt = 0
    y0 = p2[1]
    for strg in strgs:
        y = y0 + diry * cnt * 160/40 * scale
        lth = strlth(strg)
        p2 = [p2[0], y]
        p3 = [p2[0] + lth * 70/40 * scale , y]
        pb2 = np.array(p2)       
        pb3 = np.array(p3)

        addstring(lst, p2, p3, strg, cn, cc)   #文字列はaddstring()でofs適用されるのでここでは元値を指定する
        if dirx < 0:
            dx = pb3[0] - pb2[0]
            x2 = pb2[0] - dx; x3 = pb3[0] -dx
        else:
            x2 = pb2[0]; x3 = pb3[0]
        line = "L {} {} {} {}\n".format(x2, pb3[1], x3, pb3[1]); lst.append(line)
        cnt += 1

def strlth(text):   #全角を2文字と数えた文字列長
    count = 0
    for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
            count += 2
        else:
            count += 1
    return count

def strtrm(strg):   #建具寸法文字を整形
    if strg[:3] == "布基礎": return "布基礎"
    if strg[:2] == "束石": return strg.replace(",", " ")

    st = strg.split("x")
    if strg[0] == "W":
        hd1 = st[0][:-3]; ed1 = st[0][-3:]
        hd2 = st[1][:-3]; ed2 = st[1][-3:]
        ret = "{},{}×{},{}".format(hd1, ed1, hd2, ed2)
    else:
        i = 0 ; ret = st[0]
        while i < len(st) - 1:
            i += 1
            ret = ret + "×" + st[i]
    return ret

def getCrossPoint(ia, ixy, ja, jxy):# 二本の線の傾きと通る一点を指定
    ix1 = ixy[0]; iy1 = ixy[1]
    jx1 = jxy[0]; jy1 = jxy[1]
    ib = iy1 - ia * ix1
    jb = jy1 - ja * jx1
    #(ix1, iy1)-(0, ib), (jx1, jy1)-(0, jb)
    ix2 = 0; iy2 = ib
    jx2 = 0; jy2 = jb
    s1 = ((jx2 - jx1) * (iy1 - jy1) - (jy2 - jy1) * (ix1 - jx1)) / 2
    s2 = ((jx2 - jx1) * (jy1 - iy2) - (jy2 - jy1) * (jx1 - ix2)) / 2
    #a =  ix1 + (ix2 - ix1) * s1 / (s1 + s2)
    x = ix1 + (ix2 - ix1) * s1 / (s1 + s2)  #X座標
    y = iy1 + (iy2 - iy1) * s1 / (s1 + s2)  #Y座標
    return [x, y]

def getCrossPointby4P(p1,p2,p3,p4):
    s1 = ((p4[0]-p3[0])*(p1[1]-p3[1]) - (p4[1]-p3[1])*(p1[0]-p3[0])) / 2
    s2 = ((p4[0]-p3[0])*(p3[1]-p2[1]) - (p4[1]-p3[1])*(p3[0]-p2[0])) / 2
    cx = p1[0] + (p2[0]-p1[0]) * s1/(s1 + s2)
    cy = p1[1] + (p2[1]-p1[1]) * s1/(s1 + s2)    
    return [cx, cy]

def expandfig_x(elements, thr, tarlen):# 原点からthr以上離れた点群を最遠点からtarlenの差分だけ移動する
    x1 = []
    for ele in elements:
        el = ele.split()
        if el[0] == "L":
            x1.append(float(el[1]))
            x1.append(float(el[3]))
        elif len(el) > 4:
            x1.append(float(el[1]))
    if thr > 0:
        xmax = max(x1)
    else:
        xmax = min(x1)
    explen = tarlen - xmax

    ele2 = []
    for ele in elements:
        el = ele.split()
        if el[0] == "L":
            xp1 = float(el[1]); yp1 = float(el[2])
            xp2 = float(el[3]); yp2 = float(el[4])
            if thr > 0:
                if float(el[1]) > thr:
                    xp1 = float(el[1]) + explen
                if float(el[3]) > thr:
                    xp2 = float(el[3]) + explen              
            else:
                if float(el[1]) < thr:
                    xp1 = float(el[1]) + explen
                if float(el[3]) < thr:
                    xp2 = float(el[3]) + explen              

            line = "L {} {} {} {} {} {}\n".format(str(xp1), str(yp1), str(xp2), str(yp2), el[5], el[6]); ele2.append(line)
        elif len(el) > 4:
            xp1 = float(el[1]); yp1 = float(el[2]); rp1 = float(el[3])
            if float(el[1]) > thr:
                xp1 = float(el[1]) + explen  
            line = "{} {} {} {} {} {}\n".format("ci", str(xp1), str(yp1), str(rp1), el[4], el[5]); ele2.append(line)
    return ele2
    
def expandfig_y(elements, thr, tarlen):# 原点からthr以上離れた点群を最遠点からtarlenの差分だけ移動する
    x1 = []
    for ele in elements:
        el = ele.split()
        if el[0] == "L":
            x1.append(float(el[2]))
            x1.append(float(el[4]))
        else:
            x1.append(float(el[2]))
    ymax = max(x1)
    explen = tarlen - ymax

    ele2 = []
    for ele in elements:
        el = ele.split()
        if el[0] == "L":
            xp1 = float(el[1]); yp1 = float(el[2])
            xp2 = float(el[3]); yp2 = float(el[4])
            if float(el[2]) > thr:
                yp1 = float(el[2]) + explen
            if float(el[4]) > thr:
                yp2 = float(el[4]) + explen              
            line = "L {} {} {} {} {} {}\n".format(str(xp1), str(yp1), str(xp2), str(yp2), el[5], el[6]); ele2.append(line)
        else:
            xp1 = float(el[1]); yp1 = float(el[2]); rp1 = float(el[3])
            if float(el[2]) > thr:
                yp1 = float(el[2]) + explen  
            line = "{} {} {} {} {} {}\n".format("ci", str(xp1), str(yp1), str(rp1), el[4], el[5]); ele2.append(line)
    return ele2

def mirror(lst, axis, axisp):
    def inv(strxy):
        xy = float(strxy)
        dis = xy - axisp
        invxy = xy - dis * 2
        return str(invxy)

    newlst = []
    for ele in lst:
        cmd = ele[0:2]
        elst = ele.strip("L ").rstrip("\n").split(" ")    #末尾の\nを除いた後、スペースで分割
        if cmd == "pt":
            if axis == "x":
                elst[1] = inv(elst[1])
            else:
                elst[2] = inv(elst[2])
            line = "{} {} {}\n".format(cmd, elst[1], elst[2]); newlst.append(line)  
        else:
            if len(elst) >= 4:
                if axis == "x":
                    elst[0] = inv(elst[0]); elst[2] = inv(elst[2])
                else:
                    elst[1] = inv(elst[1]); elst[3] = inv(elst[3])
                line = "L {} {} {} {}\n".format(elst[0], elst[1], elst[2], elst[3]); newlst.append(line)
            else:
                newlst.append(ele)
    return newlst    

def objSize(rh, elements):
    horlines = []; ylst = []
    verlines = []; xlst = []
    for ele in elements:
        el = ele.split()
        if el[0] == "L":
            if el[1] == el[3]:
                verlines.append(ele)
                xlst.append(float(el[1]))
            if el[2] == el[4]:
                horlines.append(ele)
                ylst.append(float(el[2]))
    xmax = max(xlst); xmin = min(xlst)
    if rh == "立面":
        ymax = max(ylst); ymin = min(ylst)    
    else:
        ymax = 100; ymin = 0
    return xmax, xmin, ymax, ymin, verlines, horlines

def putTategu(lst, tor):
    #lst.append("ly5\n")
    for i in range(1, window_vol+1):
        itm = "窓" + str(i)
        kind(lst, itm, tor)
    for i in range(1, door_vol + 1):
        itm = "框ドア" + str(i)
        kind(lst, itm, tor)
    for i in range(1, turido_vol + 1):
        itm = "吊り戸" + str(i)
        kind(lst, itm, tor)
    for i in range(1, shutter_vol + 1):
        itm = "軽量シャッター" + str(i)
        kind(lst, itm, tor)
    for i in range(1, idoushutter_vol + 1):
        itm = "移動中柱付きシャッター" + str(i)
        kind(lst, itm, tor)
    for i in range(1, OS_vol + 1):
        itm = "オーバースライダー" + str(i)
        kind(lst, itm, tor)
    if tor == "A":
        talst.append(ylen)
        return sorted(talst)
    if tor == "B":
        global tblst
        tblst.append(ylen)
        if len(tblst) > 2:  # 寸法セグをreverseする
            lnth = []
            for i in range(1, len(tblst)):
                lnth.append(tblst[i] - tblst[i-1])
            lnth.reverse()
            tblst = [0]
            for ln in lnth:
                if ln != 0: tblst.append(tblst[-1] + ln)
        return sorted(tblst)
    if tor == "1":
        global t1lst
        t1lst.append(xlen)
        if len(t1lst) > 2:  # 寸法セグをreverseする
            lnth = []
            for i in range(1, len(t1lst)):
                lnth.append(t1lst[i] - t1lst[i-1])
            lnth.reverse()
            t1lst = [0]
            for ln in lnth:
                if ln != 0: t1lst.append(t1lst[-1] + ln)        
        return sorted(t1lst)
    if tor == "E":
        telst.append(xlen)
        return sorted(telst)

def kind(lst, itm, tor):
    lst.append("ly5\n")    
    pos_h_spec = dic[itm].split(",")
    pos = pos_h_spec[0].split("-")
    tori = pos[0]
    if tori != tor: return
    seg = int(pos[1])
    hpos = int(pos_h_spec[1])
    spec = pos_h_spec[2]

    lst.append("lc3\n")    #線色:緑 
    if tori == "A":
        if "窓" in itm and hpos > 3000:
            toriAry = toriNum
        else:
            toriAry = toriA
        pl = int(toriAry[seg-1])
        ph = int(toriAry[seg])    
        if "窓" not in itm and "框ドア" not in itm: 
            if talst[-1] != pl: talst.append(pl)
            talst.append(ph)
    if tori == "B": 
        toriAry = toriB
        pl = int(toriAry[seg-1])
        ph = int(toriAry[seg])
        if "窓" not in itm and "框ドア" not in itm:          
            if tblst[-1] != pl: tblst.append(pl)
            tblst.append(ph)
    if tori == "1":
        toriAry = tori1
        pl = int(toriAry[seg-1])
        ph = int(toriAry[seg])    
        if "窓" not in itm and "框ドア" not in itm: 
            if t1lst[-1] != pl: t1lst.append(pl)
            t1lst.append(ph)
    if tori == "E":
        toriAry = toriE
        pl = int(toriAry[seg-1])
        ph = int(toriAry[seg])    
        if "窓" not in itm and "框ドア" not in itm: 
            if telst[-1] != pl: telst.append(pl)
            telst.append(ph)
    pm = pl + (ph - pl) / 2

    if tori == "B": pm = ylen - pm; pl = ylen - pl; ph = ylen - ph
    if tori == "1": pm = xlen - pm; pl = xlen - pl; ph = xlen - ph
    if spec[0] == "W":
        width = int(spec.split("x")[0][1:])
        height = int(spec.split("x")[1][1:])
        truewidth = int(abs(ph - pl))
        tnum = 2 if width < truewidth else 1
        ele1 = getFig(itm[:-1] + "\n")

        if "吊り戸" in itm: nam = "吊り戸"
        elif "シャッター" in itm: nam = "軽量シャッター"
        else: nam = "オーバースライダー"

        if tnum == 1:
            ele1 = expandfig_x(ele1, 800, abs(ph - pl) / 2 + 50)
            ele1 = expandfig_x(ele1, -800, -abs(ph - pl) / 2 - 50)
            elements = expandfig_y(ele1, 1400, height + 50)
        else:   # 2枚
            ele1 = expandfig_x(ele1, 800, 0)
            ele1 = expandfig_x(ele1, -800, -abs(ph - pl)/2 - 50)
            elements = expandfig_y(ele1, 1400, height + 50)
            elements2 = mirror(elements, "x", 0)          
            elements.extend(elements2)

        if nam == "吊り戸":
            opt = "(片開き)" if tnum == 1 else "(両開き)"
        elif nam == "軽量シャッター": 
            if "中柱" in itm:
                opt = "(移動中柱付き)"
                y = 0; p = sorted([pl, pm - 50, pm + 50, ph])
                while y < height - 150:
                    y += 150
                    addLine(lst, [p[0], hpos + y], [p[1], hpos + y])
                    addLine(lst, [p[2], hpos + y], [p[3], hpos + y])                
            else:   # 普通のシャッター
                opt = ""
                y = 0
                while y < height - 150:
                    y += 150
                    addLine(lst, [pl, hpos + y], [ph, hpos + y])
        else:   # O.S
            opt = ""
            y = 0; p = sorted([pl, pm - 50, pm + 50, ph])
            while y < height - 400:
                y += 400
                addLine(lst, [p[0], hpos + y], [p[3], hpos + y])

        key = strtrm(f"W{truewidth}xH{height}") + opt
        keylst.append((nam, key))            

    else:   # "WxH"ではない場合
        elements = getFig(spec + "\n")
        if "窓" in itm:
            nam = "サッシ窓"
        if "框ドア" in itm:
            nam = "框ドア"
        key = str(spec)
        keylst.append((nam, key))           

    putObj("ly5", lst, elements, [pm, hpos], [0, 0], 0)
    trimHatch(lst, elements, pm, hpos)
def trimHatch(lst, elements, pm, hpos):
    lst.append("ly4\n")    
    mxlnlst = []#; mninlst = []
    #llnlst = []; rlnlst = []
    xmax, xmin, ymax, ymin, verlines, horlines = objSize("立面", elements)

    for ele in horlines:
        el = ele.split()
        if float(el[2]) == ymax:
            mxlnlst.append([float(el[1]), float(el[2]), float(el[3]), float(el[4])])
    for el in mxlnlst:
        ly = hpos
        hy = hpos + ymax
        if el[0] < el[2]:
            lx = el[0]; rx = el[2]
        else:
            lx = el[2]; rx = el[0]

    dellst = []; addlst = []
    for ele in lst: # 立面ハッチ線のトリミング
        if ele[0]=="L": # 直線
            el = ele.split()
            x1 = float(el[1]); x2 = float(el[3]); y1 = float(el[2]); y2 = float(el[4])
            if abs(x1 - x2) < 0.1:  # 縦線　演算誤差を含むので0ではない
                if x1 > xmin + pm and x1 < xmax + pm:   # 横範囲に入る
                    if y1 > y2:
                        ehy = y1; ely = y2
                    else:
                        ehy = y2; ely = y1
                    if ehy > hy and ely < hy and ely >= ly:
                        dellst.append(ele)
                        addlst.append("L {} {} {} {}\n".format(x1, str(ehy), x1, str(hy)))
                    if ehy > hy and ely < ly:
                        dellst.append(ele)
                        addlst.append("L {} {} {} {}\n".format(x1, str(ehy), x1, str(hy)))                    
                        addlst.append("L {} {} {} {}\n".format(x1, str(ly), x1, str(ely))) 
    if ly < 0:  # 立面基礎線のトリミング
        for ele in lst:
            if ele[0]=="L": # 直線
                el = ele.split()
                x1 = float(el[1]); x2 = float(el[3]); y1 = float(el[2]); y2 = float(el[4])
                if y1 == 0 and y2 == 0:  # 横線　演算誤差を含むので0ではない
                    if x1 < x2:
                        elx = x1; erx = x2
                    else:
                        elx = x2; erx = x1
                    lx = pm + xmin; rx = pm + xmax
                    if elx < lx and erx > rx:
                        dellst.append(ele)
                        addlst.append("L {} {} {} {}\n".format(elx, 0, lx, 0))                    
                        addlst.append("L {} {} {} {}\n".format(rx, 0, erx, 0))                     
    for ele in dellst:
        lst.remove(ele)
    lst.append("lc4\n")    #線色:黄        
    for ele in addlst:
        lst.append(ele)

def putTateguHei(lst):
    for tor in ("1", "E", "A", "B"):
        for i in range(1, window_vol+1):
            itm = "窓" + str(i)
            kind1(lst, itm, tor)
        for i in range(1, door_vol + 1):
            itm = "框ドア" + str(i)
            kind1(lst, itm, tor)
        for i in range(1, turido_vol + 1):
            itm = "吊り戸" + str(i)
            kind1(lst, itm, tor)
        for i in range(1, shutter_vol + 1):
            itm = "軽量シャッター" + str(i)
            kind1(lst, itm, tor)
        for i in range(1, idoushutter_vol + 1):
            itm = "移動中柱付きシャッター" + str(i)
            kind1(lst, itm, tor)
        for i in range(1, OS_vol + 1):
            itm = "オーバースライダー" + str(i)
            kind1(lst, itm, tor)
def kind1(lst, itm, tor):
    pos_h_spec = dic[itm].split(",")
    pos = pos_h_spec[0].split("-")
    tori = pos[0]
    if tori != tor: return
    seg = int(pos[1])
    hpos = int(pos_h_spec[1])
    spec = pos_h_spec[2]
    if hpos > 2000: return

    lst.append("lc3\n")    #線色:緑
    if tori == "A":
        elements, el2, pm, tategustr = get(itm, toriA, seg, spec, tor)
        xmax, xmin, ymax, ymin, verlines, horlines = objSize("平面", elements)      
        elements.extend(el2)
        putObj("ly5", lst, elements, [pm, -cw/2 - dobutih], [0, 0], math.pi)
        trm(lst, tori, [pm, -cw/2 - dobutih], pm, xmax)
        lst.append("ly1\n")
        addstring(lst, [pm, 1400], [pm+100, 1400], tategustr[0], "cn5\n", "cc1\n")
        addstring(lst, [pm, 700], [pm+100, 700], tategustr[1], "cn5\n", "cc1\n")
    if tori == "B": 
        elements, el2, pm, tategustr = get(itm, toriB, seg, spec, tor)       
        xmax, xmin, ymax, ymin, verlines, horlines = objSize("平面", elements)
        elements.extend(el2)
        putObj("ly5", lst, elements, [pm, xlen + cw/2 + dobutih], [0, 0], 0)
        trm(lst, tori, [pm, xlen + cw/2 + dobutih], pm, xmax)
        lst.append("ly1\n")
        addstring(lst, [pm, xlen-700], [pm+100, xlen-700], tategustr[0], "cn5\n", "cc7\n")
        addstring(lst, [pm, xlen-1400], [pm+100, xlen-1400], tategustr[1], "cn5\n", "cc7\n")        
    if tori == "1":
        elements, el2, pm, tategustr = get(itm, tori1, seg, spec, tor)       
        xmax, xmin, ymax, ymin, verlines, horlines = objSize("平面", elements)
        elements.extend(el2)
        putObj("ly5", lst, elements, [-mw/2 - dobutih, pm], [0, 0], math.pi/2)
        trm(lst, tori, [-mw/2 - dobutih, pm], pm, xmax)
        lst.append("ly1\n")
        addstring(lst, [600, pm+200], [800, pm+200], tategustr[0], "cn5\n", "cc0\n")
        addstring(lst, [600, pm-500], [800, pm-500], tategustr[1], "cn5\n", "cc0\n")        
    if tori == "E":
        elements, el2, pm, tategustr = get(itm, toriE, seg, spec, tor)
        xmax, xmin, ymax, ymin, verlines, horlines = objSize("平面", elements)
        elements.extend(el2)
        putObj("ly5", lst, elements, [ylen + mw/2 + dobutih, pm], [0, 0], -math.pi/2)
        trm(lst, tori, [ylen + mw/2 + dobutih, pm], pm, xmax)
        lst.append("ly1\n")
        addstring(lst, [ylen-600, pm+200], [ylen-500, pm+200], tategustr[0], "cn5\n", "cc2\n")
        addstring(lst, [ylen-600, pm-500], [ylen-500, pm-500], tategustr[1], "cn5\n", "cc2\n")           
def get(itm, toriAry, seg, spec, tor):
    tategustr = ("", "")
    el2 = []
    pl = float(toriAry[seg-1])
    ph = float(toriAry[seg])
    pw = (ph - pl) / 2
    pm = pl + pw
    if spec[0] == "W":
        width = int(spec.split("x")[0][1:])
        height = int(spec.split("x")[1][1:])
        truewidth = int(abs(ph - pl))        
        tnum = 2 if width < ph - pl else 1        
        if tor == "A" or tor == "B":
            p1 = [-pw + cd/2, kabe_t]; p3 = [pw - cd/2, kabe_t]
            p2 = [-pw + cd/2, -dobutih -cw]; p4 = [pw - cd/2, -dobutih -cw]
            p5 = [-pw, -dobutih -cw -40]; p6 = [pw, -dobutih -cw -40]
        else:
            p1 = [-pw + md/2, kabe_t]; p3 = [pw - md/2, kabe_t]
            p2 = [-pw + md/2, -dobutih -mw]; p4 = [pw - md/2, -dobutih -mw]
            p5 = [-pw, -dobutih -mw -40]; p6 = [pw, -dobutih -mw -40]
        elements = []
        elements.append("ly3\n")
        elements.append("L {} {} {} {} {} {}\n".format(str(p1[0]), str(p1[1]), str(p2[0]), str(p2[1]), "lt1", "lc4")) 
        elements.append("L {} {} {} {} {} {}\n".format(str(p3[0]), str(p3[1]), str(p4[0]), str(p4[1]), "lt1", "lc4")) 
        elements.append("ly5\n")
        if ("吊り戸" in itm) == True:
            elements.append("L {} {} {} {} {} {}\n".format(str(p5[0]), str(p5[1]), str(p6[0]), str(p6[1]), "lt1", "lc3")) 
            elements.append("L {} {} {} {} {} {}\n".format(str(p5[0]), str(p5[1]-50), str(p6[0]), str(p6[1]-50), "lt1", "lc3")) 
            if tnum == 2:   # 両開きの場合
                tategustr = ("両開き吊り戸", strtrm(f"W{truewidth}xH{height}"))
                el2 = getFig("両開き入口記号\n")
                el2.append("L {} {} {} {} {} {}\n".format(str(p5[0]-width), str(p5[1]-25), str(p5[0]), str(p5[1]-25), "lt2", "lc3"))            
                el2.append("L {} {} {} {} {} {}\n".format(str(p6[0]+width), str(p5[1]-25), str(p6[0]), str(p5[1]-25), "lt2", "lc3"))            
                el2.append("L {} {} {} {} {} {}\n".format(0, str(p5[1]), 0, str(p5[1]-50), "lt1", "lc3"))            
                el2.append("L {} {} {} {} {} {}\n".format(str(p5[0]), str(p5[1]), str(p5[0]), str(p5[1]-50), "lt1", "lc3"))            
                el2.append("L {} {} {} {} {} {}\n".format(str(p6[0]), str(p5[1]), str(p6[0]), str(p5[1]-50), "lt1", "lc3"))
            else:   # 片開きの場合
                tategustr = ("吊り戸", strtrm(f"W{truewidth}xH{height}"))
                el2 = getFig("入口記号\n")
                el2.append("L {} {} {} {} {} {}\n".format(str(p5[0]-width), str(p5[1]-25), str(p5[0]), str(p5[1]-25), "lt2", "lc3"))
                el2.append("L {} {} {} {} {} {}\n".format(str(p5[0]), str(p5[1]), str(p5[0]), str(p5[1]-50), "lt1", "lc3"))            
                el2.append("L {} {} {} {} {} {}\n".format(str(p6[0]), str(p5[1]), str(p6[0]), str(p5[1]-50), "lt1", "lc3"))              
        else:   # シャッター、O.S
            if "シャッター" in itm: tategustr = ("軽量シャッター", strtrm(f"W{truewidth}xH{height}"))
            if "オーバースライダー" in itm: tategustr = ("オーバースライダー", strtrm(f"W{width}xH{height}"))
            el2 = getFig("入口記号\n") 
            elements.append("L {} {} {} {} {} {}\n".format(str(p5[0]), str(p5[1]), str(p6[0]), str(p6[1]), "lt2", "lc3")) 
    else:
        elements = getFig(spec + "上" + "\n")
    return elements, el2, pm, tategustr
def trm(lst, tori, pos, pm, xmax):
    lst.append("lc4\n")    #線色:黄
    lst.append("ly3\n")
    lst.append("lt1\n")
    dellst = []; addlst = []
    lobjx = pm -xmax; robjx = pm + xmax
    for ele in lst:
        el = ele.split()
        if el[0]=="L": # 直線
            x1 = float(el[1]); x2 = float(el[3]); y1 = float(el[2]); y2 = float(el[4])
            if tori == "A":
                if (y1 == pos[1] and y2 == pos[1]) or (y1 == pos[1] - kabe_t and y2 == pos[1] - kabe_t):
                    (lx, rx) = (x1, x2) if x1 < x2 else (x2, x1)
                    if lx < lobjx and rx > robjx:
                        dellst.append(ele)
                        addlst.append("L {} {} {} {}\n".format(str(lx), str(y1), str(lobjx), str(y1)))                    
                        addlst.append("L {} {} {} {}\n".format(str(robjx), str(y1), str(rx), str(y1)))
            if tori == "B":
                if (y1 == pos[1] and y2 == pos[1]) or (y1 == pos[1] + kabe_t and y2 == pos[1] + kabe_t):
                    (lx, rx) = (x1, x2) if x1 < x2 else (x2, x1)
                    if lx < lobjx and rx > robjx:
                        dellst.append(ele)
                        addlst.append("L {} {} {} {}\n".format(str(lx), str(y1), str(lobjx), str(y1)))                    
                        addlst.append("L {} {} {} {}\n".format(str(robjx), str(y1), str(rx), str(y1)))
            if tori == "1":
                if (x1 == pos[0] and x2 == pos[0]) or (x1 == pos[0] - kabe_t and x2 == pos[0] - kabe_t):
                    (ly, ry) = (y1, y2) if y1 < y2 else (y2, y1)
                    if ly < lobjx and ry > robjx:
                        dellst.append(ele)
                        addlst.append("L {} {} {} {}\n".format(str(x1), str(ly), str(x1), str(lobjx)))                    
                        addlst.append("L {} {} {} {}\n".format(str(x1), str(robjx), str(x1), str(ry)))
            if tori == "E":
                if (x1 == pos[0] and x2 == pos[0]) or (x1 == pos[0] + kabe_t and x2 == pos[0] + kabe_t):
                    (ly, ry) = (y1, y2) if y1 < y2 else (y2, y1)
                    if ly < lobjx and ry > robjx:
                        dellst.append(ele)
                        addlst.append("L {} {} {} {}\n".format(str(x1), str(ly), str(x1), str(lobjx)))                    
                        addlst.append("L {} {} {} {}\n".format(str(x1), str(robjx), str(x1), str(ry)))
    for ele in dellst:
        lst.remove(ele)
    for ele in addlst:
        lst.append(ele)

def editSunpou(lst, scale, typ):
    lst.append("cc1\n")    #文字基準点:中下
    lst.append("lc1\n")    #線色:青
    lst.append("ly1\n")
    lst.append("lg8\n")    #矩計図
    d1 = 4 * scale
    d2 = d1 + 8 * scale
    sof = -5 * scale    
    if typ == "片流れ":
        toph = nh+slope*xlen
    else:
        toph = nh+slope*xlen/2
    putSunpou(lst, [sof, -mbase[1]], [sof, gl], [d1, d2], "cn6\n", 0)
    putSunpou(lst, [sof, gl], [sof, 0], [d1, d2], "cn6\n", 0)
    putSunpou(lst, [sof, 0], [sof, nh], [d1, d2], "cn6\n", 0)
    putSunpou(lst, [sof, nh], [sof, toph], [d1, d2], "cn6\n", 0)
    putSunpou(lst, [sof, -mbase[1]], [sof, 0], [d2, d2 + (d2-d1)], "cn6\n", 0)
    putSunpou(lst, [sof, 0], [sof, toph], [d2, d2 + (d2-d1)], "cn6\n", 0)
    strg = "矩 計 図"
    dd = -scale * 15
    lth = strlth(strg) * 70/40 * scale
    if typ == "片流れ":
        p1 = [xlen/2 - lth*0.7, 0]
        p2 = [xlen/2 + lth*0.7, 0]    
        putZumei(lst, p1, p2, dd, strg, "cc1\n")
        putSunpou(lst, [0, -900], [xlen, -900], [-d1, -d2], "cn6\n", 0)
    else:
        p1 = [xlen/4 - lth*0.7, 0]
        p2 = [xlen/4 + lth*0.7, 0]    
        putZumei(lst, p1, p2, dd, strg, "cc1\n")
        putSunpou(lst, [0, -900], [xlen/2, -900], [-d1, -d2], "cn6\n", 0)

    slp0 = [400, nh + 800]
    slp1 = [slp0[0], slp0[1] + math.tan(r) * 1000]
    slp2 = [slp0[0] + 1000, slp1[1]]
    addLine(lst, slp0, slp1); addLine(lst, slp1, slp2); addLine(lst, slp0, slp2)
    addstring(lst, slp1, slp2, "10", "cn5\n", "cc1\n")
    lth = strlth(str(slope * 10)) *70/40 * scale
    slp4 = [slp0[0], (slp0[1]+slp1[1])/2]
    slp3 = [slp4[0]-lth, slp4[1]]
    addstring(lst, slp3, slp4, str(slope*10), "cn5\n", "cc3\n")

def editSunpouRitu(lst, tlst, fulllth, scale, tori, typ):
    lst.append("lg0\n")
    lst.append("lc1\n")    #線色:青
    lst.append("ly1\n")
    d1 = 4 * scale
    d2 = d1 + 5 * scale 
    putSunpou(lst, [0, gl], [0, 0], [d1, d2], "cn6\n", 0)
    putSunpou(lst, [0, 0], [0, nh], [d1, d2], "cn6\n", 0)
    toph = nh+slope*xlen if typ == "片流れ" else nh+slope*xlen / 2
    putSunpou(lst, [0, nh], [0, toph], [d1, d2], "cn6\n", 0)
    putSunpou(lst, [0, 0], [0, toph], [d2, d2 + (d2-d1)], "cn6\n", 0)
    i = 0
    while i < len(tlst)-1:
        d3 = -d2
        if tlst[i] != tlst[i+1]:
            putSunpou(lst, [tlst[i], 0], [tlst[i+1], -0], [-d1, -d2], "cn6\n", 0)
        i += 1
    if i > 1:
        d3 = -d2 - (d2-d1)
        putSunpou(lst, [0, 0], [fulllth, -0], [-d2, d3], "cn6\n", 0)
    strg = tori + " 立 面 図"
    if tori == "E": strg = f"{torivol} 立 面 図"
    
    dd = d3 - scale * 5
    lth = strlth(strg) * 70/40 * scale
    p1 = [fulllth/2 - lth*0.7, 0]
    p2 = [fulllth/2 + lth*0.7, 0]    
    putZumei(lst, p1, p2, dd, strg, "cc1\n")
    if tori == "1" or tori == "E":
        putTumaNum(lst, [0, toph + scale * 8], scale, tori)
    else:
        putNokiNum(lst, [0, toph + scale * 8], toriNum, scale, tori)        

def editSunpouHei(lst, scale):
    lst.append("lg0\n")
    lst.append("lc1\n")    #線色:青
    lst.append("ly1\n")
    d1 = 4 * scale
    d2 = d1 + 5 * scale 
    i = 0
    while i < len(toriA)-1:
        putSunpou(lst, [toriA[i], 0], [toriA[i+1], 0], [-d1, -d2], "cn6\n", 0); i += 1
    putSunpou(lst, [0, 0], [max(toriA), 0], [-d2, -d2 - (d2-d1)], "cn6\n", 0); i = 0
    while i < len(toriB)-1:
        putSunpou(lst, [toriB[i], xlen], [toriB[i+1], xlen], [d1, d2], "cn6\n", 0); i += 1
    putSunpou(lst, [0, xlen], [max(toriB), xlen], [d2, d2 + (d2-d1)], "cn6\n", 0); i = 0
    while i < len(tori1)-1:
        putSunpou(lst, [0, tori1[i]], [0, tori1[i+1]], [d1, d2], "cn6\n", 0); i += 1
    putSunpou(lst, [0, 0], [0, max(tori1)], [d2, d2 + (d2-d1)], "cn6\n", 0); i = 0
    while i < len(toriE)-1:
        putSunpou(lst, [ylen, toriE[i]], [ylen, toriE[i+1]], [-d1, -d2], "cn6\n", 0); i += 1
    putSunpou(lst, [ylen, 0], [ylen, max(toriE)], [-d2, -d2 - (d2-d1)], "cn6\n", 0)
    strg = "平 面 図"
    dd = -scale * 20
    lth = strlth(strg) * 70/40 * scale
    p1 = [ylen/2 - lth*0.7, 0]
    p2 = [ylen/2 + lth*0.7, 0]    
    putZumei(lst, p1, p2, dd, strg, "cc1\n")
    putNokiNum(lst, [0, xlen + d2 * 2.5], toriNum, scale, "A")
    putTumaNum(lst, [-d2 * 2.5, 0], scale, "H")
    addstring(lst, [0, xlen/2], [ylen, xlen/2], yuka.split(",")[0] , "cn5\n", "cc1\n")

def putSunpou(lst, p1, p2, dd, cn, decp):
    vec1 = [p2[0]-p1[0], p2[1]-p1[1]]   # 寸法対象のベクトル
    vec2 = [-vec1[1], vec1[0]]  # vec1に垂直なベクトル
    vsize = math.sqrt(vec2[0]**2 + vec2[1]**2)
    bai1 = dd[0] / vsize
    bai2 = dd[1] / vsize
    pd11 = [vec2[0]*bai1, vec2[1]*bai1]
    pd12 = [vec2[0]*bai2, vec2[1]*bai2]
    d1 = np.array(p1) + np.array(pd11)
    d2 = np.array(p1) + np.array(pd12)
    d3 = np.array(p2) + np.array(pd11)
    d4 = np.array(p2) + np.array(pd12)
    addLine(lst, d1, d2)
    addLine(lst, d3, d4)
    addLine(lst, d2, d4)
    lst.append("pn0\n")
    addpoint(lst, d2); addpoint(lst, d4)
    strsize = "{:,.0f}\n".format(vsize) if decp ==0 else "{:,.1f}\n".format(vsize)
    strg = str(strsize)
    addstring(lst, d2, d4, strg, cn, "cc1\n")

def putTumaNum(lst, inip, scale, tori):
    bai = 2.4; r = scale * bai
    if tori == "1":
        i = "B"
        x = inip[0] + 0; y = inip[1]
        putNumCi(lst, x, y, r, scale, i)
        i = "A"
        x = inip[0] + xlen; y = inip[1]
        putNumCi(lst, x, y, r, scale, i)
    if tori == "E":
        i = "A"
        x = inip[0] + 0; y = inip[1]
        putNumCi(lst, x, y, r, scale, i)
        i = "B"
        x = inip[0] + xlen; y = inip[1]
        putNumCi(lst, x, y, r, scale, i)
    if tori == "H":
        i = "A"
        x = inip[0]; y = inip[1]
        putNumCi(lst, x, y, r, scale, i)
        i = "B"
        x = inip[0]; y = inip[1] + xlen
        putNumCi(lst, x, y, r, scale, i)

def putNokiNum(lst, inip, ary, scale, tori):
    i = 0; bai = 2.4
    for p in ary:
        i += 1; j = i
        if tori == "B": j = len(ary) +1 -i
        x = inip[0] + p; y = inip[1]; r = scale * bai
        putNumCi(lst, x, y, r, scale, j)        

def putNumCi(lst, x, y, r, scale, i):
    p1 = [x - 10, y]
    p2 = [x + 10, y]
    d1 = r; d2 = r + scale * 0.8
    addcircle(lst, x, y, r)
    addstring(lst, p1, p2, str(i), "cn6\n", "cc4\n")
    addLine(lst, [x - d2, y], [x - d1, y])
    addLine(lst, [x + d2, y], [x + d1, y])
    addLine(lst, [x, y - d2], [x, y - d1])
    addLine(lst, [x, y + d2], [x, y + d1])


def putZumei(lst, p1, p2, dd, strg, cn):
    vec1 = [p2[0]-p1[0], p2[1]-p1[1]]   # 寸法対象のベクトル
    vec2 = [-vec1[1], vec1[0]]  # vec1に垂直なベクトル
    vsize = math.sqrt(vec2[0]**2 + vec2[1]**2)
    bai2 = dd / vsize
    pd12 = [vec2[0]*bai2, vec2[1]*bai2]
    d2 = np.array(p1) + np.array(pd12)
    d4 = np.array(p2) + np.array(pd12)
    addLine(lst, d2, d4)
    addstring(lst, d2, d4, strg, cn, "cc1\n")

def editHyo(lst):
    dy = 4.5
    lst.append("lgF\n")
    lst.append("lc1\n")    #線色:青
    lst.append("ly1\n")    
    kozaitpl = ("梁", "柱", "間柱", "入口梁", "継梁", "方杖", "屋根ﾌﾞﾚｰｽ", "壁ﾌﾞﾚｰｽ", "母屋", "胴縁")
    rw = 0; ym = 0.5
    endx = 60
    addLine(lst, [0, rw], [endx, rw])
    addstring(lst,[0, rw + ym],[20, rw + ym], "鋼 材 表", "cn6\n", "cc0\n")
    for ele in kozaitpl:
        rw -= dy
        if len(ele) == 2:
            el = f"{ele[0]} {ele[1]}" 
        else:
            el = ele
        addstring(lst,[0, rw + ym],[20, rw + ym], el, "cn5\n", "cc1\n")
        opt = ""
        if ele == "母屋": opt = f"  @{int(moyapitch)}"
        if ele == "胴縁": opt = f"  @{int(dobutipitch)}"
        addstring(lst,[22, rw + ym],[endx, rw + ym], strtrm(dic[ele]) + opt, "cn5\n", "cc0\n")
        addLine(lst, [0, rw], [endx, rw])
    addLine(lst, [0, 0], [0, rw])
    addLine(lst, [20, 0], [20, rw])
    addLine(lst, [endx, 0], [endx, rw])

    kozaitpl = ("基礎", "床", "屋根", "屋根下地", "壁")
    Wcol0 = collections.Counter(keylst)
    Wcol = sorted(Wcol0.items(), key=lambda i: i[0][1])
    
    siagelst = []; lthlst1 = []; lthlst2 = []
    for ele in kozaitpl:
        if dic[ele] == "なし": continue
        el = f"{ele[0]} {ele[1]}" if len(ele) == 2 else ele
        try:
            if ele != "床":
                siagelst.append((el, strtrm(dic[ele])))
                lthlst1.append(strlth(el))
                lthlst2.append(strlth(strtrm(dic[ele])))                
            else:
                strg = ""
                strgs = yuka.split(",")
                siagelst.append((el, strgs[0]))                
                if len(strgs) > 1:
                    strg = yuka.replace(strgs[0]+",", "")
                    siagelst.append(("", strg))
                lthlst1.append(strlth(el))
                lthlst2.append(strlth(strg))
        except KeyError:
            continue

    for itms in Wcol:
        strg = itms[0][1] + f" ～ {itms[1]}set"      
        siagelst.append((itms[0][0], strg))
        lthlst1.append(strlth(itms[0][0]))
        lthlst2.append(strlth(strg))
    lth1 = max(lthlst1)
    lth2 = max(lthlst2)

    rw = 0; ym = 0.5
    lx = endx + 4
    mx = lx + (lth1 + 2) * 1.5
    rx = mx + (lth2 + 2) * 1.5
    addLine(lst, [lx, rw], [rx, rw])
    addstring(lst,[lx, rw + ym],[mx, rw + ym], "仕 上 表", "cn6\n", "cc0\n")
    
    for ele in siagelst:
        rw -= dy
        addstring(lst,[lx, rw + ym],[mx, rw + ym], ele[0], "cn5\n", "cc1\n")
        addstring(lst,[mx + 2, rw + ym],[rx, rw + ym], ele[1], "cn5\n", "cc0\n")
        addLine(lst, [lx, rw], [rx, rw])
    addLine(lst, [lx, 0], [lx, rw])
    addLine(lst, [mx, 0], [mx, rw])
    addLine(lst, [rx, 0], [rx, rw]) 
