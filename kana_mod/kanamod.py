import math, re
import numpy as np
import unicodedata

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

#--------------------
dic = {}    # 部材ディクショナリ作成
dic0 = {}
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
door_vol = len([ke for ke in dic.keys() if ("框ドア" in ke)])

xlen = float(dic["妻方向柱芯全長"])
ylen = float(dic["軒方向柱芯全長"])
nh = float(dic["軒高"])
slp = dic["屋根勾配"].split("/")
slope = float(slp[0])/float(slp[1])

c1 = dic["C1鋼材"]
g1 = dic["G1鋼材"]
m1 = dic["P1鋼材"]
nk = dic["軒先鋼材"]
h1 = dic["方杖鋼材"]
moya = dic["母屋材"]
dobuti = dic["胴縁材"]
base = dic["基礎材"]
#base = "布基礎"
sitaji = dic["屋根下地"]

tnt = float(dic["C1天板厚"])
base_t = float(dic["BPL厚"])
nokilen = float(dic["軒先長"])
sitaji_t = float(dic["屋根下地厚"])
yane_t = float(dic["屋根材厚"])
kabe_t = float(dic["壁材厚"])
kiso_h = float(dic["基礎天端高"])
gl = -kiso_h
pitch = float(dic["壁ハッチングピッチ"])
#--------------------

r = math.atan(slope)
mc = list(map(float, c1[2:].split("x")))
mg = list(map(float, g1[2:].split("x")))
mn = list(map(float, nk[2:].split("x")))
mm = list(map(float, m1[2:].split("x")))
mmoya = list(map(float, moya[2:].split("x")))
mdobuti = list(map(float, dobuti[2:].split("x")))
mbase = list(map(float, base[2:].split("x")))
cw = mc[0]; cd = mc[1]
gw = mg[0]; gd = mg[1]
nw = mn[0]; ng = mn[1]
mw = mm[0]; md = mm[1]
moyaw = mmoya[0]
moyah = mmoya[1]
dobutiw = mdobuti[0]
dobutih = mdobuti[1]
kisoh = mbase[1]
hafuyakuw = [220, 230] if moyaw + nw + sitaji_t > 181 else [180, 190]
hafut = 24 if moyaw + nw + sitaji_t > 181 else 18
ry = cw/2 * math.tan(r)
grw = gw/2/math.cos(r)
crw = cw/1/math.cos(r)
nrw = nw/1/math.cos(r)
dtn = tnt*math.sin(r)
initP = []
endP = []
initGT = []
initHP = []
initGB = []
ofs_kana = [15000, 2000]
ofs_ritu1, ofs_rituA = [36000, 30000], [8000, 10000]
ofs_rituE, ofs_rituB = [56000, 30000], [8000, 24000]
ofs_hei = [8000, 36000]
lg = "lg0"; ly = "ly0"; lt = "lt0"; lc = "lc0"
conf = {"lg":lg, "ly":ly, "lt":lt, "lc":lc, "ofs":ofs_kana}
tlst = []
cmdlist = ["pt", "ci", "ch", "cc*", "cn*", ""]
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

def setconf(llst, conf):
    global lg, ly, lt, lc
    if conf[lg] != lg:
        lg = conf[lg]; llst.append(conf[lg+"\n"])
    if conf[ly] != ly:
        ly = conf[ly]; llst.append(conf[ly+"\n"])
    if conf[lt] != lt:
        lt = conf[lt]; llst.append(conf[lt+"\n"])
    if conf[lc] != lc:
        lc = conf[lc]; llst.append(conf[lc+"\n"])

def addBox(llst, p1, p2, p3, p4):
    n1 = np.array(p1); n2 = np.array(p2); n3 = np.array(p3); n4 = np.array(p4)
    pb1 = n1 + ofs; pb2 = n2 + ofs; pt1 = n3 + ofs; pt2 = n4 + ofs
    line = "{} {} {} {}\n".format(pb1[0], pb1[1], pb2[0], pb2[1]); llst.append(line)
    line = "{} {} {} {}\n".format(pb1[0], pb1[1], pt1[0], pt1[1]); llst.append(line)
    line = "{} {} {} {}\n".format(pt2[0], pt2[1], pt1[0], pt1[1]); llst.append(line)
    line = "{} {} {} {}\n".format(pt2[0], pt2[1], pb2[0], pb2[1]); llst.append(line)
