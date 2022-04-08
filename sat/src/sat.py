from xml import dom
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from z3 import *
from math import ceil
import os
import datetime

#get the max one in a list
# find height
def symMax(list):
    m = list[0]
    for i in list[1:]:
        m = If(i > m, i, m)
    return m

def cumulative(start, duration, requirement, capacity):
    c = []
    for u in requirement:
        c.append(
            sum([If(And(start[i] <= u, u < start[i] + duration[i]), requirement[i], 0)
            for i in range(len(start))]) <= capacity
        )
    return c

# mimic lex_less of minizinc
def less_eq(x, y):
    return And([x[0] <= y[0]] +
          [Implies(
           And([x[i] == y[i] for i in range(k)]), x[k] <= y[k])
           for k in range(1, len(x))])

def read_file(instance):
    w = 0  # width
    n = 0  # number
    width = []
    height = []
    squre = []
    squresum = 0
    maxcircuit = 0
    secondcircuit = 0

    with open("./instances/ins-{0}.txt".format(instance), "r") as f:
        i = 0
        for line in f.readlines():
            if i == 0:
                w = int(line)
            elif i == 1:
                n = int(line)
            else:
                l = line.split()
                width.append(int(l[0]))
                height.append(int(l[1]))
                squre.append(int(l[0]) *int(l[1]))
            i += 1
    
    squresum = sum(squre)
    maxcircuit = squre.index(max(squre))
    del squre[maxcircuit]
    secondcircuit = squre.index(max(squre))
    minHeight = ceil(squresum / w)
    maxHeight = sum(height)

    data = {}
    data['minHeight'] = minHeight
    data['maxHeight'] = maxHeight
    data['maxcircuit'] = maxcircuit
    data['secondcircuit'] = secondcircuit
    return w,n,width,height,data

def build_model(w,n,width,height,data):
    Xposition = [Int("x_%s" % i) for i in range(n)]
    Yposition = [Int("y_%s" % i) for i in range(n)]

    h = symMax([Yposition[i] + height[i] for i in range(n)])

    ##constraints
    #h's domain
    domain_c = []
    for i in range(n):
        domain_c.append(And(Xposition[i] + width[i] <= w,
                            Xposition[i] >= 0, 
                            Yposition[i] >= 0,
                            Yposition[i] + height[i] <= h))
    #cumulative
    cumulative_x = cumulative(Xposition,width,height,h)
    cumulative_y = cumulative(Yposition,height,width,w)
    #noOverlap
    nooverlap_c = []
    for i in range(n):
        for j in range(n):
            if i < j:
                nooverlap_c.append(Or(Xposition[i] + width[i] <= Xposition[j],
                                      Xposition[i] >= Xposition[j] + width[j],
                                      Yposition[i] + height[i] <= Yposition[j],
                                      Yposition[i] >= Yposition[j] + height[j]))
    
    #noGapBetween
    nogap_c = []
    for i in range(n):
        nogap_c.append(And(
                Or(Xposition[i] == 0, 
                Or([Xposition[i] == Xposition[j] + width[j]
                    for j in range(n)])),
                Or(Yposition[i] == 0,
                Or([Yposition[i] == Yposition[j] + height[j]
                    for j in range(n)]))))

    #symmetry breaking
    symmetry_breaking_c = [less_eq([Yposition[data['maxcircuit']], Xposition[data['maxcircuit']]],
                                    [Yposition[data['secondcircuit']],Xposition[data['secondcircuit']]])]
    
    equal_c = [Implies(And(width[j] == width[i], height[j] == height[i]), 
        If(Xposition[j] == Xposition[i], Yposition[j] >= Yposition[i], Xposition[j] >= Xposition[i]))
        for j in range(n) for i in range(n)]

    constraints = domain_c +\
                    nooverlap_c +\
                    nogap_c +\
                    symmetry_breaking_c +\
                    equal_c
    
    return Xposition, Yposition, h, constraints

def plot_result(r):
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rectCollection = []

    for i in range(r['n']):
        rect = plt.Rectangle((r['x'][i],r['y'][i]),r['width'][i],r['height'][i])
        rectCollection.append(rect)

    ax.add_patch(rect)
    colors = np.linspace(0, 1, len(rectCollection))
    collection = PatchCollection(rectCollection, cmap=plt.cm.hsv, alpha=0.3)
    collection.set_array(colors)

    ax.add_collection(collection)
    ax.set_ylim(0,r['h']) 
    ax.set_xlim(0,r['w']) 
    ax.grid(True, linestyle='-.',color='gray')

    plt.plot()

    figpath = './sat/output/noRotation/'
    if not os.path.exists(figpath):
        os.makedirs(figpath)
        
    plt.savefig(figpath +'pic-{0}.jpg'.format(r['i']))
    plt.show()

def write_file(r):
    writepath = './sat/output/noRotation/'
    if not os.path.exists(writepath):
        os.makedirs(writepath)

    with open(writepath + 'out-{0}.txt'.format(r['i']),'w') as f:  
        f.writelines('%d %d \n' %(r['w'], r['h']))
        f.writelines(str(r['n'])+'\n')
        for i in range(r['n']):
            f.writelines('%d %d %d %d \n' % (r['width'][i],r['height'][i],r['x'][i],r['y'][i]))
        f.close()

    results = writepath + 'results.txt'
    if not os.path.exists(results) and r['i'] == 1:
        with open(results,'w') as f:
            f.writelines('%s %s %s\n' % ('instance', 'time', 'height'))
            f.writelines('%d %s %d \n' % (r['i'], r['duration'], r['h']))
            f.close()
    else:
        with open(results, 'a') as f:
            f.writelines('%d %s %d \n' % (r['i'], r['duration'], r['h']))
            f.close()

def run(instance):
    w,n,width,height,data = read_file(instance)
    s = Solver()
    s.set(timeout =300000)
    x, y, h, constraints = build_model(w,n,width,height,data)
    s.add(constraints)
    
    for i in range(data['minHeight'], data['maxHeight'] + 1):
        s.push()
        s.add(h == i)
        start = datetime.datetime.now()
        if s.check() == sat:
            model = s.model()
            duration = datetime.datetime.now() - start 
            print("It's best height is %d" % i)
            y_sol = []
            x_sol = []
            for i in range(n):
                y_sol.append(int(model.evaluate(y[i]).as_string()))
                x_sol.append(int(model.evaluate(x[i]).as_string()))
            h_sol = int(model.evaluate(h).as_string())
            return {'i':instance, 'w':w, 'n':n, 'width':width, 'height':height, 'x':x_sol, 'y':y_sol, 'h':h_sol, 'duration':str(duration)}
        else:
            print("Solution not found on height %d" % i)
            s.pop()
    print("instance {} Solution not found".format(instance))
    print(datetime.datetime.now() - start)
    return None


