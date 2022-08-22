
figs = []
f = open("C:/jww/部材リスト/鋼材データ.txt")
figs = f.readlines()
f.close()

dic = {}
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

def torilist(toriname):
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
#toriA = []; tiriB = []; tori1 = []; toriE = []   
toriA = torilist("柱芯間A通り")
toriB = torilist("柱芯間B通り")
tori1 = torilist("柱芯間1通り")
toriE = torilist("柱芯間E通り")

c1 = dic["C1鋼材"]


ofs_hei = [1000, 10000]
ofs = ofs_hei

def editHeimen(llst):
    putP = [0, 0]
    ele = getfig(c1)
    for Ax in toriA:
        putP[0] = Ax; putP[1] = 0
        putObj("lg0", llst, ele, putP, [0 ,0], 0)




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
                line = "{} {} {} {}\n".format("ci", str(rx1), str(ry1), str(rlen)); llst.append(line)