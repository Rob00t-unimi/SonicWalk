# SonicWalk
## Introduction    

SonicWalk is an innovative healthcare application designed to simplify and engage patients during rehabilitative exercises using real-time sonification. For more Medical informations [click here](https://clinicaltrials.gov/study/NCT04876339?term=alfredo%20raglio&rank=1). Developed in **Python** and **PyQT5** to ensure cross-platform compatibility, the application allows medical staff to manage patient records, monitor exercise sessions, and visualize results. It utilizes **Movella MTw Awinda** motion trackers and their respective APIs to gather necessary data.

### Features
- **Real-time Sonification**: SonicWalk employs sonification techniques to provide auditory feedback during rehabilitative exercises, enhancing patient engagement, motivation, and ultimately, improving results.

- **Cross-Platform Compatibility**: Built with Python and PyQT5, SonicWalk ensures compatibility across different operating systems (*Windows*, *Linux*), maximizing accessibility and usability.

- **Patient Management**: Medical personnel can easily manage patients' information and exercise records through SonicWalk's intuitive interface, streamlining administrative tasks and optimizing patient care.

- **Exercise Monitoring**: The application facilitates real-time monitoring of exercise sessions by healthcare providers, empowering proactive intervention and personalized guidance for patients throughout their rehabilitation journey.

<!-- - **Data Visualization**: SonicWalk visualizes exercise data, enabling medical staff to analyze trends, identify areas for improvement, and personalize treatment plans. -->

### About the Project
SonicWalk originated as part of a final internship project for a bachelor's degree in computer science. The project involved the implementation of real-time signal analysis and processing methods to detect points of interest during exercises, as well as the complete development of the graphical user interface and data management logic.

### Contributions
Roberto Tallarini's Contribution:
- Expanded the original Gabriele's interface to include additional rehabilitative exercises, such as high-knee marching, backward step marching, swing, and double step.
- Implemented real-time signals analysis methods for each exercise, including automatic leg detection and audio feedback using the Pygame library (which provides stability and is less susceptible to interference from threads or drivers compared to Simpleaudio).
- Implemented a bpm estimator to calculate the medium bpm of the patient.
- Ideated, Designed and developed a comprehensive graphical user interface for managing patients informations, records, exercise sessions, and music libraries.
- Conducted the porting of the original code to Windows and integrated it with the graphical user interface.
- Envisioned, designed, and implemented the entire user interface and data management system.
- https://github.com/Rob00t-unimi/SonicWalk

Gabriele Esposito's Contribution:
- Developed a Python interface based on the Xsens Device API to communicate with MTw Awinda motion trackers.
- Implemented data recording and real-time plotting of motion tracking data.
- Created a gyroscope-based step detector capable of detecting steps during various walking speeds.
- Integrated sound reproduction for signaling step occurrences using simpleaudio library.
- Assisted in the porting process to ensure cross-platform compatibility.
- https://github.com/xyzxyzxyzxy/SonicWalk


### A simple python interface based on the Xsens Device API to communicate with MTw Awinda motion trackers. 

Data from MTw motion trackers can be recorded and returned as a Numpy.array (pitch angle).
Additionally data can be plotted in real-time in a separate process as it is received from the devices.
A step detector can be spawn to detect steps while walking. Steps are detected and counted separately for each sensor (leg).

The interface is created specifically to work with two MTw Awinda sensors that need to be both detected before starting the recording. 
Sensors produce motion tracking data in the form of Euler angles, for the specific application of step detection pitch angle only is recorded and processed.

The gyroscope based step detector is capable to detect steps during very slow walk, and can work with a great range of speeds.
To signal the occurence of a step a sound can be reproduced from a sample library. The sample library can be specified as a path to a directory containing .WAV or .mp3 samples, such samples will be reproduced sequentially in lexicographic order. 
This gives the possibility to partition a music track into samples that will be reproduced back to back while the subject wearing the sensors is walking, at the speed the subject is walking at.

A usage example can be found in the examples directory

```python

duration = 90
samplesPath = "../sonicwalk/audio_samples/cammino_1_fase_2"

with mtw.MtwAwinda(120, 19, samplesPath) as mtw:
        data = mtw.mtwRecord(duration, plot=True, analyze=True, exType=0, sensitivityLev=3, auto_detectLegs=False , selectedLeg=True, calculateBpm=False, shared_data=None, setStart=None, sound=True)

data0 = data[0][0]
data1 = data[0][1]
index0 = data[1][0]
index1 = data[1][1]

interestingPoints0 = data[2][0]
interestingPoints1 = data[2][1]

bpmValue = data[3]  # if calculateBpm==False will be None

```
- **exType** indicates the exercise to run:

    0) Walking
    1)  Walking in place (High Knees marching, backward step marching)
    2) Walking in place (High Knees with sensors on the thighs)
    3) Swing
    4) Double step

