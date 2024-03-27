# Energy efficient computing

## Schedule
### April 18 2024 (start 10:00 end 15:00)
- (10:00-11:00) Introduction 
- (11:00-12:00) Energy Monitoring
- (12:00-13:00) Lunch
- (13:00-14:00) Dynamic Voltage Frequency Scaling
- (14:00-15:00) Energy Optimization


# Practical information
- [How to connect to Snellius](#how-to-connect-to-snellius)
- [How to interact with the course.](#how-to-interact-with-the-course)
- [Reservations available for the course](#Reservations-available-for-the-course)
- [Previous Course Material](#previous-course-material)


## How to connect to Snellius

>Snellius uses a white-list of ip-addresses and only from those locations you can access the system. 

If you are connecting with eduroam (from the SURF Amsterdam office) you should be able to go directly to snellius. This IP has been whitelisted. 
```
ssh username@snellius.surf.nl
```

If you are connecting from outside SURF Amsterdam you will have to have your IP whitelisted by us. Please send us your IP address to be white listed. 
You can find the blocked ip-address when logging in to Snellius using ssh -v [login]@snellius.surf.nl.

If whitelisting is not an option for you, you can always access Snellius via the "Doornode"
```
ssh user@doornode.surfsara.nl
```
The doornode is separate login server, that can be accessed from anywhere in the world: doornode.surfsara.nl (thus using `ssh user@doornode.surfsara.nl`). This server can be accessed with your usual login and password, after which you get a menu with systems that you can login to. Select 'Snellius' and type your password a second time. You are now logged on to Snellius. Please note that you cannot copy files or use X11 when using the door node.


## How to interact with the course.

This course is a "command line" course. We assume that you are somewhat comfortable with using the command line. This comes with some caveats, mainly its not so "nice" to view images or GUIs. Though not essential to have nice "viewing" capabilities, for this course we will be looking at some nice plots `.pngs`. Here are some suggested remedies.

1. Window forwarding `ssh -X username@snellius.surf.nl`. To redirect any graphics output from the HPC system to your own system, you'll need an X-server like [XQuartz](https://www.xquartz.org). Download and install it. Then, login to the HPC system using (note that X is capitalized). 
   - To view a png while on snellius use `display file.png`
2. [MobaXterm](https://mobaxterm.mobatek.net) (windows) 
3. Visual Studio Code we have documentation on how to set it up [here](https://servicedesk.surf.nl/wiki/display/WIKI/Visual+Studio+Code+for+remote+development) (go to the Running the VS Code Server on a login node section)


## Reservations available for the course

### Day 1 (energy_efficiency_course_cpu)

How to get there
```
salloc --ntasks=32 -t 02:00:00 -p thin --reservation=energy_efficiency_course_cpu --constraint=hwperf
```

### Day 2 (energy_efficiency_course_cpu and energy_efficiency_course_gpu)

```
salloc --gpus-per-node=1 -t 01:00:00 -p gpu --reservation=energy_efficiency_course_gpu 
```




## Previous Course Material
> Past course materials can be found on seperate branches on this repository.

- June 15-16 2023. [Material](https://github.com/sara-nl/energy-efficient-computing/tree/june_2023)
    - Topic Intro - Sagar Dolas (SURF)
    - System architecture - Prof. Ana Lucia Varbanescu (UTwente)
    - Characteristics of applications - Xavier Álvarez Farré (SURF)
    - Kernel Tuner - Alessio Sclocco and Stijn Heldens (Netherlands eScience Center)