def addcent(llst, p1, p2):
    n1 = np.array(p1); n2 = np.array(p2)
    pb1 = n1 + ofs; pb2 = n2 + ofs    
    line = "{} {} {} {}\n".format(pb1[0], pb1[1], pb2[0], pb2[1]); llst.append(line)
def addflg(llst, p1, p2, p3, p4):
    n1 = np.array(p1); n2 = np.array(p2); n3 = np.array(p3); n4 = np.array(p4)
    pb1 = n1 + ofs; pb2 = n2 + ofs; pt1 = n3 + ofs; pt2 = n4 + ofs    
    line = "{} {} {} {}\n".format(pb1[0], pb1[1], pb2[0], pb2[1]); llst.append(line)
    line = "{} {} {} {}\n".format(pt1[0], pt1[1], pt2[0], pt2[1]); llst.append(line)
def addpoint(llst, p1):
    n1 = np.array(p1)
    pb1 = n1 + ofs    
    line = "pt {} {}\n".format(pb1[0], pb1[1]); llst.append(line)    
def addstring(llst, p1, p2, strg, cn, cc):
    llst.append(cc)
    if cc == "cc1\n":
        x = (p1[0] + p2[0]) / 2; y = (p1[1] + p2[1]) / 2
    else:
        x = p1[0]; y = p1[1]
    x1 = x + ofs[0]; y1 = y + ofs[1]
    dx = p2[0] - p1[0]; dy = p2[1] - p1[1]
    llst.append(cn)
    line = "ch {} {} {} {} \"{}\n".format(x1, y1, dx, dy, strg); llst.append(line)

def addBalloon(llst, p1, p2, strgs, cn, cc):
    llst.append("lc1\n")    #線色:青
    llst.append("lt1\n")
    llst.append("ly1\n")
    llst.append("lg8\n")
    n1 = np.array(p1); n2 = np.array(p2)
    pb1 = n1 + ofs; pb2 = n2 + ofs
    line = "{} {} {} {}\n".format(pb1[0], pb1[1], pb2[0], pb2[1]); llst.append(line)
    line = "{} {} {} {}\n".format(pb2[0], pb2[1]+160*(len(strgs)-1), pb2[0], pb2[1]); llst.append(line)
    dirx = 1 if p2[0] > p1[0] else -1
    diry = 1 if p2[1] > p1[1] else -1    
    cnt = 0
    y0 = p2[1]
    for strg in strgs:
        y = y0 + diry * cnt * 160
        lth = strlth(strg)
        p2 = [p2[0], y]
        p3 = [p2[0] + lth * 70, y]
        n2 = np.array(p2);  pb2 = n2 + ofs       
        n3 = np.array(p3);  pb3 = n3 + ofs
        addstring(llst, p2, p3, strg, cn, cc)   #文字列はaddstring()でofs適用されるのでここでは元値を指定する
        if dirx < 0:
            dx = pb3[0] - pb2[0]
            x2 = pb2[0] - dx; x3 = pb3[0] -dx
        else:
            x2 = pb2[0]; x3 = pb3[0]
        line = "{} {} {} {}\n".format(x2, pb3[1], x3, pb3[1]); llst.append(line)
        cnt += 1

def strlth(text):   #全角を2文字と数えた文字列長
    count = 0
    for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
            count += 2
        else:
            count += 1
    return count

