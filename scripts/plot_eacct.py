import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from subprocess import Popen, PIPE
import argparse
import numpy as np
import os
import pdb

class Plotter():
    def __init__(self):
        self.data = {}

        self.filename = "tmp.csv"

        # Color Palettes
        self.arch_palette ={"Rome": "tab:blue",
                            "Genoa": "tab:orange",
                            "A100": "tab:green",
                            "H100": "tab:red",
                            "Fat_Rome": "tab:purple",
                            "Fat_Genoa": "tab:brown"
                            }

        #Roofline Metrics
        # Rome
        self.ROME_name = "AMD Rome 7H12 (2x)"
        self.ROME_ncores = 128
        self.ROME_freq = 2.6 # GHz
        self.ROME_NDPs = 16 # Has two 256-bit Fused Multiply-Add (FMA) units and can deliver up to 16 double-precision floating point operations (flops) per cycle.
        self.ROME_DP_RPEAK = self.ROME_ncores * self.ROME_freq * self.ROME_NDPs #5324.8 Value confirmed from AMUuProf (4.1.424)
        self.ROME_SP_RPEAK = self.ROME_DP_RPEAK*2.0
        self.ROME_HP_RPEAK = self.ROME_SP_RPEAK*2.0
        self.ROME_DP_NOSIMD_RPEAK = 1331.20 # found from AMDuprof
        self.ROME_DRAMBW = 409.60 # 204.8 single socket (Value taken from AMUuProf (4.1.424))
       
        # Genoa
        self.GENOA_name = "AMD Genoa 9654 (2x)"
        self.GENOA_ncores = 192
        self.GENOA_freq = 2.4 # GHz
        self.GENOA_NDPs = 16 # Has two 256-bit Fused Multiply-Add (FMA) units and can deliver up to 16 double-precision floating point operations (flops) per cycle.
        self.GENOA_DP_RPEAK = self.GENOA_ncores *  self.GENOA_freq * self.GENOA_NDPs # 7372.80 GFLOPs
        self.GENOA_SP_RPEAK = self.GENOA_DP_RPEAK * 2.0
        self.GENOA_HP_RPEAK = self.GENOA_DP_RPEAK * 4.0
        self.GENOA_DP_NOSIMD_RPEAK = 1843.97 # found from AMDuprof

        self.GENOA_N_memory_channels = 12 * 2 # 2 sockets
        self.GENOA_memory_freq = 4800 #MHz
        self.GENOA_DRAMBW = (64./8.) * self.GENOA_memory_freq * self.GENOA_N_memory_channels * (1e6/1e9) # (bits/bytes) * Mem_freq * N channels * (Mega/Giga)  Per Socket Mem BW 460.8 GB/s

        # A100s
        self.XEON_name = "Intel Xeon Platinum 8360Y (2x)"
        self.XEON_ncores = 72
        self.XEON_freq = 2.4 # GHz
        self.XEON_NDPs = 32 # Intel Skylake processors (the Gold or Platinum family) have two AVX512 units capable of performing 32 DP ops/cycle.
        self.XEON_DP_RPEAK = self.XEON_ncores *  self.XEON_freq * self.XEON_NDPs # 7372.80 GFLOPs
        self.XEON_SP_RPEAK = self.XEON_DP_RPEAK * 2.0
        self.XEON_HP_RPEAK = self.XEON_DP_RPEAK * 4.0
        self.XEON_N_memory_channels = 8 * 2 # 2 sockets
        self.XEON_memory_freq = 3200 #MHz
        self.XEON_DRAMBW = (64./8.) * self.XEON_memory_freq * self.XEON_N_memory_channels * (1e6/1e9) # (bits/bytes) * Mem_freq * N channels * (Mega/Giga)

        self.A100_DP_RPEAK =   9700 # FP64 GFlops https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf
        self.A100_SP_RPEAK =  19500 # FP32 GFlops 
        self.A100_HP_RPEAK = 312000 # FP16 Tensor core GFlops 
        self.A100_HBM2 = 1935 #GB/s

        # H100s
        self.HGENOA_name = "AMD EPYC 9334 32-Core Processor"
        self.HGENOA_ncores = 64
        self.HGENOA_freq = 2.7 # GHz
        self.HGENOA_NDPs = 16 # Has two 256-bit Fused Multiply-Add (FMA) units and can deliver up to 16 double-precision floating point operations (flops) per cycle.
        self.HGENOA_DP_RPEAK = self.HGENOA_ncores *  self.HGENOA_freq * self.HGENOA_NDPs # 7372.80 GFLOPs
        self.HGENOA_SP_RPEAK = self.HGENOA_DP_RPEAK * 2.0
        self.HGENOA_HP_RPEAK = self.HGENOA_DP_RPEAK * 4.0
        self.HGENOA_N_memory_channels = 12 * 2 # 2 sockets
        self.HGENOA_memory_freq = 4800 #MHz
        self.HGENOA_DRAMBW = (64./8.) * self.HGENOA_memory_freq * self.HGENOA_N_memory_channels * (1e6/1e9) # (bits/bytes) * Mem_freq * N channels * (Mega/Giga)

        self.H100_DP_RPEAK =  34000 # FP64 GFlops https://www.nvidia.com/en-us/data-center/h100/
        self.H100_SP_RPEAK =  67000 # FP32 GFlops 
        self.H100_HP_RPEAK = 1979000 # FP16 Tensor core GFlops 
        self.H100_HBM2 = 3300 #GB/s


    def get_partition(self, data):

        data['Arch'] = "UNK"

        data['node_type'] = data['NODENAME'].str.extract(r'([a-zA-Z]*)')
        data['node_number'] = data['NODENAME'].str.extract(r'(\d+)').astype(int)

        try:
            data.loc[(data['node_type'] == "tcn") & (data['node_number'] <= 525) , "Arch"] = "Rome"
        except ValueError:
            pass
        try:
            data.loc[(data['node_type'] == "tcn") & (data['node_number'] > 525) , "Arch"] = "Genoa"
        except ValueError:
            pass
        try:
            data.loc[(data['node_type'] == "gcn") & (data['node_number'] <= 72) , "Arch"] = "A100"
        except ValueError:
            pass
        try:
            data.loc[(data['node_type'] == "gcn") & (data['node_number'] > 72) , "Arch"] = "H100"
        except ValueError:
            pass
        try:
            data.loc[(data['node_type'] == "hcn"), "Arch"] = "high_mem"
        except ValueError:
            pass
        try:
            data.loc[(data['node_type'] == "fcn") & (data['node_number'] <= 72), "Arch"] = "Fat_Rome"
        except ValueError:
            pass
        try:
            data.loc[(data['node_type'] == "fcn") & (data['node_number'] >= 73) & (data['node_number'] <= 120), "Arch"] = "Fat_Gome"
        except ValueError:
            pass

        return(data)


    def eacct_avg(self,jobid,stepid = 0):

        self.filename = jobid+"."+str(stepid)+'.csv'

        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

        process = Popen(['eacct','-j',jobid+"."+str(stepid),'-l','-c',self.filename], stdout=PIPE, stderr=PIPE)

        output, error = process.communicate()
        output = output.decode('ISO-8859-1').strip()
        error = error.decode('ISO-8859-1').strip()

        if "No jobs found" in str(output):
            print(output)
            exit(1)
                
        tmp_data = pd.read_csv(self.filename,delimiter=";")

        tmp_data = self.get_partition(tmp_data)

        tmp_data['OI'] = tmp_data['CPU-GFLOPS']/tmp_data['MEM_GBS']

        self.data = tmp_data


    def eacct_loop(self,jobid,stepid = 0):

        self.filename = jobid+"."+str(stepid)+'.csv'

        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

        process = Popen(['eacct','-j',jobid+"."+str(stepid),'-r','-c',self.filename], stdout=PIPE, stderr=PIPE)

        output, error = process.communicate()
        output = output.decode('ISO-8859-1').strip()
        error = error.decode('ISO-8859-1').strip()
        if "No loops retrieved" in str(output):
            print(output)
            exit(1)

                
        tmp_data = pd.read_csv(self.filename,delimiter=";")

        tmp_data = self.get_partition(tmp_data)

        tmp_data['time'] = (pd.to_datetime(tmp_data['DATE']) - pd.to_datetime(tmp_data['DATE']).min()).dt.seconds

        self.data = tmp_data


    def timeline(self):

        data = self.data

        fig, axs = plt.subplots(nrows=5, ncols=1,sharex=True)

        arch = data['Arch'].unique()

        if arch == "Rome":
            DRAMBW = self.ROME_DRAMBW
            POWER = 280*2

        if arch == "Genoa":
            DRAMBW = self.GENOA_DRAMBW
            POWER = 360*2

        if arch == "A100":
            DRAMBW = self.XEON_DRAMBW
            POWER = 250*2 + 400*4

        if arch == "H100":
            DRAMBW = self.HGENOA_DRAMBW
            POWER = 210*2 + 700*4


        sns.lineplot(data=data, x="time", y="CPI", hue="NODENAME", ax = axs[0])

        axs[1].plot(np.linspace(-10,1e6,100),np.ones(100)*DRAMBW,label="MAX DRAMBW "+ str(DRAMBW) + "GB/s",ls='--',color='black')
        sns.lineplot(data=data, x="time", y="MEM_GBS", hue="NODENAME", ax = axs[1],legend=False)

        sns.lineplot(data=data, x="time", y="IO_MBS", hue="NODENAME", ax = axs[2],legend=False)
        sns.lineplot(data=data, x="time", y="GFLOPS", hue="NODENAME", ax = axs[3],legend=False)
        axs[4].plot(np.linspace(-10,1e6,100),np.ones(100)*POWER,label="MAX POWER "+ str(POWER) +" (W)",ls='--',color='black')

        sns.lineplot(data=data, x="time", y="DC_NODE_POWER_W", hue="NODENAME", ax = axs[4],legend=False)

        axs[0].set_ylim(0,1.1)
        axs[1].set_ylim(0,DRAMBW+50)
        axs[4].set_ylim(0,POWER+50)
        axs[0].legend(loc=2, prop={'size': 6}, bbox_to_anchor=[1, 1])
        axs[1].legend(loc=2, prop={'size': 6}, bbox_to_anchor=[1, 1])
        axs[4].legend(loc=2, prop={'size': 6}, bbox_to_anchor=[1, 1])

        axs[0].set_ylabel("CPI")
        axs[1].set_ylabel("DRAM BW\n(GB/s)")
        axs[2].set_ylabel("IO (MB/s)")
        axs[3].set_ylabel("Gflop/s")
        axs[4].set_ylabel("Node Power (W)")

        plt.xlim(0,data['time'].max()+5)

        axs[4].set_xlabel("time (s)")

        plt.tight_layout()
        plt.savefig("timeline." + self.filename.replace(".csv",".png"))




    def roofline(self):

        data = self.data        
        for arch in data['Arch'].unique():

            plot_data = data[data['Arch'] == arch]

            plt.close()
            sns.set_style("ticks")

            fig = plt.figure()
            fig.set_figheight(5)
            fig.set_figwidth(8)
            ax = plt.subplot(111)

            # This will be set below based on Arch
            DP_Rpeak = 1 
            Ncores = 1
            NO_ILP_Rpeak = 1
            DRAMBW = 1
            # Now Set them
            if arch == "Rome":
                CPU_NAME = self.ROME_name
                DP_Rpeak = self.ROME_DP_RPEAK
                NO_SIMD_DP_Rpeak = self.ROME_DP_NOSIMD_RPEAK
                DRAMBW = self.ROME_DRAMBW
                Ncores = self.ROME_ncores

            if arch == "Genoa":
                CPU_NAME = self.GENOA_name
                DP_Rpeak = self.GENOA_DP_RPEAK
                NO_SIMD_DP_Rpeak = self.GENOA_DP_NOSIMD_RPEAK
                DRAMBW = self.GENOA_DRAMBW
                Ncores = self.GENOA_ncores
            if arch == "A100":
                CPU_NAME = self.XEON_name
                DP_Rpeak = self.XEON_DP_RPEAK
                DRAMBW = self.XEON_DRAMBW
                Ncores = self.XEON_ncores
                NO_SIMD_DP_Rpeak = 0 #UNK

            if arch == "H100":
                CPU_NAME = self.HGENOA_name
                DP_Rpeak = self.HGENOA_DP_RPEAK
                DRAMBW = self.HGENOA_DRAMBW
                Ncores = self.HGENOA_ncores
                NO_SIMD_DP_Rpeak = 0 #UNK

            # get other Precisions
            SP_Rpeak = DP_Rpeak * 2.0
            HP_Rpeak = DP_Rpeak * 4.0
            # Work Calculated on a node basis
            NO_SIMD_DP_W = np.linspace(1./(Ncores*10),1.0,1000)*NO_SIMD_DP_Rpeak # thousand is just some arbitraty factor to make the line
            D_W = np.linspace(1./(Ncores*10),1.0,1000)*DP_Rpeak # thousand is just some arbitraty factor to make the line
            S_W = np.linspace(1./(Ncores*10),1.0,1000)*SP_Rpeak
            H_W = np.linspace(1./(Ncores*10),1.0,1000)*HP_Rpeak 
            # Operation Intensity (Flops/Byte)
            NO_SIMD_DP_I = NO_SIMD_DP_W/DRAMBW
            D_I = D_W/DRAMBW
            S_I = S_W/DRAMBW
            H_I = H_W/DRAMBW


            # Main Memory Line
            ax.plot(H_I,H_W,c='black')

            ax.text(np.median(H_I)/100., np.median(H_W)/100.+ 30, "DRAM BW = "+ str(DRAMBW)+" GB/s", fontsize=8,rotation=45)
            
            # CPU Bound Lines
            ax.plot(np.linspace(np.max(NO_SIMD_DP_I),5e10,len(NO_SIMD_DP_I)),NO_SIMD_DP_Rpeak*np.ones(len(NO_SIMD_DP_I)), c='black', ls = "--")
            ax.plot(np.linspace(np.max(D_I),5e10,len(D_I)),DP_Rpeak*np.ones(len(D_W)), c='black')
            ax.plot(np.linspace(np.max(S_I),5e10,len(S_I)),SP_Rpeak*np.ones(len(S_W)), c='black')
            ax.plot(np.linspace(np.max(H_I),5e10,len(H_I)),HP_Rpeak*np.ones(len(H_W)), c='black')
            
            Ytext_factor = 0.05
            ax.text(np.max(H_I)+ 600, np.max(NO_SIMD_DP_W) + np.max(NO_SIMD_DP_W) * Ytext_factor, "NO SIMD DP = "+ str(round(NO_SIMD_DP_Rpeak,2))+" GFLOPS", fontsize=8)
            ax.text(np.max(H_I)+ 600, np.max(H_W) + np.max(H_W) * Ytext_factor, "HP Rpeak = "+ str(round(HP_Rpeak,2))+" GFLOPS", fontsize=8)
            ax.text(np.max(H_I)+ 600, np.max(S_W) + np.max(S_W) * Ytext_factor, "SP Rpeak = "+ str(round(SP_Rpeak,2))+" GFLOPS", fontsize=8)
            ax.text(np.max(H_I)+ 600, np.max(D_W) + np.max(D_W) * Ytext_factor, "DP Rpeak = "+ str(round(DP_Rpeak,2))+" GFLOPS", fontsize=8)

            ax.set_title(CPU_NAME)


            if "Method" in data.columns:
                g =sns.scatterplot(x="OI", y="CPU-GFLOPS",
                            linewidth=0,
                            hue='JOBID',
                            #style="PI",
                            data=plot_data, ax=ax)
            else:
                #This needs to be fixed
                g = sns.scatterplot(x="OI", y="CPU-GFLOPS",
                            linewidth=0,
                            hue='JOBID',
                            #style="PI",
                            data=plot_data, ax=ax)

            plt.xscale("log")
            plt.yscale("log")
            g.legend(loc='upper right', bbox_to_anchor=(1.30, 1.01))
            #plt.legend()
            ax.set_xlim(0.1,1e4)
            ax.set_ylim(10,1e5)
            ax.set_ylabel("Performance (GFLOPS)")
            ax.set_xlabel("Operational Intensity (FLOPS/byte)")

            plt.tight_layout()
            plt.savefig("roofline." + self.filename.replace(".csv",".png"),dpi=200)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-r", "--roofline", metavar="JobID/s", help="Plot Rooflines from eacct tool" ,type=str, nargs='+')
    parser.add_argument("-t", "--timeline", metavar="JobID/s", help="Plot Timeline from eacct tool (if loops are reported)" ,type=str, nargs='+')
    
    args = parser.parse_args()

    if args.roofline:
        plotter = Plotter()
        for jobid in args.roofline:
            plotter.eacct_avg(jobid)
            plotter.roofline()
    
    if args.timeline:
        plotter = Plotter()
        for jobid in args.timeline:
            plotter.eacct_loop(jobid)
            plotter.timeline()


        
        
