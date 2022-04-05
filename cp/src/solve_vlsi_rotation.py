import datetime
from fileinput import filename
from minizinc import Instance, Model, Solver
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
import os
import pandas as pd



def cpSolver(width,height,modelPath,circuitNum,fixedWidth):
    vlsi = Model(modelPath)
    # Find the MiniZinc solver configuration for Gecode
    gecode = Solver.lookup("gecode")
    # Create an Instance of the vlsi model for Gecode
    instance = Instance(gecode, vlsi)
    instance["n"] = circuitNum
    instance["w"] = fixedWidth
    instance["width"] = width
    instance["height"] = height
    result = instance.solve(timeout=datetime.timedelta(minutes=5)) #set time limit to 5 minutes
    return result




modelPath = "./cp/src/cp_rotation.mzn"
w = 0  # width
n = 0  # number
fileIndex = 0 #file sequence
instances=[]
timeElapse = [] #modle's run time 
solutions = []  #number of solution 
failures = [] # times of failure
restarts = [] #times of restart
files = os.listdir('./instances') #all the file names
files.sort(key = lambda x: int(x[4:-4])) #sort the file in increasing order
for file in files:
    width = []
    height = []
    fileIndex = int(file[4:-4])
    with open('./instances/{}'.format(file)) as f:
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
            i += 1
    result = cpSolver(width,height,modelPath,n,w)
    instances.append(fileIndex)
    run_time = result.statistics['time'].total_seconds()
    timeElapse.append(run_time)
    solutions.append(result.statistics['solutions']) 
    failures.append(result.statistics['failures'] )
    restarts.append(result.statistics['restarts'] )
    if result.statistics['solutions']== 0:
        xValue = [] #no solution 
        yValue = []
    else:
        xValue = result["x"] #circuit's x coordinate
        yValue = result["y"] #circuit's y coordinate
        rotation = result['rotation']
        #write the output file
        with open('./cp/output/inputOrder_min_noRestart_rotation/out-{0}.txt'.format(fileIndex),'w') as f:  
            f.writelines('%d %d \n' %(w,result["objective"]))
            f.writelines(str(n)+'\n')
            for i in range(n):
                f.writelines('%d %d %d %d %s \n' %(width[i],height[i],xValue[i],yValue[i],rotation[i]))
            # f.writelines('================')
            # f.writelines('time(s):' + str(run_time))
        
        #plot the solution
        fig = plt.figure()
        fig.suptitle('instance-{}'.format(fileIndex))
        ax = fig.add_subplot(111) 
        rectCollection = []
        for i in range(n):
            if rotation[i]:
                rect = plt.Rectangle((xValue[i],yValue[i]),height[i],width[i])
            else:
                rect = plt.Rectangle((xValue[i],yValue[i]),width[i],height[i])
            rectCollection.append(rect)

        ax.add_patch(rect)
        colors = np.linspace(0, 1, len(rectCollection))
        collection = PatchCollection(rectCollection, cmap=plt.cm.hsv, alpha=0.3)
        collection.set_array(colors)
        ax.add_collection(collection)
        #ax.add_line(line)

        ax.set_ylim(0,result["objective"]) 
        ax.set_xlim(0,w) 
        ax.grid(True, linestyle='-.',color='gray')

        plt.plot()
        plt.savefig('./cp/output/inputOrder_min_noRestart_rotation/pic-{0}.jpg'.format(fileIndex))
        plt.close(fig)
        #plt.show()


# put the data into csv file 
list_data={'instances':instances,'timeElapse':timeElapse,'solutions':solutions,'failures':failures,'restarts':restarts}
runingData=pd.DataFrame(data=list_data)
runingData.to_csv('./cp/output/inputOrder_min_noRestart_rotation/result.csv')