def putC(ly, llst, x, nh):
    #柱
    pb1 = [x+cw/2, 0]
    pb2 = [x-cw/2, 0]
    pt1 = [x+cw/2, nh+ry+grw-tnt/math.cos(r)]
    pt2 = [x-cw/2, nh-ry+grw-tnt/math.cos(r)]
    pbc = [x, 0]
    ptc = [x, nh+grw-tnt/math.cos(r)]
    pfb1 = [pb1[0]-mc[3], base_t]
    pft1 = [pt1[0]-mc[3], pt1[1]-mc[3]*math.tan(r)]
    pfb2 = [pb2[0]+mc[3], base_t]
    pft2 = [pb2[0]+mc[3], pt2[1]+mc[3]*math.tan(r)]
 
    llst.append(ly+"\n")
    llst.append("lt1\n")
    llst.append("lc2\n")
    addBox(llst, pb1, pb2, pt1, pt2)
    addflg(llst, pfb1, pft1, pfb2, pft2)
    addcent(llst, [x+cw/2, base_t], [x-cw/2, base_t])
    llst.append("lt5\n"); addcent(llst, pbc,ptc); llst.append("lt1\n")
    #C天板
    ptb1 = pt1
    ptb2 = [x-cw/2+dtn, pt2[1]+dtn*math.tan(r)]
    ptt1 = [x+cw/2-dtn, pt1[1]+tnt*math.cos(r)]
    ptt2 = [x-cw/2, pt2[1]+tnt/math.cos(r)]
    addBox(llst, ptb1, ptb2, ptt1, ptt2)

    ba1 = [-cw/2-30, 1000]
    ba2 = [ba1[0]+400, ba1[1]+400]
    strgs = ["胴縁:"+dobuti, "壁:角波カラートタン 0.27mm"]
    addBalloon(llst, ba1, ba2, strgs, "cn6\n", "cc0\n")
    ba1 = [cw/2, 2000]
    ba2 = [ba1[0]+300, ba1[1]+300]
    strgs = ["柱:" + c1]
    addBalloon(llst, ba1, ba2, strgs, "cn6\n", "cc0\n")

def putG(ly, llst):#, initHP, initGB):
    #梁
    pt1 = [cw/2, nh+ry+grw]
    pb1 = [cw/2, nh+ry-grw]
    pt2 = [xlen-cw/2, nh+ry+grw+(xlen-cw)*math.tan(r)]
    pb2 = [xlen-cw/2, nh+ry-grw+(xlen-cw)*math.tan(r)]
    pc1 = [0, (pt1[1]+pb1[1])/2 - cw/2*math.tan(r)]
    pc2 = [xlen, (pt2[1]+pb2[1])/2 + cw/2*math.tan(r)]
    pfb1 = [pb1[0], pb1[1]+mg[3]/math.cos(r)]
    pfb2 = [pb2[0], pb2[1]+mg[3]/math.cos(r)]
    pft1 = [pt1[0], pt1[1]-mg[3]/math.cos(r)]
    pft2 = [pt2[0], pt2[1]-mg[3]/math.cos(r)]
    llst.append(ly+"\n")
    llst.append("lc2\n")    
    addBox(llst, pb1,pb2,pt1,pt2)
    addflg(llst, pfb1, pfb2, pft1, pft2)
    llst.append("lt5\n"); addcent(llst, pc1,pc2); llst.append("lt1\n")

    ba1 = [(pc2[0]-pc1[0])*1/2, (pc2[1]-pc1[1])*1/2+nh]
    ba2 = [ba1[0]-400, ba1[1]+400]
    strgs = ["母屋:"+moya, "屋根下地:"+sitaji, "屋根:丸波カラートタン 0.35mm"]
    addBalloon(llst, ba1, ba2, strgs, "cn6\n", "cc2\n")
    ba1 = [(pb2[0]-pb1[0])*1/3, (pb2[1]-pb1[1])*1/3+nh]
    ba2 = [ba1[0]+400, ba1[1]-400]
    strgs = ["梁:" + g1]
    addBalloon(llst, ba1, ba2, strgs, "cn6\n", "cc0\n")
    return pt1, pc1, pb1, pt2, pc2, pb2

def putNoki_L(ly, llst, x):
    pt1 = [x-cw/2, nh-ry+grw]
    pb1 = [x-cw/2, nh-ry+grw-nrw]
    pt2 = [pt1[0]-nokilen*math.cos(r), pt1[1]-nokilen*math.sin(r)]
    pb2 = [pt2[0]+mn[0]*math.sin(r), pt2[1]-mn[0]*math.cos(r)]
    pc1 = [pt1[0], (pt1[1]+pb1[1])/2]
    pc2 = [(pt2[0]+pb2[0])/2, (pt2[1]+pb2[1])/2]
    pfb1 = [pb1[0], pb1[1]+mn[3]/math.cos(r)]
    pfb2 = [pb2[0]-mn[3]*math.sin(r), pb2[1]+mn[3]*math.cos(r)]
    pft1 = [pt1[0], pt1[1]-mn[3]/math.cos(r)]
    pft2 = [pt2[0]+mn[3]*math.sin(r), pt2[1]-mn[3]*math.cos(r)]    
    initP = pt2
    llst.append(ly+"\n")
    llst.append("lc2\n")
    addBox(llst, pb1,pb2,pt1,pt2)
    addflg(llst, pfb1, pfb2, pft1, pft2)
    llst.append("lt5\n"); addcent(llst, pc1,pc2); llst.append("lt1\n")
    return initP

