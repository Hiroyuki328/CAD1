import math, re
import numpy as np
#import unicodedata
from kana_mod import commod as cm

#--------------------
dic = {}    # 部材ディクショナリ作成
dic0 = {}
dats = []
f = open("見積諸元データ/見積諸元データ.txt")
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
tb = dic["タイバー"]
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
hari_t = float(dic["梁棟PL厚"])
h1pos = float(dic["方杖位置"])
h1agl = float(dic["方杖角度"])
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
mc.append(mc[2])   #柱が角鋼の時のために補完する

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

hafuyakuw = [220, 230] if moyah + nw + sitaji_t > 181 else [180, 190]
hafut = 24 if moyaw + nw + sitaji_t > 181 else 18
ry = cw/2 * math.tan(r)
grw = gw/2/math.cos(r)
crw = cw/1/math.cos(r)
nrw = nw/1/math.cos(r)
dtn = tnt*math.sin(r)
initP = []
endP = []
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



def editKana(lst, dic, scale, typ):
    lst.append("pn1\n")
    lst.append("lc2\n")
    lst.append("lg8\n")
    # 柱、梁、軒先
    lst.append("ly0\n")
    [gt1, gc1, gb1, gt2, gc2, gb2, endP] = putG("ly0", lst, scale, typ)
    putC("ly0", lst, 0, nh, gb1, scale)
    initP = putNoki_L("ly0", lst, 0)    
    
    if typ == "片流れ":
        putC("ly0", lst, xlen, nh + slope * xlen, gb2, scale)
        endP = putNoki_U("ly0", lst, xlen)

    ba1 = [-cw/2-30, 1000]
    ba2 = [ba1[0]+400, ba1[1]+400]
    strgs = ["胴縁:"+dobuti, "壁:" + kabe]
    cm.addBalloon(lst, ba1, ba2, strgs, "cn6\n", "cc0\n", scale)
    ba1 = [cw/2, 2000]
    ba2 = [ba1[0]+300, ba1[1]+300]
    strgs = ["柱:" + c1]
    cm.addBalloon(lst, ba1, ba2, strgs, "cn6\n", "cc0\n", scale)

    # 屋根、下地
    pb1, pb2, pt1, pt2, hf1, hf2, yaku1, yaku3, klc, krc, klb2, krb2, kabe1, kabe2, kabe3 = putYane("ly3", lst, initP, endP, typ)
    lst.append("lg8\n")
    rooflen = (endP[0]-initP[0]) / math.cos(r) #屋根全長
    # 母屋、ピース
    elements1 = cm.getFig("L-50x50x4右向\n")
    cm.putObj("ly2", lst, elements1, initP, [moyaw, 0], r)
    elements2 = cm.getFig(moya + "\n")
    cm.putObj("ly3", lst, elements2, initP, [0, moyaclr], r)
    elements1 = cm.getFig("L-50x50x4左向\n")
    x = moyapitch - moyaw / 2
    while x <= rooflen - 150:
        cm.putObj("ly2", lst, elements1, initP, [x, 0], r)
        cm.putObj("ly3", lst, elements2, initP, [x, moyaclr], r)
        x = x + moyapitch
    x = rooflen - moyaw
    if typ == "切妻":
        x = x - 70
    cm.putObj("ly2", lst, elements1, initP, [x, 0], r)
    cm.putObj("ly3", lst, elements2, initP, [x, moyaclr], r)

    # 胴縁
    initP = [-cw/2, 0]  # 水下側
    elements1 = cm.getFig("L-50x50x4右向\n")
    elements2 = cm.getFig(dobuti + "\n")
    y = 60
    cm.putObj("ly2", lst, elements1, [initP[0], y], [0, 0], math.pi/2) # 柱下端からH=60に配置
    cm.putObj("ly3", lst, elements2, [initP[0] - dobutih, y], [0, -dobuticlr], -math.pi/2)

    elements1 = cm.getFig("L-50x50x4左向\n")
    y = dobutipitch
    while y <= nh - 150:
        cm.putObj("ly2", lst, elements1, [initP[0], y], [0, 0], math.pi/2)
        cm.putObj("ly3", lst, elements2, [initP[0], y], [0, dobuticlr], math.pi/2)
        y = y + dobutipitch
    cm.putObj("ly2", lst, elements1, [initP[0], kabe1[1] - dobutiw], [0, 0], math.pi/2)  #最上段
    cm.putObj("ly3", lst, elements2, [initP[0], kabe1[1] - dobutiw], [0, dobuticlr], math.pi/2)

    if typ == "片流れ":
        initP = [xlen + cw/2, 0]    # 水上側
        y = 60
        cm.putObj("ly2", lst, elements1, [initP[0], y], [0, 0], math.pi * 3/2)
        cm.putObj("ly3", lst, elements2, [initP[0], y], [0, dobuticlr], math.pi * 3/2)

        elements1 = cm.getFig("L-50x50x4右向\n")
        y = dobutipitch
        ylim = nh + slope * xlen - 150
        while y <= ylim:
            cm.putObj("ly2", lst, elements1, [initP[0], y], [0, 0], math.pi * 3/2)
            cm.putObj("ly3", lst, elements2, [initP[0] + dobutih, y], [0, -dobuticlr], math.pi * 1/2)
            y = y + dobutipitch
        cm.putObj("ly2", lst, elements1, [initP[0], kabe3[1] - dobutiw], [0, 0], math.pi * 3/2) #最上段
        cm.putObj("ly3", lst, elements2, [initP[0] + dobutih, kabe3[1] - dobutiw], [0, -dobuticlr], math.pi * 1/2)  

    # 方杖
    if typ == "片流れ":
        hr = h1agl * math.pi / 180
        elements1 = cm.getFig(h1 + "\n")
        #右肩（図形原点）交点=（傾きi,通る点i,傾きj,通る点j）
        xy = cm.getCrossPoint(slope, gb2, -math.tan(hr), [xlen, gc2[1] - h1pos + 50 / math.cos(hr)])
        #下交点
        b = xy[1] + math.tan(hr) * xy[0]
        y2 = -math.tan(hr) * gt2[0] + b
        hlen = math.sqrt((gt2[0] - xy[0]) ** 2 + (xy[1] - y2) ** 2)
        ele2 = cm.expandfig_x(elements1, 1000, hlen)
        cm.putObj("ly0", lst, ele2, xy, [0, 0], -hr)
        cxyl = [xlen, gc2[1] - h1pos]
        cxyh = cm.getCrossPoint(slope, gc2, -math.tan(hr), cxyl)
        lst.append("lt5\n")
        cm.addLine(lst, cxyh, cxyl)

        pxyl0 = [xlen, gc2[1] - h1pos - 50 / math.cos(hr)]
        pxyl = [xlen - cw/2, pxyl0[1] + cw/2 * math.tan(hr)]
        pxyh = cm.getCrossPoint(slope, gb2, -math.tan(hr), pxyl)
        lth = 100 * math.tan(hr) + 150
        xyl = [pxyl[0] - lth * math.cos(hr), pxyl[1] + lth * math.sin(hr)]
        lth = hlen - 90 - 150
        xyh = [xyl[0] - lth * math.cos(hr), xyl[1] + lth * math.sin(hr)]
        lst.append("lt1\n")
        cm.addLine(lst, pxyh, xyh)
        cm.addLine(lst, pxyl, xyl)

        #ba1 = [(xlen - cw/2 - xy[0]) / 2 + xy[0], (xy[1] - y2) / 2 + y2]
        ba1 = [pxyl[0] - (xyl[0]-xyh[0]) / 3, (xyh[1]-xyl[1]) / 3 + pxyl[1]]
        ba2 = [ba1[0] - 400, ba1[1] - 400]
        strgs = ["方杖:" + h1]
        cm.addBalloon(lst, ba1, ba2, strgs, "cn6\n", "cc2\n", scale)

    # スプライスPL（G1鋼材名ごとにデータが定義されている）
    elements1 = cm.getFig(g1 + "_W\n")
    elements2 = cm.getFig(g1 + "_F\n")
    # 水上側
    if typ == "片流れ":
        xy = cm.getCrossPoint(slope, gc2, -1/slope, [gt2[0]-  850 / math.cos(r), gt2[1]])
        cm.putObj("ly8", lst, elements1, xy, [0, 0], r)
        xy = cm.getCrossPoint(slope, gt2, -1/slope, [gt2[0]-  850 / math.cos(r), gt2[1]])
        cm.putObj("ly8", lst, elements2, xy, [0, 0], r)
        xy = cm.getCrossPoint(slope, gb2, -1/slope, [gt2[0]-  850 / math.cos(r), gt2[1]])
        cm.putObj("ly8", lst, elements2, xy, [0, 0], r + math.pi)
    # 水下側
    xy = cm.getCrossPoint(slope, gc2, -1/slope, [gt1[0]+  850 / math.cos(r), gt1[1]])
    cm.putObj("ly8", lst, elements1, xy, [0, 0], r)
    xy = cm.getCrossPoint(slope, gt1, -1/slope, [gt1[0]+  850 / math.cos(r), gt1[1]])
    cm.putObj("ly8", lst, elements2, xy, [0, 0], r)
    xy = cm.getCrossPoint(slope, gb1, -1/slope, [gt1[0]+  850 / math.cos(r), gt1[1]])
    cm.putObj("ly8", lst, elements2, xy, [0, 0], r + math.pi)

    # 基礎
    ba1 = [240 / 2, 0]
    ba2 = [ba1[0]+200, ba1[1]+200]
    bas = base.split(",")
    mb = list(map(lambda i: float(i[1:]), bas[1].split("x")))
     
    if bas[0] == "束石":
        strg = [base.replace(",", ":")]        
        elements1 = cm.getFig(base.replace(",", "") + "\n")
        cm.putObj("ly0", lst, elements1, [0, 0], [0, 0], 0)
        if typ == "片流れ":
            cm.putObj("ly0", lst, elements1, [xlen, 0], [0, 0], 0)
        ofx = 70
    else:   # 布基礎
        strg = ["布基礎"]
        nulst = []
        nulst.append("lt1\n")
        cm.addLine(nulst, [-mb[0]/2, 0], [-mb[0]/2, -mb[1]+mb[3]])
        cm.addLine(nulst, [-mb[2]/2, -mb[1]+mb[3]], [-mb[0]/2, -mb[1]+mb[3]])
        cm.addLine(nulst, [-mb[2]/2, -mb[1]+mb[3]], [-mb[2]/2, -mb[1]])
        cm.addLine(nulst, [mb[0]/2, 0], [mb[0]/2, -mb[1]+mb[3]])
        cm.addLine(nulst, [mb[2]/2, -mb[1]+mb[3]], [mb[0]/2, -mb[1]+mb[3]])
        cm.addLine(nulst, [mb[2]/2, -mb[1]+mb[3]], [mb[2]/2, -mb[1]])
        cm.addLine(nulst, [-mb[0]/2, 0], [mb[0]/2, 0])
        cm.addLine(nulst, [-mb[2]/2, -mb[1]], [mb[2]/2, -mb[1]])
        cm.addLine(nulst, [-mb[0]/2, -400], [mb[0]/2, -400-mb[0]])
        cm.addLine(nulst, [-mb[0]/2, -440], [mb[0]/2, -440-mb[0]])
        cm.putObj("ly0", lst, nulst, [0, 0], [0, 0], 0)
        if typ == "片流れ":
            nu1 = cm.mirror(nulst, "x", xlen/2)
            nu1 = cm.mirror(nu1, "x", xlen)
            lst.extend(nu1)
        ofx = 0
    cm.addBalloon(lst, ba1, ba2, strg, "cn6\n", "cc0\n", scale)

    # 床
    if "コンクリート" in yuka:
        strgs = yuka.split(",")
        con_t = float(strgs[0].strip("土間コンクリート").strip("mm"))
        for yu in strgs:
            if "切込砂利" in yu:
                ja_t = float(yu.strip("切込砂利").strip("mm"))
        strg = [strgs[1]+","+strgs[2], "床:"+strgs[0]]

        lst.append("lc2\n")        
        if typ == "片流れ":
            cm.addLine(lst, [mb[0]/2 - ofx, fl], [xlen-mb[0]/2 + ofx, fl])
            cm.addLine(lst, [mb[0]/2 - ofx, fl - con_t], [xlen-mb[0]/2 + ofx, fl - con_t])
            cm.addLine(lst, [mb[0]/2 - ofx, fl - con_t - ja_t], [xlen-mb[0]/2 + ofx, fl - con_t - ja_t])
            dx = ja_t * math.tan(math.pi/6)
            ddx = dx / 6
            ddy = ddx / math.tan(math.pi/6)
            x = mb[0] / 2 + dx
            cnt = 0
            while x < xlen - mb[0]/2:
                cm.addLine(lst, [x, fl - con_t], [x - dx , fl - con_t - ja_t])
                cm.addLine(lst, [x - ddx * 2, fl - con_t], [x - ddx , fl - con_t - ddy])
                cm.addLine(lst, [x - ddx * 4, fl - con_t - ja_t], [x - ddx * 5, fl - con_t - ja_t + ddy])
                x = x + ja_t
                if (cnt % 8) == 0:
                    cm.addLine(lst, [x, fl], [x + con_t , fl - con_t])
                    cm.addLine(lst, [x+40, fl], [x+40 + con_t , fl - con_t])
                cnt += 1
            ba1 = [xlen*2/5, fl] # Balloon
        else:
            cm.addLine(lst, [mb[0]/2 - ofx, fl], [xlen/2, fl])
            cm.addLine(lst, [mb[0]/2 - ofx, fl - con_t], [xlen/2, fl - con_t])
            cm.addLine(lst, [mb[0]/2 - ofx, fl - con_t - ja_t], [xlen/2, fl - con_t - ja_t])
            dx = ja_t * math.tan(math.pi/6)
            ddx = dx / 6
            ddy = ddx / math.tan(math.pi/6)
            x = mb[0] / 2 + dx
            cnt = 0
            while x < xlen/2 + ja_t:
                cm.addLine(lst, [x, fl - con_t], [x - dx , fl - con_t - ja_t])
                cm.addLine(lst, [x - ddx * 2, fl - con_t], [x - ddx , fl - con_t - ddy])
                cm.addLine(lst, [x - ddx * 4, fl - con_t - ja_t], [x - ddx * 5, fl - con_t - ja_t + ddy])
                x = x + ja_t
                if (cnt % 8) == 0:
                    cm.addLine(lst, [x, fl], [x + con_t , fl - con_t])
                    cm.addLine(lst, [x+40, fl], [x+40 + con_t , fl - con_t])
                cnt += 1                
            ba1 = [xlen/5, fl] # Balloon
        ba2 = [ba1[0]+300, ba1[1]+300]
        cm.addBalloon(lst, ba1, ba2, strg, "cn6\n", "cc0\n", scale)

    # GL
    lst.append("lt6\n")
    if typ == "片流れ":
        cm.addLine(lst, [-500, gl], [xlen+500, gl])
    else:
        cm.addLine(lst, [-500, gl], [xlen/2, gl])
        try:
            cm.addLine(lst, [xlen/2, pt2[1]], [xlen/2, fl - con_t - ja_t])
        except:
            cm.addLine(lst, [xlen/2, pt2[1]], [xlen/2, gl])            
    lst.append("lt1\n")
    glele = cm.getFig("GL記号\n")
    cm.putObj("ly1",lst, glele, [-mb[0]/2 + ofx, gl], [0, 0], 0)
    cm.addstring(lst, [-mb[0]/2 + ofx, gl], [1000, gl], "G.L ", "cn5\n", "cc2\n")
    
    return pb1, pb2, pt1, pt2, hf1, hf2, yaku1, yaku3, klc, krc, klb2, krb2, kabe1, kabe2, kabe3