- **setStart** is a callback function to call when the exercise starts
- **CalculateBpm** is a boolean indicating if the bpm must be extimated during the execution of the exercise
- **shared_data** is an optional pre-allocated SharedData object
- **sensitivityLev** is a number between 1 and 5 indicating the level of sensitivity (inversely proportional to accuracy), default: 3
- **selectedLeg** is a boolean indicating the manual selected leg (true if right leg forward, false if left leg forward. Defaults to None.)
- **auto_detectLegs** is a boolean indicating if the legs must be automatically detected or not
- **sound** is a boolean indicating if the real time sound must be played during the exercise



A **MtwAwinda** singleton object instance must be created in a **with** statement,
this ensures proper setup of the sensors and closing. 
When creating the object instance a *sample rate* and a *radio channel* must be specified together with a *path to the library of samples*. 
For the available sample rates and radio channels consult the Xsense Device API documentation or the MTw Awinda motion trackers documentation.
After the creation of the object the sensors and master devices are put in *Measurement mode* and recording can be started.
To start recording the public method **mtwRecord** can be called, specifying a duration value that must be a positive integer indicating the number of seconds the recording should last.
Two additional flags can be provided:
- plot: spawns a daemon that handles real time plotting (using matplotlib).
- analyze: spawns two daemons (one for each sensor) handling step detection and samples reproduction from the library of samples provided.

The Recorded data returned by the `mtwRecord` function includes several components:

- `data[0][0]` and `data[0][1]` are tuples of Numpy.arrays containing the pitch angle buffers for the two signals, respectively. The two buffers of length 72000 samples can contain roughly 10 minutes of recording (at 120Hz) after witch the buffers are overwritten.
- `data[1][0]` and `data[1][1]` represent the indices at which the recording stopped for the two signals.
- The 'interesting points' related to the two signals are stored in `data[2][0]` and `data[2][1]`, which are tuples of Numpy.arrays. These arrays contain the approximate indices of the two signals at which points of interest were detected.
- `data[3]` contains the average beats per minute (bpm) value if the calculation was requested and the relevant data was acquired. Otherwise, it will be `False`.

# Installation
## Simplified Installation (Executable Package)
Only for windows:

Go to [dist folder](https://github.com/Rob00t-unimi/SonicWalk/tree/master/dist), download and run SonicWalk_app-installer.exe

If you do not find the file SonicWalk_app-installer.exe in the dist folder, you can download it from this link: [SonicWalk_app-installer.exe](https://drive.google.com/file/d/1G9776gC1ApdkP-RRJCeb2Vk0KTFDaHDu/view?usp=sharing)

## Detailed Installation (Python Environment Setup)
### Requires and dependencies installation
Python version 3.9 is required, (it is recommended to create a conda virtual environment using the python version 3.9)\
Installing the *xsensdeviceapi* dependency:

Windows:

```
pip install xsense_wheels/xsensdeviceapi-2022.2.0-cp39-none-win_amd64.whl
```
Linux:
```
pip install xsense_wheels/xsensdeviceapi-2022.0.0-cp39-none-linux_x86_64.whl
```
#### Installation of the simple Python interface Dependencies
- matplotlib
- pygame
- scipy

    Installing the sonicwalk package:
    ```
    pip install dist/sonicwalk-1.0.0.dev1-py3-none-any.whl
    ```
    ```
    pip install matplotlib pygame scipy
    ```
    ```python
    from sonicwalk import mtw

    ```
#### Installation of GUI application Dependencies
- matplotlib
- pygame
- scipy
- PyQt5
- qt_material

    ```
    pip install PyQt5 matplotlib pygame qt_material scipy
    ```

#### Run the GUI by Shell
Install the Complete GUI application Dependencies, then run:
```
python SonicWalk.py
```
