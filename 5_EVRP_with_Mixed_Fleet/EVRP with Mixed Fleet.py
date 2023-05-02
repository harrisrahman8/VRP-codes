from itertools import product
from sys import stdout as out
from mip import Model, xsum, minimize, BINARY
from PIL import Image, ImageDraw
import random
from math import cos, sin, pi, sqrt, dist
import warnings
warnings.filterwarnings('ignore')

def drawarrow(draw, pos, color, width, amp):
    a = 30/180*pi
    pos = ((100+10*pos[0])*amp,
           (100+10*pos[1])*amp,
           (100+10*pos[2])*amp,
           (100+10*pos[3])*amp)
    dist = ((pos[0]-pos[2])**2+(pos[1]-pos[3])**2)**0.5
    midpoint = ((pos[0]+pos[2])/2, (pos[1]+pos[3])/2)
    draw.line(pos, fill=color, width=width)
    vec = (3*amp*(pos[0]-pos[2])/dist, 3*amp*(pos[1]-pos[3])/dist)
    vec1 = (vec[0]*cos(a)-vec[1]*sin(a), vec[0]*sin(a)+vec[1]*cos(a))
    pos1 = midpoint + (midpoint[0]+vec1[0], midpoint[1]+vec1[1])
    vec2 = (vec[0]*cos(a)+vec[1]*sin(a), -vec[0]*sin(a)+vec[1]*cos(a))
    pos2 = midpoint + (midpoint[0]+vec2[0], midpoint[1]+vec2[1])
    draw.line(pos1, fill=color, width=width)
    draw.line(pos2, fill=color, width=width)

def makeresimg(SIZE, node_size, route_width, coordinates, V, Vn, Vc, Ve, K, Kc, Ke, Qc, Qe, rc, re, x, c):
    img = Image.new(mode='RGB', size=(200*SIZE, 200*SIZE), color=0xFFFFFF)
    draw = ImageDraw.Draw(img)
    typeColor = [0x0000FF,   # conventional
                 0x00FF00]    # electrical
    cap = []
    for i in K:
        cap.append([])
        for j in V:
            if j in {0}:
                cap[i].append(0)
            if j in Vn:
                cap[i].append(-1)
            if j in Vc:
                cap[i].append(Qc)
            if j in Ve:
                cap[i].append(Qe)
    for k in Kc:
        cap[k][0] = Qc
        for n in {0}.union(Vc):
            idx = n
            while True:
                nidx = [i for i in V if x[k][idx][i].x >= 0.99]
                if len(nidx) > 1:
                    for m in nidx:
                        sidx = m
                        while True:
                            snidx = [i for i in V if x[k][sidx][i].x >= 0.99][0]
                            pos = tuple(coordinates[sidx]+coordinates[snidx])
                            drawarrow(draw, pos, typeColor[0], route_width, SIZE)
                            if snidx in {0}.union(Vc):
                                break
                            cap[k][snidx] = cap[k][sidx] - c[snidx][sidx]*rc
                            sidx = snidx
                    break
                elif len(nidx) == 1:
                    nidx = nidx[0]
                    pos = tuple(coordinates[idx]+coordinates[nidx])
                    drawarrow(draw, pos, typeColor[0], route_width, SIZE)
                    if nidx in {0}.union(Vc):
                        break
                    cap[k][nidx] = cap[k][idx] - c[nidx][idx]*rc
                    idx = nidx
                else:
                    break
    for k in Ke:
        cap[k][0] = Qe
        for n in {0}.union(Ve):
            idx = n
            while True:
                nidx = [i for i in V if x[k][idx][i].x >= 0.99]
                if len(nidx) > 1:
                    for m in nidx:
                        sidx = m
                        while True:
                            snidx = [i for i in V if x[k][sidx][i].x >= 0.99][0]
                            pos = tuple(coordinates[sidx]+coordinates[snidx])
                            drawarrow(draw, pos, typeColor[1], route_width, SIZE)
                            if snidx in {0}.union(Ve):
                                break
                            cap[k][snidx] = cap[k][sidx] - c[snidx][sidx]*re
                            sidx = snidx
                    break
                elif len(nidx) == 1:
                    nidx = nidx[0]
                    pos = tuple(coordinates[idx]+coordinates[nidx])
                    drawarrow(draw, pos, typeColor[1], route_width, SIZE)
                    if nidx in {0}.union(Ve):
                        break
                    cap[k][nidx] = cap[k][idx] - c[nidx][idx]*re
                    idx = nidx
                else:
                    break
    for i in V:
        print()
        for j in K:
            print('%.1f\t\t' % cap[j][i], end='')
    ncap = [0]*(len(Vn)+1)
    for i in Vn:
        for k in K:
            if cap[k][i] > 0:
                ncap[i] = cap[k][i]
                break
    draw.rectangle(((100-node_size)*SIZE,
                    (100-node_size)*SIZE,
                    (100+node_size)*SIZE,
                    (100+node_size)*SIZE), 
                    fill='white', outline='black', width=5)
    for i in Vn:
        pos = ((100 - node_size + 10*coordinates[i][0])*SIZE, 
               (100 - node_size + 10*coordinates[i][1])*SIZE, 
               (100 + node_size + 10*coordinates[i][0])*SIZE, 
               (100 + node_size + 10*coordinates[i][1])*SIZE)
        draw.ellipse(pos, fill='white', outline='black', width=5)
        captex = "{:.1f}".format(ncap[i])
        w, h = draw.textsize(captex)
        draw.text(((100+10*coordinates[i][0])*SIZE-w/2, 
                   (100+10*coordinates[i][1])*SIZE-h/2), captex, fill='black')
        draw.text(((100+10*coordinates[i][0])*SIZE, 
                   (100+10*coordinates[i][1]-3)*SIZE-h/2), str(i), fill='black')
    for i in Vc:
        pos = ((100 - node_size + 10*coordinates[i][0])*SIZE, 
               (100 - node_size + 10*coordinates[i][1])*SIZE, 
               (100 + node_size + 10*coordinates[i][0])*SIZE, 
               (100 + node_size + 10*coordinates[i][1])*SIZE)
        draw.ellipse(pos, fill='white', outline=typeColor[0], width=5)
    for i in Ve:
        pos = ((100 - node_size + 10*coordinates[i][0])*SIZE, 
               (100 - node_size + 10*coordinates[i][1])*SIZE, 
               (100 + node_size + 10*coordinates[i][0])*SIZE, 
               (100 + node_size + 10*coordinates[i][1])*SIZE)
        draw.ellipse(pos, fill='white', outline=typeColor[1], width=5)
    return img