def putC(ly, lst, x, nh, gb, scale):
    #柱
    pb1 = [x+cw/2, 0]
    pb2 = [x-cw/2, 0]
    pt1 = [x+cw/2, nh+ry+grw-tnt/math.cos(r)]
    pt2 = [x-cw/2, nh-ry+grw-tnt/math.cos(r)]
    pbc = [x, 0]
    ptc = [x, nh+grw-tnt/math.cos(r)]
    #mc.append(mc[2])   #柱が角鋼の時
    pfb1 = [pb1[0]-mc[3], base_t]
    pft1 = [pt1[0]-mc[3], pt1[1]-mc[3]*math.tan(r)]
    pfb2 = [pb2[0]+mc[3], base_t]
    pft2 = [pb2[0]+mc[3], pt2[1]+mc[3]*math.tan(r)]
    gpb1 = [pfb1[0], gb[1]]
    gpb2 = [pfb2[0], gb[1]]
    gpt1 = [pfb1[0], gb[1] + 9]
    gpt2 = [pfb2[0], gb[1] + 9]
    lst.append(ly+"\n")
    lst.append("lt1\n")
    lst.append("lc2\n")
    cm.addBox(lst, pb1, pb2, pt1, pt2)
    cm.addflg(lst, pfb1, pft1, pfb2, pft2)
    cm.addLine(lst, [x+cw/2, base_t], [x-cw/2, base_t])
    lst.append("lt5\n"); cm.addLine(lst, pbc, ptc); lst.append("lt1\n")
    cm.addLine(lst, gpb1, gpb2)
    cm.addLine(lst, gpt1, gpt2)
    elements = cm.getFig("ブレースPL側面\n")
    cm.putObj("ly4", lst, elements, [x, gb[1]], [0, 0], math.pi)
    cm.putObj("ly4", lst, elements, [x, 100], [0, 0], 0)
    #C天板
    lst.append("lt1\n")
    lst.append("ly0\n")
    ptb1 = pt1
    ptb2 = [x-cw/2+dtn, pt2[1]+dtn*math.tan(r)]
    ptt1 = [x+cw/2-dtn, pt1[1]+tnt*math.cos(r)]
    ptt2 = [x-cw/2, pt2[1]+tnt/math.cos(r)]
    cm.addBox(lst, ptb1, ptb2, ptt1, ptt2)

