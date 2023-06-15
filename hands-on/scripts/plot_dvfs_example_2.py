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

Size = [] 
Time = [] 
Joule = []  
Watt = []
Freq = []

for infile in sys.argv[1:]:
    data = np.loadtxt(infile).T
    Size.append(data[0])
    Time.append(data[1])
    Joule.append(data[2])  
    Watt.append(data[3])

    Freq.append(int(infile.split("_")[2].split(".")[0]))

Size  = np.array(Size)
Time  = np.array(Time)
Joule = np.array(Joule)
Watt  = np.array(Watt)
Freq  = np.array(Freq)

axs[0].set_title("Matrix Multiplication ({} x {}) ".format(Size[0],Size[0]))
axs[0].plot(Freq,Time,label=infile)
axs[0].set_ylabel("Execution Time (s)")

axs[1].plot(Freq,Joule)
axs[1].set_ylabel("Energy (J)")

axs[2].plot(Freq,Watt)
axs[2].set_ylabel("Power (W)")
axs[2].set_xlabel("Frequency (Hz)")

plt.savefig("dvfs_example_2.png",dpi=150)

