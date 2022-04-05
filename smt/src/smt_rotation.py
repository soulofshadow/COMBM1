import numpy as np
import time
from itertools import combinations
from z3 import *
import smt as nr
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import pandas as pd


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
    rotation = [Bool("ro_%s" % str(i+1)) for i in range(n)]

    width_r = [If(And(rotation[i],width[i] != height[i],height[i] <= w),height[i],width[i]) for i in range(n)]
    height_r = [If(And(rotation[i],width[i] != height[i],height[i] <= w),width[i],height[i]) for i in range(n)]
    


    h = nr.maxH([y[i] + height_r[i] for i in range(n)])
    minWidth = nr.minH([width_r[i] for i in range(n)])
    minHeight = nr.minH([height_r[i] for i in range(n)])
    squareHeight = data['squareHeight']
    sumHeight = sum(height_r)


    # h's domain
    
    # h_constraint = [And(squareHeight<=h , h<=sumHeight)]
    #domian constraint for x and y
    domain_x_l = [x[i] >= 0 for i in range(n)]
    #domain_x_u = [x[i] <= width_r[i]-minWidth for i in range(n)]
    domain_y_l = [y[i] >=0 for i in range(n)]
    #domain_y_u = [y[i] <= sumHeight-minHeight for i in range(n)]

    #rotation_constraint = [Implies(height[i]>w,rotation[i]==False) for i in range(n)]

    #width and height constraints
    width_constraint = [x[i] + width_r[i] <= w for i in range(n)]
    height_constraint = [y[i] + height_r[i] <= h for i in range(n) ]

    #cumulative
    cumulative_x = nr.cumulative(x,width_r,height_r,h)
    cumulative_y = nr.cumulative(y,height_r,width_r,w)

    #noOverlap
    noOverlap = []
    for (i,j) in combinations(range(n),2):
        noOverlap.append(
            Or(
                x[i] + width_r[i] <= x[j],
                x[j] + width_r[j] <= x[i],
                y[i] + height_r[i] <= y[j],
                y[j] + height_r[j] <= y[i]
            )
        )
    
    #no Gap
    noGap = []
    for i in range(n):
        noGap.append(And(Or(
            x[i] == 0,
            Or([x[i] == x[j]+width_r[j] for j in range(n)])),
            Or(
            y[i] == 0,
            Or([y[i] == y[j]+height_r[j] for j in range(n)]))
    ))

    #symmetry breaking
    symmetry_breaking = [nr.less_eq([y[maxcircuit],x[maxcircuit]],[y[secondMaxcircuit],x[secondMaxcircuit]])]

    #symmetry breaking for circuit with same width and height
    symmetry_breaking_same = []
    for i in range(n):
        r = []
        for j in range(n):
            if width[i]==width[j]:
                if height[i]==height[j]:
                    r.append(i)
            if width[i]==height[j]:
                if height[i] == width[j]:
                    if i not in r:
                        r.append(i)
        if len(r)>1:
            if nr.minH(r)==i:
                for k in range(len(r)):
                    if k>0:
                        symmetry_breaking_same.append(nr.less_eq([y[r[k-1]],x[r[k-1]]],[y[r[k]],x[r[k]]]))

    constraints = domain_x_l + domain_y_l + width_constraint + height_constraint + noOverlap + \
        cumulative_x + cumulative_y + noGap + symmetry_breaking + symmetry_breaking_same
        

    opt = Optimize()
    opt.set(timeout=300000)
    opt.add(constraints)
    opt.minimize(h)

    y_sol = []
    x_sol = []
    r_sol = []
    start = time.time()
    if opt.check() == sat:
        model = opt.model()
        duration = time.time() - start
        for i in range(n):
            y_sol.append(int(model.evaluate(y[i]).as_string()))
            x_sol.append(int(model.evaluate(x[i]).as_string()))
            r_value = model[rotation[i]]
            if r_value is None:
                r_sol.append(False)
            else:
                r_sol.append(r_value)
        h_sol = int(model.evaluate(h).as_string())
        write_file(instance,x_sol,y_sol,width,height,w,n,h_sol,duration,r_sol)
        plot_result(instance,x_sol,y_sol,width,height,w,n,h_sol,r_sol)
    else:
        duration = time.time() - start
        print(f'{duration * 1000:.1f} ms')
        print("Solution not found")
    
    return duration

def write_file(instance,x,y,width,height,w,n,h,duration,rotation):
        with open('./smt/output/rotation/out-{0}.txt'.format(instance),'w') as f:  
            f.writelines('%d %d \n' %(w, h))
            f.writelines(str(n)+'\n')
            for i in range(n):
                f.writelines('%d %d %d %d %s\n' %(width[i],height[i],x[i],y[i],rotation[i]))
            f.writelines('========== \n')
            f.writelines("%.3f s" % duration)

def plot_result(instance,x,y,width,height,w,n,h,rotation):
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    rectCollection = []

    for i in range(n):
        if rotation[i]:
            rect = plt.Rectangle((x[i],y[i]),height[i],width[i])
        else:
            rect = plt.Rectangle((x[i],y[i]),width[i],height[i])
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
    plt.savefig('./smt/output/rotation/pic-{0}.jpg'.format(instance))
    plt.close(fig)
    #plt.show()

def main():

    # data = nr.read_file(13)
    # solve_instance(data)
    instance = []
    time = []
    for i in range(1,41):
        data = nr.read_file(i)
        t = solve_instance(data)
        time.append(round(t,3))
        instance.append(i)
    list_data={'instances':instance,'timeElapse':time}
    runingData=pd.DataFrame(data=list_data)
    runingData.to_csv('./smt/output/rotation/result_rotation.csv') 

if __name__ == '__main__':
    main()