def putG(ly, lst, scale, typ):
    # 梁
    gt1 = [cw/2, nh+ry+grw]
    gb1 = [cw/2, nh+ry-grw]
    
    gt2 = [xlen-cw/2, gt1[1] + (xlen-cw) * math.tan(r)]
    gb2 = [xlen-cw/2, gb1[1] + (xlen-cw) * math.tan(r)]
    gt3 = [xlen/2 - hari_t, gt1[1] + ((xlen/2-cw/2 - hari_t) * math.tan(r))]
    gb3 = [xlen/2 - hari_t, gb1[1] + ((xlen/2-cw/2 - hari_t) * math.tan(r))]
    # 切妻水上brsPL座標
    gt4 = [xlen/2 - hari_t - 200, gt1[1] + ((xlen/2-cw/2 - hari_t -200) * math.tan(r))]
    gb4 = [xlen/2 - hari_t - 200, gb1[1] + ((xlen/2-cw/2 - hari_t -200) * math.tan(r))]

    gc1 = [0, (gt1[1]+gb1[1])/2 - cw/2*math.tan(r)]
    gc2 = [xlen, (gt2[1]+gb2[1])/2 + cw/2*math.tan(r)]
    gc3 = [xlen/2 - hari_t, (gt1[1]+gb1[1])/2 + (xlen/2 - cw/2 - hari_t) * math.tan(r)]    

    pfb1 = [gb1[0], gb1[1]+mg[3]/math.cos(r)]
    pfb2 = [gb2[0], gb2[1]+mg[3]/math.cos(r)]
    pfb3 = [gb3[0], gb3[1]+mg[3]/math.cos(r)]
    pft1 = [gt1[0], gt1[1]-mg[3]/math.cos(r)]
    pft2 = [gt2[0], gt2[1]-mg[3]/math.cos(r)]
    pft3 = [gt3[0], gt3[1]-mg[3]/math.cos(r)]
    
    lst.append(ly+"\n")
    lst.append("lc2\n")    
    if typ == "片流れ":
        cm.addBox(lst, gb1, gb2, gt1, gt2)
        cm.addflg(lst, pfb1, pfb2, pft1, pft2)
        lst.append("lt5\n"); cm.addLine(lst, gc1, gc2); lst.append("lt1\n")
    else:
        pllth = gt3[1] - gb3[1]
        pllth = round(pllth * 1.1 / 10) * 10 / 2
        plx1 = gc3[0]; plx2 = xlen/2; ply1 = gc3[1] + pllth; ply2 = ply1 - pllth * 2
        cm.addBox(lst, [plx1, ply1], [plx2, ply1], [plx1, ply2], [plx2, ply2])
        cm.addBox(lst, gb1, gb3, gt1, gt3)
        cm.addflg(lst, pfb1, pfb3, pft1, pft3)
        lst.append("lt5\n"); cm.addLine(lst, gc1, gc3); lst.append("lt1\n")
        gt3 = [xlen/2, gt1[1] + ((xlen/2-cw/2) * math.tan(r))]

    gp = [gt1[0], (gt1[1]+gb1[1])/2]    # ブレースPL
    gp1 = [gp[0] + 3*math.tan(r)*math.cos(r), gp[1] + 3*math.tan(r)*math.sin(r)]
    if typ == "片流れ":
        gp = [gt2[0], (gt2[1]+gb2[1])/2]
    else:
        gp = [gt4[0], (gt4[1]+gb4[1])/2]
    gp2 = [gp[0] - 3*math.tan(r)*math.cos(r), gp[1] - 3*math.tan(r)*math.sin(r)]
    gpm = [gp1[0] +(gp2[0]-gp1[0])/2, gp1[1] +(gp2[1]-gp1[1])/2]
    gpm1 = [gp1[0] +(gp2[0]-gp1[0])/3, gp1[1]+(gp2[1]-gp1[1])/3]
    gpm2 = [gp1[0] +(gp2[0]-gp1[0])*2/3, gp1[1]+(gp2[1]-gp1[1])*2/3]

    elements = cm.getFig("ブレースPL側面\n")
    cm.putObj("ly4", lst, elements, gp1, [0, 0], r - math.pi/2)
    cm.putObj("ly4", lst, elements, gp2, [0, 0], r + math.pi/2)
    if ybrsnum == 2:    # 屋根ブレース2段
        cm.putObj("ly4", lst, elements, gpm, [0, 0], r - math.pi/2)
        cm.putObj("ly4", lst, elements, gpm, [0, 0], r + math.pi/2)
    elif ybrsnum == 3:  # 屋根ブレース3段
        cm.putObj("ly4", lst, elements, gpm1, [0, 0], r - math.pi/2)
        cm.putObj("ly4", lst, elements, gpm1, [0, 0], r + math.pi/2)
        cm.putObj("ly4", lst, elements, gpm2, [0, 0], r - math.pi/2)
        cm.putObj("ly4", lst, elements, gpm2, [0, 0], r + math.pi/2)

    if typ == "切妻":
        elements = cm.getFig(tb + "\n") # タイバー
        tbinip = [gpm[0] + gw/2/math.sin(r) + 37.5/math.tan(r) , gpm[1] + 37.5]
        elements = cm.expandfig_x(elements, 600, xlen/2 - tbinip[0])
        cm.putObj("ly0", lst, elements, tbinip, [0, 0], 0)
        cm.addLine(lst, [tbinip[0] - 75/math.tan(r), tbinip[1] - 75], [tbinip[0] + 80, tbinip[1] - 75])
        lst.append("lt5\n")
        cm.addLine(lst, gpm, [xlen/2, gpm[1]])  # centerline
        strgs = ["ﾀｲﾊﾞｰ:" + tb]
        ba1 = [tbinip[0] + 650, tbinip[1] - 45.5]
        ba2 = [ba1[0] + 300, ba1[1] - 300]
        cm.addBalloon(lst, ba1, ba2, strgs, "cn6\n", "cc0\n", scale)

    if typ == "片流れ":
        ba1 = [(gc2[0]-gc1[0])*1/2, (gc2[1]-gc1[1])*1/2+nh + (gw/2+30)/math.cos(r)] # Balloon
    else:
        ba1 = [(gc2[0]-gc1[0])*1/3, (gc2[1]-gc1[1])*1/3+nh + (gw/2+30)/math.cos(r)] # Balloon
    ba2 = [ba1[0]-400, ba1[1]+400]
    strgs = ["母屋:"+moya, "屋根下地:"+sitaji, "屋根:"+yane]
    cm.addBalloon(lst, ba1, ba2, strgs, "cn6\n", "cc2\n", scale)
    if typ == "片流れ":
        ba1 = [gb1[0] +(gb2[0]-gb1[0])*1/3, gb1[1] +(gb2[1]-gb1[1])*1/3]
    else:
        ba1 = [gb1[0] +(gb2[0]-gb1[0])*1/6, gb1[1] +(gb2[1]-gb1[1])*1/6]
    ba2 = [ba1[0]+400, ba1[1]-400]
    strgs = ["梁:" + g1]
    cm.addBalloon(lst, ba1, ba2, strgs, "cn6\n", "cc0\n", scale)

    return gt1, gc1, gb1, gt2, gc2, gb2, gt3

