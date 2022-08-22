import math, copy
from kana_mod import katakana
from kana_mod import commod as cm
#import subprocess, pyautogui, time
#import win32gui, win32process, win32api
#----------------------------


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

jwf = []
with open("C:/jww8/JW_WIN.JWF") as f:
    jwf = f.readlines()

s0 = dic["lg0縮尺"]
s8 = dic["lg8縮尺"]
#Lg縮尺                   0  1  2  3  4  5  6  7    8  9  A  B  C  D  E  F
jwf[36] = f"LAYSCALE = {s0} 40 40 40 40 40 40 40 {s8} 10 10 10 10 10 10 1\n"
slst = list(map(int, jwf[36].strip("LAYSCALE = ").split()))

with open("C:/jww8/JW_WIN.JWF", mode="w") as f:
    f.writelines(jwf)

typ = dic["タイプ"]
mei = dic["工事名称"]
tanto = dic["担当"]
seizu = dic["製図"]
date = dic["日付"]

xlen = float(dic["妻方向柱芯全長"])
ylen = float(dic["軒方向柱芯全長"])

lg = ""; ly = ""; lt = ""; lc = ""
cn = ""; cc = ""; pn = ""
conf = {"lg":lg, "ly":ly, "lt":lt, "lc":lc, "cn":cn, "cc":cc, "pn":pn}

def jwEdit(lst, ofs, lg):   # jw形式に変換
    xlst = []; ylst = []
    jwlst.append(lg)
    for ele in lst:
        if len(ele) < 6 or ele[0:2] == "cn":    # 単発コマンド
            hd = ele[0:2]
            if ele != conf[hd]: # 直前コマンドと同じなら追加しない
                conf[hd] = ele
                jwlst.append(ele) 
        else:
            if ele[1] == "h":   # ch
                el = ele.split("_")
                x = float(el[1]); y = float(el[2]); dx = el[3]; dy = el[4]; strg = el[5]
                x += ofs[0]
                y += ofs[1]
                jwlst.append("ch {} {} {} {} \"{}\n".format(str(x), str(y), el[3], el[4], el[5]))
                xlst.append(x); ylst.append(y)
            else:
                if ele[1] == "i":   # ci
                    el = ele.split()
                    x = float(el[1]); y = float(el[2]); rlen = float(el[3])
                    x += ofs[0]
                    y += ofs[1]
                    if len(el) == 4:
                        jwlst.append("{} {} {} {}\n".format("ci", str(x), str(y), str(rlen)))
                    else:
                        jwlst.append("{} {} {} {} {} {} {} {}\n".format("ci", str(x), str(y), str(rlen), el[4], el[5], el[6], el[7]))
                    xlst.append(x); ylst.append(y)
                else:
                    if ele[0] == "L":   # line
                        el = ele.split()
                        x1 = float(el[1]); y1 = float(el[2])
                        x2 = float(el[3]); y2 = float(el[4])
                        x1 += ofs[0]; x2 += ofs[0]
                        y1 += ofs[1]; y2 += ofs[1]
                        jwlst.append("{} {} {} {}\n".format(str(x1), str(y1), str(x2), str(y2)))
                        xlst.append(x1); ylst.append(y1)
                        xlst.append(x2); ylst.append(y2)
                    if ele[0] == "p":   # point
                        el = ele.split()
                        x1 = float(el[1]); y1 = float(el[2])
                        x1 += ofs[0]; y1 += ofs[1]
                        jwlst.append("{} {} {}\n".format("pt", str(x1), str(y1)))
                        xlst.append(x1); ylst.append(y1)
    xmax = max(xlst); ymax = max(ylst)
    xmin = min(xlst); ymin = min(ylst)
    mmdic = {"hx": xmax, "hy": ymax, "lx": -xmin, "ly": -ymin}
    return mmdic

Hyolst = []
Kanalst = []; Hlst = []; RAlst = []; RBlst = []; R1lst = []; RElst = []; pts = []
jwlst = []; wakulst = []; lg0strlst = []; lg8strlst = []


# 矩計
pts = katakana.editKana(Kanalst, dic, slst[8], typ)
pb1, pb2, pt1, pt2, hf1, hf2, yaku1, yaku3, klc, krc, klb2, krb2, xy1, xy2, xy3 = pts
cm.editSunpou(Kanalst, slst[8], typ)

# 立面
katakana.editRitu1(R1lst, pb1, pb2, pt1, pt2, hf1, hf2, yaku1, yaku3, klc, krc, klb2, krb2, typ)
RElst = cm.mirror(R1lst, "x", xlen/2)
katakana.editRituB(RBlst, pb1, pb2, pt1, pt2, hf1, hf2, yaku1, yaku3, klc, krc, klb2, krb2)
if typ == "片流れ":
    katakana.editRituA(RAlst, pb1, pb2, pt1, pt2, hf1, hf2, yaku1, yaku3, klc, krc, klb2, krb2)
else:
    RAlst = copy.copy(RBlst)

# 立面建具
t1lst = cm.putTategu(R1lst, "1")
telst = cm.putTategu(RElst, "E")
talst = cm.putTategu(RAlst, "A")
tblst = cm.putTategu(RBlst, "B")
# 立面寸法
cm.editSunpouRitu(RAlst, talst, ylen, slst[0], "A", typ)
cm.editSunpouRitu(RBlst, tblst, ylen, slst[0], "B", typ)
cm.editSunpouRitu(R1lst, t1lst, xlen, slst[0], "1", typ)
cm.editSunpouRitu(RElst, telst, xlen, slst[0], "E", typ)

# 平面
katakana.editHeimen(Hlst)
cm.putTateguHei(Hlst)
cm.editSunpouHei(Hlst, slst[0])

# 表
cm.editHyo(Hyolst)

