import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from subprocess import Popen, PIPE
import argparse
import pdb

class Plotter():
    def __init__(self):
        self.data = {}

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


        # H100s Needed

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

    def eacct(self,jobid,stepid = 0):

        process = Popen(['eacct','-j',jobid+"."+str(stepid),'-l','-c',jobid+str(stepid)+'.csv'], stdout=PIPE, stderr=PIPE)

        output, error = process.communicate()
        output = output.decode('ISO-8859-1').strip()
        error = error.decode('ISO-8859-1').strip()
                
        tmp_data = pd.read_csv(jobid+str(stepid)+'.csv',delimiter=";")
        self.data = tmp_data



    def roofline(self,data,*args, **kwargs):
        
        hue = kwargs.get('hue', None)
        style = kwargs.get('style', None)
        sort_by = kwargs.get('sort_by', None)
        title = kwargs.get('title', None)

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
                g =sns.scatterplot(x="OI", y="Gflops",
                            linewidth=0,
                            hue='Application',
                            style="PI",
                            data=plot_data, ax=ax)
            else:
                #This needs to be fixed
                g = sns.scatterplot(x="OI", y="Gflops",
                            linewidth=0,
                            hue='Application',
                            style="PI",
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
            plt.savefig("plots/earl/arch/roofline_" + arch + ".png",dpi=200)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--jobid",metavar="JobID/s", help="Plot Rooflines from eacct tool" ,type=str, nargs='+')
    args = parser.parse_args()


    if args.jobid:

        plotter = Plotter()

        plotter.eacct(args.jobid[0])

        plotter.roofline()
        
        