def makerawimg(SIZE, node_size, route_width, coordinates):
    print("no img")

# N     : customer node의 개수
# kc    : conventional vehicle의 개수
# ke    : electric vehicle의 개수
# Sc    : fuel station의 개수
# Se    : charging station의 개수
# Qc    : conventional vehicle의 최대 연료 용량
# Qe    : electric vehicle의 최대 배터리 용량
# rc    : 거리에 따라 소모되는 연료의 양
# re    : 거리에 따라 소모되는 배터리의 양
N = 8
kc, ke = 2, 2
Sc, Se = 2, 2
Qc, Qe = 20, 15
rc, re = 1, 1

# (0, 0) depot node
coordinates = [[0, 0]] 

# 랜덤 좌표에 N개의 customer node 생성
for i in range(N):
    #coordinates.append([20*random.random()-10, 20*random.random()-10])
    r = 7*random.random()+3
    t = random.random()
    #r = 6.5
    #t = 1/N*(i+0.5)
    coordinates.append([r*cos(t*2*pi), r*sin(t*2*pi)])
    #coordinates.append([r*cos(i/N*2*pi), r*sin(i/N*2*pi)])

# Sc개의 fuel station 위치 지정
for i in range(Sc):
    r = 5.5
    t = 2*pi*(1/Sc*(i)+1/4)
    coordinates.append([r*cos(t), r*sin(t)])

# Se개의 charging station 위치 지정
for i in range(Se):
    r = 3.5
    t = 2*pi/Se*(i)
    coordinates.append([r*cos(t), r*sin(t)])

# =====================           Sets          ===================== 
# V     : 모든 노드의 set
# Vn    : customer node의 set
# Vc    : fuel station의 set
# Ve    : charging station의 set
V = set(range(1+N+Sc+Se))
Vn = set(range(1, 1+N))
Vc = set(range(1+N, 1+N+Sc))
Ve = set(range(1+N+Sc, 1+N+Sc+Se))
# K     : 모든 vehicle set
# Kc    : conventional vehicle set
# Ke    : electrical vehicle set
K = set(range(kc+ke))
Kc = set(range(kc))
Ke = set(range(kc, kc+ke))

# distances matrix
c = []
for i in V:
    c.append([])
    for j in V:
        c[i].append(dist(coordinates[i], coordinates[j]))