def putNoki_L(ly, lst, x):
    pt1 = [x-cw/2, nh-ry+grw]
    pb1 = [x-cw/2, nh-ry+grw-nrw]
    pt2 = [pt1[0]-nokilen*math.cos(r), pt1[1]-nokilen*math.sin(r)]
    pb2 = [pt2[0]+mn[0]*math.sin(r), pt2[1]-mn[0]*math.cos(r)]
    pc1 = [pt1[0], (pt1[1]+pb1[1])/2]
    pc2 = [(pt2[0]+pb2[0])/2, (pt2[1]+pb2[1])/2]
    #mn.append(mn[2])   #柱が角鋼の時
    pfb1 = [pb1[0], pb1[1]+mn[3]/math.cos(r)]
    pfb2 = [pb2[0]-mn[3]*math.sin(r), pb2[1]+mn[3]*math.cos(r)]
    pft1 = [pt1[0], pt1[1]-mn[3]/math.cos(r)]
    pft2 = [pt2[0]+mn[3]*math.sin(r), pt2[1]-mn[3]*math.cos(r)]    
    initP = pt2
    lst.append(ly+"\n")
    lst.append("lc2\n")
    cm.addBox(lst, pb1, pb2, pt1, pt2)
    cm.addflg(lst, pfb1, pfb2, pft1, pft2)
    lst.append("lt5\n"); cm.addLine(lst, pc1, pc2); lst.append("lt1\n")
    return initP