def putNoki_U(ly, llst, x):
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
    llst.append(ly+"\n")
    llst.append("lc2\n")   
    addBox(llst, pb1,pb2,pt1,pt2)
    addflg(llst, pfb1, pfb2, pft1, pft2)
    llst.append("lt5\n"); addcent(llst, pc1,pc2); llst.append("lt1\n")
    return endP

def putYane(ly, llst, initP, endP):
    shape_yane = []
    shape_hafu = []
    shape_kabe = []
    llst.append(ly+"\n")
    llst.append("lc4\n")
    sj0 = [initP[0] - 60 * math.sin(r), initP[1] + 60 * math.cos(r)]    #下地
    sj1 = [endP[0] - 60 * math.sin(r), endP[1] + 60 * math.cos(r)]    
    sjt0 = [sj0[0]-sitaji_t*math.sin(r), sj0[1]+sitaji_t*math.cos(r)]
    sjt1 = [sj1[0]-sitaji_t*math.sin(r), sj1[1]+sitaji_t*math.cos(r)]
    addcent(llst, sj0, sj1)
    pb1 = [sj0[0]-sitaji_t*math.sin(r)-48*math.cos(r), sj0[1]+sitaji_t*math.cos(r)-48*math.sin(r)]  #屋根
    pt1 = [pb1[0]-yane_t*math.sin(r), pb1[1]+yane_t*math.cos(r)]
    pb2 = [sj1[0]-sitaji_t*math.sin(r)+48*math.cos(r), sj1[1]+sitaji_t*math.cos(r)+48*math.sin(r)]
    pt2 = [pb2[0]-yane_t*math.sin(r), pb2[1]+yane_t*math.cos(r)]
    addBox(llst, pb1,pb2,pt1,pt2)


    hft1 = [sjt1[0]+hafut*math.cos(r), sjt1[1]+hafut*math.sin(r)] #破風板
    ele2 = getfig("木-45x60\n")
    ele2 = expandfig_x(ele2, 30, hafut)
    ele2 = expandfig_y(ele2, 30, hafuyakuw[0])
    putObj("ly3", llst, ele2, sjt0, [0, 0], math.pi+r)
    putObj("ly3", llst, ele2, hft1, [0, 0], math.pi+r)
    # 役物
    yaku0 = [sjt0[0]-(hafut*math.cos(r)-hafuyakuw[0]*math.sin(r)), sjt0[1]-(hafut*math.sin(r)+hafuyakuw[0]*math.cos(r))]
    yaku1 = [sjt0[0]-(hafut*math.cos(r)-hafuyakuw[1]*math.sin(r)), sjt0[1]-(hafut*math.sin(r)+hafuyakuw[1]*math.cos(r))]
    yaku2 = [hft1[0]-(0*math.cos(r)-hafuyakuw[0]*math.sin(r)), hft1[1]-(0*math.sin(r)+hafuyakuw[0]*math.cos(r))]
    yaku3 = [hft1[0]-(0*math.cos(r)-hafuyakuw[1]*math.sin(r)), hft1[1]-(0*math.sin(r)+hafuyakuw[1]*math.cos(r))]
    addcent(llst, yaku0, yaku1)
    addcent(llst, yaku2, yaku3)
    hf1 = getCrossPointby4P(pb1, pb2, yaku0, yaku1)
    hf2 = getCrossPointby4P(pb1, pb2, yaku2, yaku3)

    k1 = [-cw/2-moyah, 0]
    k3 = [k1[0], 1]
    xy1 = getCrossPointby4P(yaku1, yaku3, k1, k3)
    addcent(llst, yaku1, xy1)
    k1 = [xlen+cw/2+moyah, 0]
    k3 = [k1[0], 1]
    xy2 = getCrossPointby4P(yaku1, yaku3, k1, k3)
    addcent(llst, yaku3, xy2)
    k1 = [xlen+cw/2, 0]
    k3 = [k1[0], 1]
    xy3 = getCrossPointby4P(yaku1, yaku3, k1, k3)

    klt1 = [xy1[0], xy1[1]+5]  #左壁
    klt2 = [klt1[0]-kabe_t, klt1[1]]
    klb2 = [klt2[0], 0]
    klb1 = [klt1[0], 0]
    klc = getCrossPointby4P(yaku1, yaku3, klt2, klb2)
    addBox(llst, klt1, klt2, klb1, klb2)
    krt1 = [xy2[0], xy2[1]+10]  #右壁
    krt2 = [krt1[0]+kabe_t, krt1[1]]
    krb2 = [krt2[0], 0]
    krb1 = [krt1[0], 0]
    krc = getCrossPointby4P(yaku1, yaku3, krt2, krb2)    
    addBox(llst, krt1, krt2, krb1, krb2)

    global ofs
    ofs = ofs_ritu1     #一時リストに1立面書き込み
    tlst.clear()
    tlst.append("lg0\n")
    addBox(tlst, pb1,pb2,pt1,pt2)
    addBox(tlst, hf1, yaku1, hf2, yaku3)
    addcent(tlst, klc, klb2)
    addcent(tlst, krc, krb2)
    addcent(tlst, klb2, krb2)
    shape_yane.extend([pb1, pt1, pt2, pb2])   
    shape_hafu.extend([hf1, yaku1, hf2, yaku3])
    shape_kabe.extend([klc, klb2, krb2, krc])    
    #壁ハッチング
    x = klc[0] + ((krc[0] - klc[0]) % pitch) / 2
    while x < krc[0]:
        tp = getCrossPointby4P(yaku1, yaku3, [x, 0], [x, 1])
        addcent(tlst, tp, [x, 0])
        x += pitch
    kisolt = [-120, 0]; kisolb = [-120, -100]   #基礎
    kisort = [xlen+120, 0]; kisorb = [xlen+120, -100]
    addcent(tlst, kisolt, kisolb)
    addcent(tlst, kisolb, kisorb)
    addcent(tlst, kisorb, kisort)

    for ele in tlst:    #一時リストを書き込み    
        llst.append(ele)
    lst_ritu_e = mirror(tlst, "x", ofs_ritu1[0] + xlen/2, ofs_rituE)    #一時原点から反転ラインまでの距離、配置先原点指定
    for ele in lst_ritu_e:
        llst.append(ele)


    ofs = ofs_rituB
    side = cd/2 + dobutiw + kabe_t  # B立面
    ylt = [-side-250, pt2[1]]; yrt = [ylen + side+250, pt2[1]]; ylb = [-side-250, yaku1[1]]; yrb = [ylen + side+250, yaku1[1]] 
    yl2 = [-side-250, pb1[1]]; yr2 = [ylen + side+250, pb1[1]]
    yl3 = [-side-250, pt1[1]]; yr3 = [ylen + side+250, pt1[1]]    
    addBox(llst, ylt, yrt, ylb, yrb)
    addcent(llst, yl2, yr2)
    addcent(llst, yl3, yr3)
    #屋根ハッチング
    llst.append("lc8\n")
    x = ylt[0] + ((yrt[0] - ylt[0]) % 400) / 2
    while x < yrt[0]:
        tp = getCrossPointby4P(ylt, yrt, [x, 0], [x, 1])
        addcent(llst, tp, [x, yl3[1]])
        x += 400
    llst.append("lc4\n")
    addBox(llst, [-side, yaku1[1]], [ylen + side, yaku1[1]], [-side, 0], [ylen + side, 0])
    #壁ハッチング
    x = -side + ((ylen+side + side) % pitch) / 2
    while x < ylen + side:
        tp = getCrossPointby4P(ylb, yrb, [x, 0], [x, 1])
        addcent(llst, tp, [x, 0])
        x += pitch
    kisolt = [-60, 0]; kisolb = [-60, -100]   #基礎
    kisort = [ylen+60, 0]; kisorb = [ylen+60, -100]
    addcent(llst, kisolt, kisolb)
    addcent(llst, kisolb, kisorb)
    addcent(llst, kisorb, kisort)

    ofs = ofs_rituA
    side = cd/2 + dobutiw + kabe_t  # A立面
    ylt = [-side-250, pt2[1]]; yrt = [ylen + side+250, pt2[1]]; ylb = [-side-250, yaku3[1]]; yrb = [ylen + side+250, yaku3[1]] 
    addBox(llst, ylt, yrt, ylb, yrb)
    addcent(llst, [-side-250, hf2[1]], [ylen + side+250, hf2[1]])
    addcent(llst, [-side-250, yaku1[1]], [-side, yaku1[1]])
    addcent(llst, [ylen + side, yaku1[1]], [ylen + side+250, yaku1[1]]) 
    addcent(llst, [-side-250, yaku1[1]], ylb)
    addcent(llst, [ylen + side+250, yaku1[1]], yrb)
    yl4 = [-side, krc[1]]; yr4 = [ylen + side, krc[1]]
    yl5 = [-side, 0]; yr5 = [ylen + side, 0]
    addBox(llst, yl4, yr4, yl5, yr5)
    #壁ハッチング
    x = -side + ((ylen+side + side) % pitch) / 2
    while x < ylen + side:
        tp = getCrossPointby4P(yl4, yr4, [x, 0], [x, 1])
        addcent(llst, tp, [x, 0])
        x += pitch
    kisolt = [-60, 0]; kisolb = [-60, -100]   #基礎
    kisort = [ylen+60, 0]; kisorb = [ylen+60, -100]
    addcent(llst, kisolt, kisolb)
    addcent(llst, kisolb, kisorb)
    addcent(llst, kisorb, kisort)

    ofs = [0, 0]
    llst.append("lg8\n")
    llst.append("lc2\n")
    return xy1, xy2, xy3

