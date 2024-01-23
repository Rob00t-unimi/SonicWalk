# SonicWalk

### A simple python interface based on the Xsens Device API to communicate with MTw Awinda motion trackers. 

Data from MTw motion trackers can be recorded and returned as a Numpy.array (pitch angle).
Additionally data can be plotted in real-time in a separate process as it is received from the devices.
A step detector can be spawn to detect steps while walking. Steps are detected and counted separately for each sensor (leg).

The interface is created specifically to work with two MTw Awinda sensors that need to be both detected before starting the recording. 
Sensors produce motion tracking data in the form of Euler angles, for the specific application of step detection pitch angle only is recorded and processed.

The gyroscope based step detector is capable to detect steps during very slow walk, and can work with a great range of speeds.
To signal the occurence of a step a sound can be reproduced from a sample library. The sample library can be specified as a path to a directory containing .WAV samples, such samples will be reproduced sequentially in lexicographic order. 
This gives the possibility to partition a music track into samples that will be reproduced back to back while the subject wearing the sensors is walking, at the speed the subject is walking at.

A usage example can be found in the examples directory

```python
duration = 60
samplesPath = "../sonicwalk/audio_samples/cammino_1_fase_2"

with mtw.MtwAwinda(120, 19, samplesPath) as mtw:
    data = mtw.mtwRecord(duration, plot=True, analyze=True)

data0 = data[0][0]
data1 = data[0][1]
index0 = data[1][0]
index1 = data[1][1]

```

A **MtwAwinda** singleton object instance must be created in a **with** statement,
this ensures proper setup of the sensors and closing. 
When creating the object instance a *sample rate* and a *radio channel* must be specified together with a *path to the library of samples*. 
For the available sample rates and radio channels consult the Xsense Device API documentation or the MTw Awinda motion trackers documentation.
After the creation of the object the sensors and master devices are put in *Measurement mode* and recording can be started.
To start recording the public method **mtwRecord** can be called, specifying a duration value that must be a positive integer indicating the number of seconds the recording should last.
Two additional flags can be provided:
- plot: spawns a daemon that handles real time plotting (using matplotlib).
- analyze: spawns two daemons (one for each sensor) handling step detection and samples reproduction from the library of samples provided.

Recorded data is returned by the function as a tuple of Numpy.arrays. 
With the first element consisting of two buffers of pitch angles of a maximum lenght of 72000 samples, and the second being the index at witch the recording has stopped.
The two buffers of length 72000 samples can contain roughly 10 minutes of recording (at 120Hz) after witch the buffers are overwritten.

### Installation
Python version 3.9 is required, (it is recommended to create a conda virtual environment using the python version 3.9)\
Installing the *xsensdeviceapi* dependency:

```
pip install wheels/xsensdeviceapi-2022.0.0-cp39-none-linux_x86_64.whl
```
Installing the package:
```
pip install dist/sonicwalk-1.0.0.dev1-py3-none-any.whl
```

### Usage
You can find a usage example in the examples directory
```python
from sonicwalk import mtw

```