def putNoki_U(ly, lst, x):
    pt2 = [x+cw/2, nh+ry+grw+(xlen-0)*math.tan(r)]
    pb2 = [x+cw/2, nh+ry+grw+(xlen-0)*math.tan(r)-nrw]
    pt1 = [pt2[0]+nokilen*math.cos(r), pt2[1]+nokilen*math.sin(r)]
    pb1 = [pt1[0]+mn[0]*math.sin(r), pt1[1]-mn[0]*math.cos(r)]
    pc1 = [pt2[0], (pt2[1]+pb2[1])/2]
    pc2 = [(pt1[0]+pb1[0])/2, (pt1[1]+pb1[1])/2]
    pfb1 = [pb1[0]-mn[3]*math.sin(r), pb1[1]+mn[3]/math.cos(r)]
    pfb2 = [pb2[0], pb2[1]+mn[3]*math.cos(r)]
    pft1 = [pt1[0]+mn[3]*math.sin(r), pt1[1]-mn[3]/math.cos(r)]
    pft2 = [pt2[0], pt2[1]-mn[3]*math.cos(r)]        
    endP = pt1
    lst.append(ly+"\n")
    lst.append("lc2\n")   
    cm.addBox(lst, pb1, pb2, pt1, pt2)
    cm.addflg(lst, pfb1, pfb2, pft1, pft2)
    lst.append("lt5\n"); cm.addLine(lst, pc1, pc2); lst.append("lt1\n")
    return endP