def putTategu(llst, itm):
    pos_h_spec = dic[itm].split(",")
    pos = pos_h_spec[0].split("-")
    tori = pos[0]
    seg = int(pos[1])
    hpos = int(pos_h_spec[1])
    spec = pos_h_spec[2]
    putTori(llst, itm, tori, seg, hpos, spec)

def putTori(llst, itm, tori, seg, hpos, spec):
    global ofs
    if tori == "A":
        ofs = ofs_rituA; toriAry = toriA
    if tori == "B": 
        ofs = ofs_rituB; toriAry = toriB
    if tori == "1":
        ofs = ofs_ritu1; toriAry = tori1
    if tori == "E":
        ofs = ofs_rituE; toriAry = toriE
    pl = int(toriAry[seg-1])
    ph = int(toriAry[seg])
    pm = pl + (ph - pl) / 2
    if spec[0] == "H":
        spec = float(spec[1:])
        ele2 = getfig(itm[:-1] + "\n")
        ele2 = expandfig_x(ele2, 800, (ph - pl) / 2 + 50)
        ele2 = expandfig_x(ele2, -800, -(ph - pl) / 2 - 50)
        elements = expandfig_y(ele2, 500, spec)
    else:
        elements = getfig(spec + "\n")
    putObj("ly5", llst, elements, [pm, hpos], [0, 0], 0)
    trimHatch(llst, elements, ofs, hpos)

