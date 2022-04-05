from gevent import wait
from minizinc import Instance, Model, Solver
import matplotlib.pyplot as plt
import numpy as np
import time
from matplotlib.collections import PatchCollection
from itertools import combinations
from sklearn import naive_bayes
from sympy import false
from z3 import *
from math import ceil
import pandas as pd

### Here to wirte functions to help build the model

#get the max one in a list
def maxH(list):
    maxone = list[0]
    for i in list[1:]:
        maxone = If(maxone>i,maxone,i)
    return maxone

def minH(list):
    minone = list[0]
    for i in list:
        minone = If(minone<=i,minone,i)
    return minone

def cumulative(start, duration,requirement,capacity):
    c = []
    for u in requirement:
        c.append(
            sum([If(And(start[i] <= u, u < start[i] + duration[i]), requirement[i], 0)
            for i in range(len(start))]) <= capacity
        )
    return c

# single bool variable
def le(x, y):
    return x <= y

# on each position of (i,j) iterate n circuits
def less_eq(x, y):
    return And([le(x[0], y[0])] +
          [Implies(
           And([x[j] == y[j] for j in range(i)]), 
           le(x[i], y[i]))
           for i in range(1, len(x))]
    )


def read_file(instance):
    w = 0  # width
    n = 0  # number
    width = []
    height = []
    squre = []
    squresum = 0
    maxcircuit = 0
    secondMaxcircuit = 0

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
    squareHeight = ceil(squresum / w)
    maxcircuit = squre.index(max(squre))
    del squre[maxcircuit] 
    secondMaxcircuit = squre.index(max(squre))

    
    data = {}
    data['w'] = w
    data['n'] = n
    data['width'] = width
    data['height'] = height
    data['maxcircuit'] = maxcircuit
    data['squareHeight'] = squareHeight
    data['secondMaxcircuit'] = secondMaxcircuit
    data['instance'] = instance
    return data

def solve_instance(data):
    w = data['w']
    n = data['n']
    width = data['width']
    height = data['height']
    maxcircuit = data['maxcircuit']
    secondMaxcircuit = data['secondMaxcircuit']
    instance = data['instance']
    x = [Int("x_%s" % str(i+1)) for i in range(n)]
    y = [Int("y_%s" % str(i+1)) for i in range(n)]
    
    h = maxH([ y[i] + height[i] for i in range(n)])
    minWidth = minH([width[i] for i in range(n)])
    minHeight = minH([height[i] for i in range(n)])
    squareHeight = data['squareHeight']
    sumHeight = sum(height)

    # h's domain
    h_constraint = [And(squareHeight<=h , h<=sumHeight)]
    #domian constraint for x and y
    domain_x_l = [x[i] >= 0 for i in range(n)]
    #domain_x_u = [x[i] <= width[i]-minWidth for i in range(n)]
    domain_y_l = [y[i] >=0 for i in range(n)]
    #domain_y_u = [y[i] <= sumHeight-minHeight for i in range(n)]

    #width and height constraints
    width_constraint = [x[i] + width[i] <= w for i in range(n)]
    height_constraint = [y[i] + height[i] <= h for i in range(n) ]

    #cumulative
    cumulative_x = cumulative(x,width,height,h)
    cumulative_y = cumulative(y,height,width,w)

    #noOverlap
    noOverlap = []
    # for i in range(n):
    #     for j in range(n):
    for (i,j) in combinations(range(n),2):
        noOverlap.append(
            Or(
                x[i] + width[i] <= x[j],
                x[j] + width[j] <= x[i],
                y[i] + height[i] <= y[j],
                y[j] + height[j] <= y[i]
            )
        )
    
    #no Gap
    noGap = []
    for i in range(n):
        noGap.append(And(Or(
            x[i] == 0,
            Or([x[i] == x[j]+width[j] for j in range(n)])),
            Or(
            y[i] == 0,
            Or([y[i] == y[j]+height[j] for j in range(n)]))
    ))

    #symmetry breaking
    symmetry_breaking = [less_eq([y[maxcircuit],x[maxcircuit]],[y[secondMaxcircuit],x[secondMaxcircuit]])]

    #symmetry breaking for circuit with same width and height
    symmetry_breaking_same = []
    for i in range(n):
        r = []
        for j in range(n):
            if width[i]==width[j]:
                if height[i]==height[j]:
                    r.append(i)
        if len(r)>1:
            if minH(r)==i:
                for k in range(len(r)):
                    if k>0:
                        symmetry_breaking_same.append(less_eq([y[r[k-1]],x[r[k-1]]],[y[r[k]],x[r[k]]]))

    constraints =domain_x_l + domain_y_l + width_constraint + height_constraint + \
        noOverlap + cumulative_x + cumulative_y + noGap + symmetry_breaking + symmetry_breaking_same
        

    opt = Optimize()
    opt.set(timeout=300000)
    opt.add(constraints)
    opt.minimize(h)

    y_sol = []
    x_sol = []
    start = time.time()
    if opt.check() == sat:
        model = opt.model()
        duration = time.time() - start
        for i in range(n):
            y_sol.append(int(model.evaluate(y[i]).as_string()))
            x_sol.append(int(model.evaluate(x[i]).as_string()))
        h_sol = int(model.evaluate(h).as_string())
        write_file(instance,x_sol,y_sol,width,height,w,n,h_sol,duration)
        plot_result(instance,x_sol,y_sol,width,height,w,n,h_sol)
    else:
        duration = time.time() - start
        print(f'{duration * 1000:.2f} ms')
        print("Solution not found")

    return duration

def plot_result(instance,Xposition,Yposition,width,height,w,n,h):
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rectCollection = []

    for i in range(n):
        rect = plt.Rectangle((Xposition[i],Yposition[i]),width[i],height[i])
        rectCollection.append(rect)

    ax.add_patch(rect)
    colors = np.linspace(0, 1, len(rectCollection))
    collection = PatchCollection(rectCollection, cmap=plt.cm.hsv, alpha=0.3)
    collection.set_array(colors)

    ax.add_collection(collection)
    ax.set_ylim(0,h) 
    ax.set_xlim(0,w) 
    ax.grid(True, linestyle='-.',color='gray')

    plt.plot()
    plt.savefig('./smt/output/noRotation/pic-{0}.jpg'.format(instance))
    plt.close(fig)
    #plt.show()

def write_file(instance,Xposition,Yposition,width,height,w,n,h,duration):
        with open('./smt/output/noRotation/out-{0}.txt'.format(instance),'w') as f:  
            f.writelines('%d %d \n' %(w, h))
            f.writelines(str(n)+'\n')
            for i in range(n):
                f.writelines('%d %d %d %d \n' %(width[i],height[i],Xposition[i],Yposition[i]))
            # f.writelines('========== \n')
            #f.writelines("%.2f ms" % duration * 1000)



def main():

    instance = []
    time = []
    for i in range(1,41):
        data = read_file(i)
        t = solve_instance(data)
        time.append(round(t,3))
        instance.append(i)
    list_data={'instances':instance,'timeElapse':time}
    runingData=pd.DataFrame(data=list_data)
    runingData.to_csv('./smt/output/noRotation/result_noRotation.csv') 
    # data = read_file(1)
    # solve_instance(data)

if __name__ == '__main__':
    main()