def putYane(ly, lst, initP, endP, typ):
    lst.append(ly+"\n")
    lst.append("lc4\n")
    if typ == "片流れ":
        sj0 = [initP[0] - (moyah + moyaclr) * math.sin(r), initP[1] + (moyah + moyaclr) * math.cos(r)]    #下地
        sj1 = [endP[0] - (moyah + moyaclr) * math.sin(r), endP[1] + (moyah + moyaclr) * math.cos(r)]    
        sjt0 = [sj0[0]-sitaji_t*math.sin(r), sj0[1]+sitaji_t*math.cos(r)]
        sjt1 = [sj1[0]-sitaji_t*math.sin(r), sj1[1]+sitaji_t*math.cos(r)]
    else:
        sj0 = [initP[0] - (moyah + moyaclr) * math.sin(r), initP[1] + (moyah + moyaclr) * math.cos(r)]    #下地
        sj1 = [endP[0], endP[1] + (moyah + moyaclr) / math.cos(r)]    
        sjt0 = [sj0[0]-sitaji_t*math.sin(r), sj0[1]+sitaji_t*math.cos(r)]
        sjt1 = [sj1[0], sj1[1]+sitaji_t / math.cos(r)]
    cm.addLine(lst, sj0, sj1)
    if typ == "片流れ":
        pb1 = [sj0[0]-sitaji_t*math.sin(r)-48*math.cos(r), sj0[1]+sitaji_t*math.cos(r)-48*math.sin(r)]  #屋根
        pt1 = [pb1[0]-yane_t*math.sin(r), pb1[1]+yane_t*math.cos(r)]
        pb2 = [sj1[0]-sitaji_t*math.sin(r)+48*math.cos(r), sj1[1]+sitaji_t*math.cos(r)+48*math.sin(r)]
        pt2 = [pb2[0]-yane_t*math.sin(r), pb2[1]+yane_t*math.cos(r)]
    else:
        pb1 = [sj0[0]-sitaji_t*math.sin(r)-48*math.cos(r), sj0[1]+sitaji_t*math.cos(r)-48*math.sin(r)]  #屋根
        pt1 = [pb1[0]-yane_t*math.sin(r), pb1[1]+yane_t*math.cos(r)]
        pb2 = [sj1[0], sj1[1]+sitaji_t/math.cos(r)]
        pt2 = [pb2[0], pb2[1]+yane_t/math.cos(r)]
    cm.addBox(lst, pb1, pb2, pt1, pt2)

    hft1 = [sjt1[0]+hafut*math.cos(r), sjt1[1]+hafut*math.sin(r)] #破風板
    ele2 = cm.getFig("木-45x60\n")
    ele2 = cm.expandfig_x(ele2, 30, hafut)
    ele2 = cm.expandfig_y(ele2, 30, hafuyakuw[0])
    cm.putObj("ly3", lst, ele2, sjt0, [0, 0], math.pi+r)
    if typ == "片流れ":
        cm.putObj("ly3", lst, ele2, hft1, [0, 0], math.pi+r)
    # 役物
    yaku0 = [sjt0[0]-(hafut*math.cos(r)-hafuyakuw[0]*math.sin(r)), sjt0[1]-(hafut*math.sin(r)+hafuyakuw[0]*math.cos(r))]
    yaku1 = [sjt0[0]-(hafut*math.cos(r)-hafuyakuw[1]*math.sin(r)), sjt0[1]-(hafut*math.sin(r)+hafuyakuw[1]*math.cos(r))]
    yaku2 = [hft1[0]-(0*math.cos(r)-hafuyakuw[0]*math.sin(r)), hft1[1]-(0*math.sin(r)+hafuyakuw[0]*math.cos(r))]
    yaku3 = [hft1[0]-(0*math.cos(r)-hafuyakuw[1]*math.sin(r)), hft1[1]-(0*math.sin(r)+hafuyakuw[1]*math.cos(r))]
    cm.addLine(lst, yaku0, yaku1)
    hf1 = cm.getCrossPointby4P(pb1, pb2, yaku0, yaku1)
    hf2 = cm.getCrossPointby4P(pb1, pb2, yaku2, yaku3)
    if typ == "片流れ":
        cm.addLine(lst, yaku2, yaku3)

    k1 = [-cw/2 - dobutih - dobuticlr, 0]
    k3 = [k1[0], 1]
    xy1 = cm.getCrossPointby4P(yaku1, yaku3, k1, k3)
    cm.addLine(lst, yaku1, xy1)
    k1 = [xlen+cw/2+ dobutih + dobuticlr, 0]
    k3 = [k1[0], 1]
    xy2 = cm.getCrossPointby4P(yaku1, yaku3, k1, k3)
    if typ == "片流れ":        
        cm.addLine(lst, yaku3, xy2)
    k1 = [xlen+cw/2, 0]
    k3 = [k1[0], 1]
    xy3 = cm.getCrossPointby4P(yaku1, yaku3, k1, k3)

    klt1 = [xy1[0], xy1[1]+5]  #左壁
    klt2 = [klt1[0]-kabe_t, klt1[1]]
    klb2 = [klt2[0], 0]
    klb1 = [klt1[0], 0]
    klc = cm.getCrossPointby4P(yaku1, yaku3, klt2, klb2)
    cm.addBox(lst, klt1, klt2, klb1, klb2)

    krt1 = [xy2[0], xy2[1]+10]  #右壁
    krt2 = [krt1[0]+kabe_t, krt1[1]]
    krb2 = [krt2[0], 0]
    krb1 = [krt1[0], 0]
    krc = cm.getCrossPointby4P(yaku1, yaku3, krt2, krb2)    
    if typ == "片流れ":
        cm.addBox(lst, krt1, krt2, krb1, krb2)

    if typ == "切妻":    
        hf2 = cm.getCrossPointby4P(hf1, hf2, [xlen/2, 0], [xlen/2, 10])
        yaku3 = cm.getCrossPointby4P(yaku1, yaku3, [xlen/2, 0], [xlen/2, 10])

    return pb1, pb2, pt1, pt2, hf1, hf2, yaku1, yaku3, klc, krc, klb2, krb2, xy1, xy2, xy3