def trimHatch(llst, elements, tof, hpos):
    horlines = []; ylst = []; mxlnlst = []
    for ele in elements:
        el = ele.split()
        if el[0] == "L":
            if el[2] == el[4]:
                horlines.append(ele)
                ylst.append(float(el[2]))
    ymax = max(ylst)    
    for ele in horlines:
        el = ele.split()
        if float(el[2]) == ymax:
            mxlnlst.append([float(el[1]) + tof[0], float(el[2]) + tof[1], float(el[3]) + tof[0], float(el[4]) + tof[1]])
    for el in mxlnlst:
        ly = hpos + tof[0] 
        hy = hpos + ymax + tof[1]
        if el[0] < el[2]:
            lx = el[0]; rx = el[2]
        else:
            lx = el[2]; rx = el[0]

    hitele = ""
    for ele in llst:
        #print(ele[0])
        if ele[0]==" ": # 直線
            el = ele.split()
            if el[1] == el[3]:  # 縦線
                if el[1] > lx and el[3] < rx:   # 横範囲に入る
                    ex = float(el[1]); y1 = float(el[2]); y2 = float(el[4])
                    if y1 > y2:
                        ehy = y1; ely = y2
                    else:
                        ehy = y2; ely = y1
                    if ehy > hy and ely < hy and ely > ly:
                        hitele = ele