# 図面枠
elements = cm.getFig("A3図面枠\n")
cm.putObj("ly0", wakulst, elements, [0, 0], [0, 0], 0)

# 図名、日付、縮尺
cm.addstring(wakulst, [31, 14.5], [50, 14.5],  mei, "cn7\n", "cc0\n")
cm.addstring(wakulst, [297.35, 11.75], [320, 11.75], seizu, "cn5\n", "cc4\n")
cm.addstring(wakulst, [306.45, 11.75], [320, 11.75], tanto, "cn5\n", "cc4\n")
cm.addstring(wakulst, [199.45, 6.5], [220, 6.5], date, "cn5\n", "cc2\n")
cm.addstring(lg0strlst, [31 * slst[0], 7.5 * slst[0]], [35 * slst[0], 7.5 * slst[0]], "平面図、立面図", "cn7\n", "cc0\n")
cm.addstring(lg0strlst, [181.5 * slst[0], 14.5 * slst[0]], [200 * slst[0], 14.5 * slst[0]], f"1/{slst[0]}", "cn4\n", "cc0\n")
cm.addstring(lg8strlst, [60.2 * slst[8], 7.5 * slst[8]], [70 * slst[8], 7.5 * slst[8]], "、矩計図", "cn7\n", "cc0\n")
cm.addstring(lg8strlst, [188 * slst[8], 14.5 * slst[8]], [220 * slst[8], 14.5 * slst[8]], f",1/{slst[8]}", "cn4\n", "cc0\n")

# サイズ調査
ofs_kana = [0, 0]
ofs_hei = [0, 0]
ofs_ritu1 = [0, 0]
ofs_rituE = [0, 0]
ofs_rituA = [0, 0]
ofs_rituB = [0, 0]
ofs_hyo = [0, 0]
dK = jwEdit(Kanalst, ofs_kana, "lg8\n")
dA = jwEdit(RAlst, ofs_rituA, "lg0\n")
dB = jwEdit(RBlst, ofs_rituB, "lg0\n")
dE = jwEdit(RElst, ofs_rituE, "lg0\n")
d1 = jwEdit(R1lst, ofs_ritu1, "lg0\n")
dHei = jwEdit(Hlst, ofs_hei, "lg0\n")
dHyo = jwEdit(Hyolst, ofs_hyo, "lgF\n")

limY = 270 * slst[0]
totalY = dB["ly"] + dB["hy"] + dA["ly"] + dA["hy"] + dHei["ly"] + dHei["hy"]
mgnY = (limY - totalY) / 10
ofx = 10 * slst[0]; ofy = 20.5 * slst[0]

rightKX = 413 * slst[8]
ofxK = 5 * slst[8]
ofyK = (20.5 + 5) * slst[8]

rightHyoX = 413
topHyoY = 290
ofxHyo = 3; ofyHyo = 6

rituH = (topHyoY - ofyHyo - dHyo["ly"]) * slst[0]
rituL = (ofyK + dK["ly"] + dK["hy"]) / slst[8] * slst[0]
ofyR = ((rituH - rituL) - (d1["ly"] + d1["hy"])) / 2 

# 原点配置先
ofs_rituB = [ofx + dHei["lx"] , ofy + dB["ly"] + mgnY*2]
ofs_rituA = [ofs_rituB[0], ofs_rituB[1] + dB["hy"] + dA["ly"] + mgnY*3]
ofs_hei = [ofs_rituB[0], ofs_rituA[1]  + dA["hy"] + dHei["ly"] + mgnY*3]
ofs_kana = [rightKX - dK["hx"] - ofxK, ofyK + dK["ly"]]

ofs_hyo = [rightHyoX - dHyo["hx"] - ofxHyo, topHyoY - ofyHyo]

wkana = dK["lx"] + dK["hx"]
wHei = dHei["lx"] + dHei["hx"]
writu1 = d1["lx"] + d1["hx"]
writuA = dA["lx"] + dA["hx"]
if typ == "片流れ":
    ofs_ritu1 = [ofx + wHei * 1.3, rituL + d1["ly"] + ofyR]
    ofs_rituE = [ofs_ritu1[0] + writu1 * 1.3 , rituL + dE["ly"] + ofyR]
else:
    rightlim = (rightKX - wkana) / slst[8] * slst[0]
    leftlim = ofx + writuA
    mgn = (rightlim - leftlim) - writu1
    ofs_ritu1 = [ofx + writuA + d1["lx"] + mgn/2, ofs_rituA[1]]
    ofs_rituE = [ofx + writuA + d1["lx"] + mgn/2, ofs_rituB[1]]
ofs_waku = [0, 0]
ofs_lg1str = [0, 0]
ofs_lg8str = [0, 0]

# jw出力
jwlst = []
mm = jwEdit(Kanalst, ofs_kana, "lg8\n")
mm = jwEdit(RAlst, ofs_rituA, "lg0\n")
mm = jwEdit(RBlst, ofs_rituB, "lg0\n")
mm = jwEdit(R1lst, ofs_ritu1, "lg0\n")
mm = jwEdit(RElst, ofs_rituE, "lg0\n")
mm = jwEdit(Hlst, ofs_hei, "lg0\n")
mm = jwEdit(Hyolst, ofs_hyo, "lgF\n")
mm = jwEdit(wakulst, ofs_waku, "lgF\n")
mm = jwEdit(lg0strlst, ofs_waku, "lg0\n")
mm = jwEdit(lg8strlst, ofs_waku, "lg8\n")


f = open("C:/jww/実験用bat/list.txt", mode="w")
f.writelines(jwlst)
f.close()
'''
subprocess.Popen("Jw_win.exe", shell=True)
time.sleep(0.5)
pyautogui.click(800,600)
pyautogui.write("G")
'''