# ===================== Parameters & Variables =====================

# n     : 노드의 총 개수
n = len(V)

model = Model()

x = [[[model.add_var(var_type=BINARY) for j in V] for i in V] for k in K]

# depot와 연결되지 않는 닫힌 경로를 제거하기 위한 y
y = [[model.add_var() for i in V] for k in K]

# 각 vehicle k가 i node에서 u1은 출발 배터리 양, u2는 도착 배터리 양 
u1 = [[model.add_var() for i in V] for k in K]
u2 = [[model.add_var() for i in V] for k in K]

# =====================   Objective Function   =====================

model.objective = minimize(xsum(c[i][j]*x[k][i][j] for k in K for i in V for j in V))

# =====================       Subject-to       =====================

# 경로 k에 대해서 depot에서 나오는 길은 하나, 들어오는 길은 하나
for k in K:
    model += xsum(x[k][0][j] for j in V-{0}) <= 1
    model += xsum(x[k][i][0] for i in V-{0}) <= 1

# 각 customer node에서 모든 경로 k를 고려해서 나가는 길은 하나
for i in Vn:
    model += xsum(x[k][i][j] for k in K for j in V - {i}) == 1

# 각 customer node에서 모든 경로 k를 고려해서 들어가는 길은 하나
for j in Vn:
    model += xsum(x[k][i][j] for k in K for i in V - {j}) == 1

# depot에서 나가는 vehicle의 배터리나 연료는 최대
for k in Kc:
    model += u1[k][0] == Qc
for k in Ke:
    model += u1[k][0] == Qe

# 다른 충전소에는 갈 수 없음
for k in Kc:
    for i in Ve:
        for j in V:
            model += x[k][i][j] == 0
            model += x[k][j][i] == 0
for k in Ke:
    for i in Vc:
        for j in V:
            model += x[k][i][j] == 0
            model += x[k][j][i] == 0

# 각 충전, 주유소에서 나가는 vehicle의 배터리나 연료는 최대
for k in Kc:
    for i in Vc:
        model += u1[k][i] == Qc
for k in Ke:
    for i in Ve:
        model += u1[k][i] == Qe

# 각 시점의 배터리의 값은 0과 최댓값 사이에 있어야 함
for i in V:
    for k in Kc:
        model += u1[k][i] >= 0
        model += u1[k][i] <= Qc
        model += u2[k][i] >= 0
        model += u2[k][i] <= Qc
    for k in Ke:
        model += u1[k][i] >= 0
        model += u1[k][i] <= Qe
        model += u2[k][i] >= 0
        model += u2[k][i] <= Qe

# 모든 노드에서 vehicle k가 들어오는 수와 나가는 수는 같다. 
for k in K:
    for i in V:
        model += xsum(x[k][i][j] for j in V - {i}) == xsum(x[k][j][i] for j in V - {i})

# sub-tour를 제거하는 constraints
for k in K:
    for (i,j) in product(V-{0}, V-{0}):
        if i != j:
            model += y[k][i] - (n+1)*x[k][i][j] >= y[k][j]-n

# 연료와 배터리의 소모
for (i, j) in product(V, V):
    if i != j:
        for k in Kc:
            model += u1[k][i] - rc*c[i][j]*x[k][i][j] + Qc*(1 - x[k][i][j]) >= u2[k][j]
        for k in Ke:
            model += u1[k][i] - re*c[i][j]*x[k][i][j] + Qe*(1 - x[k][i][j]) >= u2[k][j]

# 각 customer node에서 들어올때 배터리와 나갈때 배터리의 양은 같다. depot, station 제외
for k in K:
    for i in Vn:
        model += u1[k][i] == u2[k][i]

# =====================       모델 풀이       =====================
model.optimize()

# =====================      이미지 생성      =====================
SIZE = 10
node_size = 2
route_width = 2

if model.num_solutions:
    out.write('******* route with total distance %g *******'%(model.objective_value))
    print()
    for i in V:
        print('%2d\t%.1f\t%.1f'%(i, coordinates[i][0], coordinates[i][1]))
    print()
    for i in V:
        print()
        for j in V:
            print('%.1f\t'%c[i][j], end='')
    print()
    res_img = makeresimg(SIZE, node_size, route_width, coordinates, V, Vn, Vc, Ve, K, Kc, Ke, Qc, Qe, rc, re, x, c)
    res_img.show()
    res_img.save('result-EVRPMF.png')
else:
    print("NO ANSWER")
    res_img = makerawimg()