def editTategu(llst):
    llst.append("lg0\n")
    for i in range(1, window_vol+1):
        putTategu(llst, "窓" + str(i))
    for i in range(1, door_vol + 1):
        putTategu(llst, "框ドア" + str(i))
    for i in range(1, turido_vol + 1):
        putTategu(llst, "吊り戸" + str(i))
    for i in range(1, shutter_vol + 1):
        putTategu(llst, "軽量シャッター" + str(i))

def mirror(tlst, axis, axisp, putofs):
    def inv(strxy):
        putd = putofs[0]-ofs[0] if axis == "x" else putofs[1]-ofs[1]
        xy = float(strxy)
        dis = xy - axisp
        invxy = xy - dis * 2 + putd
        return str(invxy)

    newlst = []
    for ele in tlst:
        cmd = ele[0:2]
        elst = ele.rstrip("\n").split(" ")    #末尾の\nを除いた後、スペースで分割
        if cmd == "pt":
            if axis == "x":
                elst[1] = inv(elst[1])
            else:
                elst[2] = inv(elst[2])
            line = "{} {} {}\n".format(cmd, elst[1], elst[2]); newlst.append(line)  
        else:
            if len(elst) == 4:
                if axis == "x":
                    elst[0] = inv(elst[0]); elst[2] = inv(elst[2])
                else:
                    elst[1] = inv(elst[1]); elst[3] = inv(elst[3])
                line = "{} {} {} {}\n".format(elst[0], elst[1], elst[2], elst[3]); newlst.append(line)
            else:
                newlst.append(ele)
    return newlst    

def putObj(ly, llst, elements, initP, rotP, rot):
#（図形要素、図形基準の配置点、図中座標上の回転中心点、回転角）
    x0 = initP[0]; y0 = initP[1]
    px = rotP[0]; py = rotP[1]
    global lt, lc
    #lt = ""; lc = ""
    llst.append(ly+"\n")
    for ele in elements:
        el = ele.split()
        if el[0] == "L":
            x1 = float(el[1]); y1 = float(el[2])
            x2 = float(el[3]); y2 = float(el[4])
            if el[5] != lt:
                llst.append(el[5]+"\n")
                lt = el[5]
            if el[6] != lc:
                llst.append(el[6]+"\n")
                lc = el[6]              
            rx1 = (x1+px) * math.cos(rot) - (y1+py) * math.sin(rot) + x0 + ofs[0]
            ry1 = (x1+px) * math.sin(rot) + (y1+py) * math.cos(rot) + y0 + ofs[1]
            rx2 = (x2+px) * math.cos(rot) - (y2+py) * math.sin(rot) + x0 + ofs[0]
            ry2 = (x2+px) * math.sin(rot) + (y2+py) * math.cos(rot) + y0 + ofs[1]
            line = "{} {} {} {}\n".format(str(rx1), str(ry1), str(rx2), str(ry2)); llst.append(line)  
        else:
            if el[0] == "ci":
                x1 = float(el[1]); y1 = float(el[2])
                rlen = float(el[3])
                rx1 = (x1+px) * math.cos(rot) - (y1+py) * math.sin(rot) + x0 + ofs[0]
                ry1 = (x1+px) * math.sin(rot) + (y1+py) * math.cos(rot) + y0 + ofs[1]
                if len(el) == 6:    # 円
                    line = "{} {} {} {}\n".format("ci", str(rx1), str(ry1), str(rlen)); llst.append(line)
                else:   #　arc
                    line = "{} {} {} {} {} {} {} {}\n".format("ci", str(rx1), str(ry1), str(rlen), el[4], el[5], el[6], el[7]); llst.append(line)                    