def editRitu1(tlst, pb1, pb2, pt1, pt2, hf1, hf2, yaku1, yaku3, klc, krc, klb2, krb2, typ):
    tlst.clear()
    tlst.append("lg0\n")
    tlst.append("lc4\n")    #線色:黄
    tlst.append("ly0\n")
    cm.addBox(tlst, pb1, pb2, pt1, pt2)
    cm.addBox(tlst, hf1, yaku1, hf2, yaku3)
    cm.addLine(tlst, klc, klb2)
    kisolt = [-120, 0]; kisolb = [-120, gl]   #基礎
    kisort = [xlen+120, 0]; kisorb = [xlen+120, gl]
    cm.addLine(tlst, kisolt, kisolb)
    cm.addLine(tlst, kisolb, kisorb)

    if typ == "片流れ":
        xlim = krc[0]
        cm.addLine(tlst, krc, krb2)
    else:
        xlim = xlen/2
    #壁ハッチング
    tlst.append("ly4\n")    
    x = klc[0] + ((krc[0] - klc[0]) % pitch) / 2
    while x <= xlim:
        tp = cm.getCrossPointby4P(yaku1, yaku3, [x, 0], [x, 1])
        cm.addLine(tlst, tp, [x, 0])
        x += pitch
    tlst.append("ly0\n")
    if typ == "切妻":
        tmplst = cm.mirror(tlst, "x", xlen/2)
        tlst.extend(tmplst)    
    cm.addLine(tlst, kisorb, kisort)
    cm.addLine(tlst, klb2, krb2) 


def editRituB(lst, pb1, pb2, pt1, pt2, hf1, hf2, yaku1, yaku3, klc, krc, klb2, krb2):
    lst.append("lg0\n")
    lst.append("lc4\n")    #線色:黄
    lst.append("ly0\n")
    side = cd/2 + dobutiw + kabe_t  # B立面
    ylt = [-side-250, pt2[1]]; yrt = [ylen + side+250, pt2[1]]; ylb = [-side-250, yaku1[1]]; yrb = [ylen + side+250, yaku1[1]] 
    yl2 = [-side-250, pb1[1]]; yr2 = [ylen + side+250, pb1[1]]
    yl3 = [-side-250, pt1[1]]; yr3 = [ylen + side+250, pt1[1]]    
    cm.addBox(lst, ylt, yrt, ylb, yrb)
    cm.addLine(lst, yl2, yr2)
    cm.addLine(lst, yl3, yr3)
    cm.addBox(lst, [-side, yaku1[1]], [ylen + side, yaku1[1]], [-side, 0], [ylen + side, 0])
    kisolt = [-60, 0]; kisolb = [-60, gl]   #基礎
    kisort = [ylen+60, 0]; kisorb = [ylen+60, gl]
    cm.addLine(lst, kisolt, kisolb)
    cm.addLine(lst, kisolb, kisorb)
    cm.addLine(lst, kisorb, kisort)
    #屋根ハッチング
    lst.append("ly4\n")
    lst.append("lc8\n")
    x = ylt[0] + ((yrt[0] - ylt[0]) % ypitch) / 2
    while x < yrt[0]:
        tp = cm.getCrossPointby4P(ylt, yrt, [x, 0], [x, 1])
        cm.addLine(lst, tp, [x, yl3[1]])
        x += ypitch
    lst.append("lc4\n")
        #壁ハッチング
    x = -side + ((ylen+side + side) % pitch) / 2
    while x < ylen + side:
        tp = cm.getCrossPointby4P(ylb, yrb, [x, 0], [x, 1])
        cm.addLine(lst, tp, [x, 0])
        x += pitch

