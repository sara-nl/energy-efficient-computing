from matplotlib import pyplot as plt
import numpy as np
import sys

if not sys.argv[1]:
    print("You need to pass this script a results.txt file (or multiple results.txt /s)")
    exit (1)
if ".txt" not in sys.argv[1]:
    print("Need to pass this script a .txt file")
    exit (1)

fig, axs = plt.subplots(3, 1,sharex=True)

time_max = 0
joule_max = 0
watt_max = 0

for infile in sys.argv[1:]:

    data = np.loadtxt(infile).T

    Size=data[0] 
    Time=data[1] 
    Joule=data[2]  
    Watt=data[3] 

    if np.max(Time) > time_max:
        time_max=np.max(Time)
    if np.max(Joule) > joule_max:
        joule_max=np.max(Joule)
    if np.max(Watt) > watt_max:
        watt_max=np.max(Watt)

    axs[0].scatter(Size,Time,label=infile,s=10)
    axs[0].set_ylabel("Execution Time (s)")
    axs[0].legend(loc =2, fontsize = 'xx-small')

    axs[1].scatter(Size,Joule,s=10)
    axs[1].set_ylabel("Energy (J)")
    axs[1].set_ylim(-100,np.max(joule_max)+100)

    axs[2].scatter(Size,Watt,s=10)
    axs[2].set_ylabel("Power (W)")
    axs[2].set_xlabel("Matrix Size")
    axs[2].set_ylim(0,500)

plt.savefig("time_energy_power.png",dpi=150)