def editSunpou(llst):
    llst.append("cc1\n")    #文字基準点:中下
    llst.append("lc1\n")    #線色:青
    llst.append("ly1\n")
    global ofs 
    ofs = ofs_kana
    llst.append("lg8\n")    #矩計図
    putSunpou(llst, [0, -mbase[1]], [0, gl], [400, 800], "cn6\n", 0)
    putSunpou(llst, [0, gl], [0, 0], [400, 800], "cn6\n", 0)
    putSunpou(llst, [0, 0], [0, nh], [400, 800], "cn6\n", 0)
    putSunpou(llst, [0, nh], [0, nh+slope*xlen], [400, 800], "cn6\n", 0)
    putSunpou(llst, [0, -mbase[1]], [0, 0], [800, 1100], "cn6\n", 0)
    putSunpou(llst, [0, 0], [0, nh+slope*xlen], [800, 1100], "cn6\n", 0)
    putSunpou(llst, [0, -1000], [xlen, -1000], [-50, -400], "cn6\n", 0)
    ofs = ofs_ritu1 #1立面
    editSunpouRitu(llst, xlen)
    ofs = ofs_rituE #E立面
    editSunpouRitu(llst, xlen)    
    ofs = ofs_rituA #A立面
    editSunpouRitu(llst, ylen)
    ofs = ofs_rituB #B立面
    editSunpouRitu(llst, ylen)

def editSunpouRitu(llst, fulllth):
    llst.append("lg0\n")
    putSunpou(llst, [0, gl], [0, 0], [800, 1600], "cn6\n", 0)
    putSunpou(llst, [0, 0], [0, nh], [800, 1600], "cn6\n", 0)
    putSunpou(llst, [0, nh], [0, nh+slope*xlen], [800, 1600], "cn6\n", 0)
    putSunpou(llst, [0, 0], [0, nh+slope*xlen], [1600, 2200], "cn6\n", 0)
    putSunpou(llst, [0, 0], [fulllth, -0], [-300, -1000], "cn6\n", 0)

def putSunpou(llst, p1, p2, dd, cn, decp):
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
    addcent(llst, d1, d2)
    addcent(llst, d3, d4)
    addcent(llst, d2, d4)
    addpoint(llst, d2); addpoint(llst, d4)
    strsize = "{:,.0f}\n".format(vsize) if decp ==0 else "{:,.1f}\n".format(vsize)
    strg = str(strsize)
    addstring(llst, d2, d4, strg, cn, "cc1\n")

def getfig(figname):
    for fname in figs:
        if fname == figname:
            idx = int(figs.index(fname) + 2)
            elements = []
            while figs[idx] != "\n":
                cmd = "L" if figs[idx][0]==" " else ""
                elements.append(cmd + figs[idx])
                idx = idx + 1
            return elements            

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
        else:
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
        else:
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

def editHeimen(llst):
    mgn = 400
    llst.append("lc2\n")
    ele = getfig(c1 + "\n")
    for Ax in toriA:
        putObj("lg0", llst, ele, [Ax, 0], [0 ,0], 0)
    for Bx in toriB:
        putObj("lg0", llst, ele, [Bx, xlen], [0 ,0], 0)
    ele = getfig(m1 + "\n")
    for y1 in tori1:
        if y1 != 0 and y1 != xlen:
            putObj("lg0", llst, ele, [0, y1], [0, 0], 0)
    for Ey in toriE:
        if Ey != 0 and Ey != xlen:
            putObj("lg0", llst, ele, [ylen, Ey], [0, 0], 0)
    llst.append("lt5\n")
    for Ax in toriA:
        addcent(llst, [Ax, -mgn], [Ax, mgn])
    for Bx in toriB:
        addcent(llst, [Bx, xlen - mgn], [Bx, xlen + mgn])
    for y1 in tori1:
        addcent(llst, [-mgn, y1], [mgn, y1])
    for Ey in toriE:
        addcent(llst, [ylen - mgn, Ey], [ylen + mgn, Ey])        

    llst.append("lt1\n")
    llst.append("lc4\n")
    disx = mw/2 + dobutih
    disy = cw/2 + dobutih
    addcent(llst, [-disx, -disy], [ylen + disx, -disy])
    addcent(llst, [-disx, xlen+disy], [ylen + disx, xlen+disy])
    addcent(llst, [-disx, -disy], [-disx, xlen + disy])
    addcent(llst, [ylen + disx, -disy], [ylen + disx, xlen + disy])