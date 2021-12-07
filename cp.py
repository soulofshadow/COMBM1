from minizinc import Instance, Model, Solver
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection

w = 0  # width
n = 0  # number
width = []
height = []
p = 6  #instance 
with open("./instances/ins-{0}.txt".format(p), "r") as f:
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

# Load vlsi model from file
vlsi = Model("./vlsi.mzn")
# Find the MiniZinc solver configuration for Gecode
gecode = Solver.lookup("gecode")
# Create an Instance of the vlsi model for Gecode
instance = Instance(gecode, vlsi)
# Assign 4 to n
instance["n"] = n
instance["w"] = w
instance["circuitWidth"] = width
instance["circuitHeight"] = height
result = instance.solve()

# with instance.branch() as opt:
#     opt.add_string("solve minimize height;\n")
#     res = opt.solve()
#     obj = res["objective"]
# instance.add_string(f"constraint sum(x) = {obj};\n")
# result = instance.solve(all_solutions=True)
# for sol in result.solution:
#     print(sol.x)

# Output the array q
xValue = result["Xposition"]
yValue = result["Yposition"]


fig = plt.figure()
ax = fig.add_subplot(111)
rectCollection = []

with open('./output/out-{0}.txt'.format(p),'w') as f:  
    f.writelines('%d %d \n' %(w,result["objective"]))
    f.writelines(str(n)+'\n')
    for i in range(n):
        f.writelines('%d %d %d %d \n' %(width[i],height[i],xValue[i],yValue[i]))



# print('%d %d' %(w,result["objective"]))
# print(n)
for i in range(n):
    rect = plt.Rectangle((xValue[i],yValue[i]),width[i],height[i])
    rectCollection.append(rect)
    # print('%d %d %d %d' %(width[i],height[i],xValue[i],yValue[i]))

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
plt.savefig('./output/pic-{0}.jpg'.format(p))
plt.show()