def editRituA(lst, pb1, pb2, pt1, pt2, hf1, hf2, yaku1, yaku3, klc, krc, klb2, krb2):
    lst.append("lg0\n")
    lst.append("lc4\n")    #線色:黄
    lst.append("ly0\n")
    side = cd/2 + dobutiw + kabe_t  # A立面
    ylt = [-side-250, pt2[1]]; yrt = [ylen + side+250, pt2[1]]; ylb = [-side-250, yaku3[1]]; yrb = [ylen + side+250, yaku3[1]] 
    cm.addBox(lst, ylt, yrt, ylb, yrb)
    cm.addLine(lst, [-side-250, hf2[1]], [ylen + side+250, hf2[1]])
    cm.addLine(lst, [-side-250, yaku1[1]], [-side, yaku1[1]])
    cm.addLine(lst, [ylen + side, yaku1[1]], [ylen + side + 250, yaku1[1]]) 
    cm.addLine(lst, [-side-250, yaku1[1]], ylb)
    cm.addLine(lst, [ylen + side+250, yaku1[1]], yrb)
    yl4 = [-side, krc[1]]; yr4 = [ylen + side, krc[1]]
    yl5 = [-side, 0]; yr5 = [ylen + side, 0]
    cm.addBox(lst, yl4, yr4, yl5, yr5)
    kisolt = [-60, 0]; kisolb = [-60, gl]   #基礎
    kisort = [ylen+60, 0]; kisorb = [ylen+60, gl]
    cm.addLine(lst, kisolt, kisolb)
    cm.addLine(lst, kisolb, kisorb)
    cm.addLine(lst, kisorb, kisort)
    #壁ハッチング
    lst.append("ly4\n")
    x = -side + ((ylen+side + side) % pitch) / 2
    while x < ylen + side:
        tp = cm.getCrossPointby4P(yl4, yr4, [x, 0], [x, 1])
        cm.addLine(lst, tp, [x, 0])
        x += pitch

def editHeimen(lst):
    mgn = 400
    lst.append("lc2\n")
    lst.append("ly0\n")
    ele = cm.getFig(c1 + "\n")
    for Ax in toriA:
        cm.putObj("lg0", lst, ele, [Ax, 0], [0 ,0], 0)
    for Bx in toriB:
        cm.putObj("lg0", lst, ele, [Bx, xlen], [0 ,0], 0)
    ele = cm.getFig(m1 + "\n")
    for y1 in tori1:
        if y1 != 0 and y1 != xlen:
            cm.putObj("lg0", lst, ele, [0, y1], [0, 0], math.pi/2)
    for Ey in toriE:
        if Ey != 0 and Ey != xlen:
            cm.putObj("lg0", lst, ele, [ylen, Ey], [0, 0], math.pi/2)
    lst.append("lt5\n")
    #lst.append("ly0\n")
    for Ax in toriA:    # 柱芯線
        if Ax == 0 or Ax == ylen:
            cm.addLine(lst, [Ax, -mgn], [Ax, xlen + mgn])
        else:
            cm.addLine(lst, [Ax, -mgn], [Ax, mgn])
    for Bx in toriB:
        if Bx != 0 and Bx != ylen:
            cm.addLine(lst, [Bx, xlen - mgn], [Bx, xlen + mgn])
    for y1 in tori1:
        if y1 == 0 or y1 == xlen:
            cm.addLine(lst, [-mgn, y1], [ylen + mgn, y1])
        else:
            cm.addLine(lst, [-mgn, y1], [mgn, y1])
    for Ey in toriE:
        if Ey != 0 and Ey != xlen:
            cm.addLine(lst, [ylen - mgn, Ey], [ylen + mgn, Ey])        
    lst.append("lt1\n")
    lst.append("lc4\n")
    dx = mw/2 + dobutih
    dy = cw/2 + dobutih
    lb1 = [-dx, -dy]; lt1 = [-dx, xlen + dy]; rt1 = [ylen + dx, xlen + dy]; rb1 = [ylen + dx, -dy]
    lb2 = [-dx-kabe_t, -dy-kabe_t]; lt2 = [-dx-kabe_t, xlen + dy+kabe_t]; rt2 = [ylen + dx+kabe_t, xlen + dy+kabe_t]; rb2 = [ylen + dx+kabe_t, -dy-kabe_t]
    cm.addBox(lst, lb1, rb1, lt1, rt1)
    cm.addBox(lst, lb2, rb2, lt2, rt2)
