
#  Copyright (c) 2003-2022 Xsens Technologies B.V. or subsidiaries worldwide.
#  All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without modification,
#  are permitted provided that the following conditions are met:
#  
#  1.	Redistributions of source code must retain the above copyright notice,
#  	this list of conditions, and the following disclaimer.
#  
#  2.	Redistributions in binary form must reproduce the above copyright notice,
#  	this list of conditions, and the following disclaimer in the documentation
#  	and/or other materials provided with the distribution.
#  
#  3.	Neither the names of the copyright holders nor the names of their contributors
#  	may be used to endorse or promote products derived from this software without
#  	specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
#  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
#  THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
#  OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY OR
#  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.THE LAWS OF THE NETHERLANDS 
#  SHALL BE EXCLUSIVELY APPLICABLE AND ANY DISPUTES SHALL BE FINALLY SETTLED UNDER THE RULES 
#  OF ARBITRATION OF THE INTERNATIONAL CHAMBER OF COMMERCE IN THE HAGUE BY ONE OR MORE 
#  ARBITRATORS APPOINTED IN ACCORDANCE WITH SAID RULES.
#  

import sys
import time
import os
import gc
import xsensdeviceapi as xda
import multiprocessing as mp
import numpy as np
import simpleaudio as sa
from multiprocessing.sharedctypes import RawValue, RawArray
from sharedCircularIndex import SharedCircularIndex
from getch import getch
from plotter import Plotter
from analyzer import Analyzer
from threading import Lock

class MtwCallback(xda.XsCallback):
    def __init__(self, m_mtwIndex, device, max_buffer_size = 300):
        xda.XsCallback.__init__(self)
        self.m_mtwIndex = m_mtwIndex
        self.m_device = device
        self.m_maxNumberOfPacketsInBuffer = max_buffer_size
        self.m_packetBuffer = list()
        self.m_lock = Lock()

    def getMtwIndex(self):
        return self.m_mtwIndex

    def device(self):
        assert(self.m_device != 0)
        return self.m_device

    def dataAvailable(self):
        self.m_lock.acquire()
        if self.m_packetBuffer:
            res = True
        else:
            res = False
        self.m_lock.release()
        return res

    def getOldestPacket(self):
        self.m_lock.acquire()
        assert(len(self.m_packetBuffer) > 0)
        oldest_packet = xda.XsDataPacket(self.m_packetBuffer.pop(0))
        self.m_lock.release()
        return oldest_packet

    def onLiveDataAvailable(self, dev, packet):
        self.m_lock.acquire()
        assert(packet != 0)
        while len(self.m_packetBuffer) >= self.m_maxNumberOfPacketsInBuffer:
            self.m_packetBuffer.pop() #queue is full get rid of last element 
        self.m_packetBuffer.append(xda.XsDataPacket(packet))
        self.m_lock.release()

class WirelessMasterCallback(xda.XsCallback):
    def __init__(self):
        xda.XsCallback.__init__(self)
        self.m_lock = Lock()
        self.m_connectedMTWs = set()

    def getWirelessMTWs(self):
        self.m_lock.acquire()
        mtw = self.m_connectedMTWs
        self.m_lock.release()
        return mtw
    
    def onConnectivityChanged(self, dev, newState):
        self.m_lock.acquire()
        dev = dev.deviceId().toXsString()
        if newState == xda.XCS_Disconnected:
            print("EVENT: MTW DISCONNECTED -> %s" % (dev))
            self.m_connectedMTWs.remove(dev)
        elif newState == xda.XCS_Rejected:
            print("EVENT: MTW REJECTED -> %s" % (dev))
            self.m_connectedMTWs.remove(dev)
        elif newState == xda.XCS_PluggedIn:
            print("EVENT: MTW PLUGGED IN -> %s" % (dev))
            self.m_connectedMTWs.remove(dev)
        elif newState == xda.XCS_Wireless:
            print("EVENT: MTW CONNECTED -> %s" % (dev))
            self.m_connectedMTWs.add(dev)
        elif newState == xda.XCS_File:
            print("EVENT: MTW FILE -> %s" % (dev))
            self.m_connectedMTWs.remove(dev)
        elif newState == xda.XCS_Unknown:
            print("EVENT: MTW UNKNOWN -> %s" % (dev))
            self.m_connectedMTWs.remove(dev)
        else:
            print("EVENT: MTW ERROR -> %s" % (dev))
            self.m_connectedMTWs.remove(dev)
        self.m_lock.release()

class MtwAwinda(object):
    """Class that allows mtwAwinda devices handling
    
    must be used in a with block to properly initialize and close devices
    desiredUpdaterate and desiredRadioChannel are mandatory arguments to the constructor
    (see device documentation for a list of supported update rates and radio channels)
    """
    def __new__(cls, desiredUpdateRate, desiredRadioChannel, samplesPath):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MtwAwinda, cls).__new__(cls)
        return cls.instance
    
    def __init__(self, desiredUpdateRate:int, desiredRadioChannel:int, samplesPath:str = ""):
        self.__updateRate = desiredUpdateRate
        self.__radioChannel = desiredRadioChannel
        self.__samplesPath = samplesPath
        self.__maxNumberofCoords = 72000 #equivalent to 10 minutes at 120Hz
        self.__eulerData = np.zeros((2, self.__maxNumberofCoords), dtype=np.float64) #we have only two Mtw devices
        self.__index = np.zeros(2, dtype=np.uint32)

    def __enter__(self):
        print("Creating XsControl object...")
        self.control = xda.XsControl_construct()
        assert(self.control != 0)
        self.xdaVersion = xda.XsVersion()
        xda.xdaVersion(self.xdaVersion)
        print("Using XDA version %s" % self.xdaVersion.toXsString())
        try:
            print("Scanning for wireless Master...")
            portInfoArray =  xda.XsScanner_scanPorts()

            # Find an MTi device
            self.mtPort = xda.XsPortInfo()
            for i in range(portInfoArray.size()):
                if portInfoArray[i].deviceId().isWirelessMaster():
                    self.mtPort = portInfoArray[i]
                    break

            if self.mtPort.empty():
                raise RuntimeError("No wireless Master found. Aborting.")

            self.did = self.mtPort.deviceId()
            print("Found wireless master :")
            print(" Device ID: %s" % self.did.toXsString())
            print(" Port name: %s" % self.mtPort.portName())

            #OPEN DEVICE OF INTEREST
            print("Opening port...")
            if not self.control.openPort(self.mtPort.portName(), self.mtPort.baudrate()):
                raise RuntimeError("Could not open port. Aborting.")

            #GET XSDEVICE INSTANCE WITH XSCONTROL::DEVICE()
            # Get the device object
            self.masterDevice = self.control.device(self.did) 
            assert(self.masterDevice != 0)
            print("XsDevice instance created")
            print("Device: %s, with ID: %s opened." % (self.masterDevice.productCode(), self.masterDevice.deviceId().toXsString()))

            # Put the device into configuration mode before configuring the device
            print("Putting device into configuration mode...")
            if not self.masterDevice.gotoConfig(): 
                raise RuntimeError("Could not put device into configuration mode. Aborting.")

            # Create and attach callback handler to device
            self.masterCallback = WirelessMasterCallback() #create callback
            self.masterDevice.addCallbackHandler(self.masterCallback) #attach callback function to device

            #CONFIGURE DEVICE (AWINDA MASTER)
            print("Getting the list of the supported uptate rates")
            rates = self.masterDevice.supportedUpdateRates()
            for rate in rates:
                print("%d " % (rate))

            print("Setting update rate to %d Hz..." % self.__updateRate)
            if not self.masterDevice.setUpdateRate(self.__updateRate):
                raise RuntimeError("Could not set desired update rate. Aborting")
            
            print("Disabling radio channel if previously enabled...")
            if not self.masterDevice.isRadioEnabled():
                if not self.masterDevice.disableRadio():
                    raise RuntimeError("Failed to disable radio channel. Aborting")
            
            print("Setting radio channel to %d and enabling radio..." % self.__radioChannel)
            if not self.masterDevice.enableRadio(self.__radioChannel):
                raise RuntimeError("Failed to set radio channel. Aborting")
            
            print("Waiting for MTWs to wirelessly connect...")
            self.connectedMTWCount = len(self.masterCallback.getWirelessMTWs())
            while self.connectedMTWCount < 2:
                xda.msleep(100)
                while True:
                    nextCount = len(self.masterCallback.getWirelessMTWs())
                    if nextCount != self.connectedMTWCount:
                        print("Number of connected MTWs: %d" % nextCount)
                        self.connectedMTWCount = nextCount
                    else:
                        break
            
            print("Getting XsDevice instances for all MTWs...")
            allDeviceIds = self.control.deviceIds()
            mtwDeviceIds = list()
            for dev in allDeviceIds:
                if dev.isMtw():
                    mtwDeviceIds.append(dev)
            self.mtwDevices = list()
            for dev in mtwDeviceIds:
                mtwDevice = self.control.device(dev) #XsDevice object
                if mtwDevice != 0:
                    self.mtwDevices.append(mtwDevice)
                else:
                    raise RuntimeError("Failded to create an MTW XsDevice instance. Aborting")
                
            print("Attaching callback handlers to MTWs...")
            self.mtwCallbacks = list()
            for i in range(len(self.mtwDevices)):
                self.mtwCallbacks.append(MtwCallback(i, self.mtwDevices[i]))
                self.mtwDevices[i].addCallbackHandler(self.mtwCallbacks[i])
                print("Created callback %s and attached to device %s" % 
                      (self.mtwCallbacks[i].getMtwIndex(), self.mtwCallbacks[i].device().deviceId().toXsString()))
            
            #SWITCH DEVICE TO MEASUREMENT MODE
            print("Starting measurement...")
            if not self.masterDevice.gotoMeasurement():
                raise RuntimeError("Could not put device into measurement mode. Aborting.")


            return self

        except RuntimeError as error:
            print(error)
            sys.exit(1)
        except Exception as error:
            print(error)
            sys.exit(1)
        else:
            print("Successful init.")
    
    def __getEuler(self):
        """Get data from callback buffers, 
        
        returns a list of two bools one for each buffer
        the corresponding element is True if data was available, False otherwise
        
        Has to consume data faster than it is produced otherwise data is lost
        (buffersize is 300 packets for each device)
        """

        avail = [False, False]
        try:
    
            for i in range(2):
                if self.mtwCallbacks[i].dataAvailable():
                    avail[i] = True
                    # Retrieve a packet
                    packet = self.mtwCallbacks[i].getOldestPacket()
                    #packet always contains orientation NO NEED TO CHECK (Mtw Awinda)
                    euler = packet.orientationEuler()
                    self.__eulerData[i][self.__index[i]] = euler.y() #pitch only is written into the class buffer
                    self.__index[i] += 1 % self.__maxNumberofCoords

            return avail
    
        except RuntimeError as error:
            print(error)
            sys.exit(1)
        except Exception as error:
            print(error)
            sys.exit(1)

    def __cleanBuffer(self):
        self.__eulerData = np.zeros((2, self.__maxNumberofCoords), dtype=np.float64)
        self.__index = np.zeros(2, dtype=np.uint32)

    def __loadSamples(self):
        #check if sample list is empty before returning
        try:
            files = [os.path.join(self.__samplesPath, f) for f in os.listdir(self.__samplesPath) 
                    if os.path.isfile(os.path.join(self.__samplesPath, f))]
            files.sort() #sort filenames in order
            samples = []
            print("loading wave samples...")
            for f in files:
                if f.lower().endswith(".wav"):
                    samples.append(sa.WaveObject.from_wave_file(f))
        except:
            print("samples could not be loaded...Aborting. Check pathname syntax")
            sys.exit(1)
        else:
            print("...wave samples loaded successfully")

        if not samples:
            print("No wav file was found at given pathname...Aborting. Check file extensions")
            sys.exit(1)
    
        return samples 

    def __resetOrientation(self):
        try:
            #RESET ORIENTATION
            print("Scheduling Orientation reset...")
            for i in range(len(self.mtwDevices)):
                self.mtwDevices[i].resetOrientation(xda.XRM_Inclination)
        except RuntimeError as error:
            print(error)
            sys.exit(1)
        except Exception as error:
            print(error)
            sys.exit(1)
        else:
            print("...Orientation reset successfully scheduled")


    def mtwRecord(self, duration:float, plot:bool=False, analyze:bool=True):
        """Record pitch data for duration seconds
        
        Returns a numpy.array object containing the data for each device and the relative index
        Additional flags can be supplied:

        if plot=True it spawns a daemon that handles plotting
        if analyze=True (default) it spawns a daemon that performs step counting
        """
        
        if not isinstance(duration, int) or duration < 10:
            raise ValueError("duration must be a positive integer (> 10) indicating the number of seconds")
        
        def write_shared(data0, data1, index0, index1, coords, terminate=False):
            #write coordinates to shared memory
            if terminate:
                data0[index0.value] = 1000
                data1[index1.value] = 1000
            else:
                #coords contains pitch for both dx and sx sensors
                if coords[0] != 0:
                    data0[index0.value] = coords[0]
                    index0.value = (index0.value + 1) % 1000
                if coords[1] != 0:
                    data1[index1.value] = coords[1]
                    index1.value = (index1.value + 1) % 1000

        self.__cleanBuffer()

        if any((plot, analyze)):
            #Declare and initialize unsynchronized shared memory (not lock protected)
            index0 = RawValue('i', 0)
            index1 = RawValue('i', 0)
            data0 = RawArray('d', 1000)
            data1 = RawArray('d', 1000)

            if plot:
                plotter = Plotter()
                plotter_process = mp.Process(target=plotter, args=(data0, data1, index0, index1), daemon=True)
                plotter_process.start()
                
            if analyze:
                #samples are loaded only if analyzer is has to spawn
                samples = self.__loadSamples()
                sharedIndex = SharedCircularIndex(len(samples))
                analyzer0 = Analyzer()
                analyzer1 = Analyzer()
                analyzer_process0 = mp.Process(target=analyzer0, args=(data0, index0, 0, sharedIndex, samples), daemon=True)
                analyzer_process1 = mp.Process(target=analyzer1, args=(data1, index1, 1, sharedIndex, samples), daemon=True)
                analyzer_process0.start()
                analyzer_process1.start()
                #delete local version of samples 
                del samples
                gc.collect()
            
            time.sleep(1) #wait one second before starting orientation reset and to allow processes to properly start
            self.__resetOrientation()

            print("Recording started...")
            startTime = xda.XsTimeStamp_nowMs()
            while xda.XsTimeStamp_nowMs() - startTime <= 1000*duration:
                
                avail = self.__getEuler()
                if any(avail):
                    coords = [self.__eulerData[0][self.__index[0]-1], self.__eulerData[1][self.__index[1]-1]]
                    coords = [a*b for a,b in zip(coords,avail)] #send only new data
                    write_shared(data0, data1, index0, index1, coords)
                #allow other processes to run
                #sleep 3ms (a new packet is received roughly every 8.33ms)
                xda.msleep(3)

            write_shared(data0, data1, index0, index1, None, terminate=True)
            
            if plot:
                plotter_process.join()
                
            if analyze:
                analyzer_process0.join()
                analyzer_process1.join()
                #result of step counting is written into shared memory
                print("Total number of steps: {:d}".format(int(data0[index0.value-1]) + int(data1[index1.value-1])))

        else:
            #record the data and return it without analisys
            startTime = xda.XsTimeStamp_nowMs()
            while xda.XsTimeStamp_nowMs() - startTime <= 1000*duration:
                _ = self.__getEuler() #fills object buffer with data from Mtw devices
        return (self.__eulerData, self.__index)
    
    def __clean(self):
        try:
            print("Setting config mode..")
            if not self.masterDevice.gotoConfig():
                raise RuntimeError("Failed to go to Config mode. Aborting.")
            
            print("Disabling Radio...") #should check if radio is enabled
            if not self.masterDevice.disableRadio():
                raise RuntimeError("Failed to disable radio. Aborting.")

            print("Removing callback handler...")
            self.masterDevice.removeCallbackHandler(self.masterCallback)

            print("Closing port...")
            self.control.closePort(self.mtPort.portName())

            print("Closing XsControl...")
            self.control.close()

        except RuntimeError as error:
            print(error)
            sys.exit(1)
        except Exception as error:
            print(error)
            sys.exit(1)
        else:
            print("Successful clean")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__clean()
             
if __name__ == '__main__':

    desiredUpdateRate = 120
    desiredRadioChannel = 19

    #CREATE XSCONTROL OBJECT
    print("Creating XsControl object...")
    control = xda.XsControl_construct()
    assert(control != 0)

    xdaVersion = xda.XsVersion()
    xda.xdaVersion(xdaVersion)
    print("Using XDA version %s" % xdaVersion.toXsString())

    #DISCOVER DEVICES
    try:
        print("Scanning for wireless Master...")
        portInfoArray =  xda.XsScanner_scanPorts()

        # Find an MTi device
        mtPort = xda.XsPortInfo()
        for i in range(portInfoArray.size()):
            if portInfoArray[i].deviceId().isWirelessMaster():
                mtPort = portInfoArray[i]
                break

        if mtPort.empty():
            raise RuntimeError("No wireless Master found. Aborting.")

        did = mtPort.deviceId()
        print("Found wireless master :")
        print(" Device ID: %s" % did.toXsString())
        print(" Port name: %s" % mtPort.portName())

        #OPEN DEVICE OF INTEREST
        print("Opening port...")
        if not control.openPort(mtPort.portName(), mtPort.baudrate()):
            raise RuntimeError("Could not open port. Aborting.")

        #GET XSDEVICE INSTANCE WITH XSCONTROL::DEVICE()
        # Get the device object
        masterDevice = control.device(did) 
        assert(masterDevice != 0)
        print("XsDevice instance created")
        print("Device: %s, with ID: %s opened." % (masterDevice.productCode(), masterDevice.deviceId().toXsString()))

        # Put the device into configuration mode before configuring the device
        print("Putting device into configuration mode...")
        if not masterDevice.gotoConfig(): 
            raise RuntimeError("Could not put device into configuration mode. Aborting.")

        # Create and attach callback handler to device
        masterCallback = WirelessMasterCallback() #create callback
        masterDevice.addCallbackHandler(masterCallback) #attach callback function to device

        #CONFIGURE DEVICE (AWINDA MASTER)
        print("Getting the list of the supported uptate rates")
        rates = masterDevice.supportedUpdateRates()
        for rate in rates:
            print("%d " % (rate))
        
        #ASSIGN NEW UPDATE RATE
        newUpdateRate = desiredUpdateRate

        print("Setting update rate to %d Hz..." % newUpdateRate)
        if not masterDevice.setUpdateRate(newUpdateRate):
            raise RuntimeError("Could not set desired update rate. Aborting")
        
        print("Disabling radio channel if previously enabled...")
        if not masterDevice.isRadioEnabled():
            if not masterDevice.disableRadio():
                raise RuntimeError("Failed to disable radio channel. Aborting")
        
        print("Setting radio channel to %d and enabling radio..." % desiredRadioChannel)
        if not masterDevice.enableRadio(desiredRadioChannel):
            raise RuntimeError("Failed to set radio channel. Aborting")
        
        print("Waiting for MTWs to wirelessly connect...")
        connectedMTWCount = len(masterCallback.getWirelessMTWs())
        while connectedMTWCount < 2:
            xda.msleep(100)
            while True:
                nextCount = len(masterCallback.getWirelessMTWs())
                if nextCount != connectedMTWCount:
                    print("Number of connected MTWs: %d" % nextCount)
                    connectedMTWCount = nextCount
                else:
                    break
                
        #BLOCKING GETCH
        print("Press Y to start measurement")
        c = getch()
        if str(c).upper() != "Y":
            print("Aborting")
            sys.exit(1)

        #SWITCH DEVICE TO MEASUREMENT MODE
        print("Starting measurement...")
        if not masterDevice.gotoMeasurement():
            raise RuntimeError("Could not put device into measurement mode. Aborting.")

        print("Getting XsDevice instances for all MTWs...")
        allDeviceIds = control.deviceIds()
        mtwDeviceIds = list()
        for dev in allDeviceIds:
            if dev.isMtw():
                mtwDeviceIds.append(dev)
        mtwDevices = list()
        for dev in mtwDeviceIds:
            mtwDevice = control.device(dev) #XsDevice object
            if mtwDevice != 0:
                mtwDevices.append(mtwDevice)
            else:
                raise RuntimeError("Failded to create an MTW XsDevice instance. Aborting")
            
        print("Attaching callback handlers to MTWs...")
        
        mtwCallbacks = list()
        for i in range(len(mtwDevices)):
            mtwCallbacks.append(MtwCallback(i, mtwDevices[i]))
            mtwDevices[i].addCallbackHandler(mtwCallbacks[i])
            print("Created callback %s and attached to device %s" % (mtwCallbacks[i].getMtwIndex(), mtwCallbacks[i].device()))

        print("Main loop. Recording data for 10 seconds.")

        startTime = xda.XsTimeStamp_nowMs()
        counter = 0

        eulerData = [list(), list()]

        while xda.XsTimeStamp_nowMs() - startTime <= 20000:
            for i in range(len(mtwCallbacks)):
                if mtwCallbacks[i].dataAvailable():
                    # Retrieve a packet
                    packet = mtwCallbacks[i].getOldestPacket()

                    s = ""

                    # if packet.containsCalibratedData():
                    #     acc = packet.calibratedAcceleration()
                    #     s = "Acc X: %.2f" % acc[0] + ", Acc Y: %.2f" % acc[1] + ", Acc Z: %.2f" % acc[2]

                    #     gyr = packet.calibratedGyroscopeData()
                    #     s += " |Gyr X: %.2f" % gyr[0] + ", Gyr Y: %.2f" % gyr[1] + ", Gyr Z: %.2f" % gyr[2]

                    #     mag = packet.calibratedMagneticField()
                    #     s += " |Mag X: %.2f" % mag[0] + ", Mag Y: %.2f" % mag[1] + ", Mag Z: %.2f" % mag[2]

                    if packet.containsOrientation():
                        # quaternion = packet.orientationQuaternion()
                        # s = "q0: %.2f" % quaternion[0] + ", q1: %.2f" % quaternion[1] + ", q2: %.2f" % quaternion[2] + ", q3: %.2f " % quaternion[3]
                        
                        euler = packet.orientationEuler()
                        eulerData[i].append(euler)
                        mtwId = packet.deviceId()
                        s += " |Roll: {:+.2f} ".format(euler.x()) + ", Pitch: {:+.2f} ".format(euler.y()) + ", Yaw: {:+.2f} ".format(euler.z()) + ", DeviceId: {}".format(mtwId)

                    # if packet.containsLatitudeLongitude():
                    #     latlon = packet.latitudeLongitude()
                    #     s += " |Lat: %7.2f" % latlon[0] + ", Lon: %7.2f " % latlon[1]

                    # if packet.containsAltitude():
                    #     s += " |Alt: %7.2f " % packet.altitude()

                    # if packet.containsVelocity():
                    #     vel = packet.velocity(xda.XDI_CoordSysEnu)
                    #     s += " |E: %7.2f" % vel[0] + ", N: %7.2f" % vel[1] + ", U: %7.2f " % vel[2]
                    if counter % 25 == 0:
                        print("%s\r" % s, flush=True)
                    counter = counter + 1

        print("\nSetting config mode..")
        if not masterDevice.gotoConfig():
            raise RuntimeError("Failed to go to Config mode. Aborting.")
        
        print("Disabling Radio...")
        if not masterDevice.disableRadio():
            raise RuntimeError("Failed to disable radio. Aborting.")

        print("Removing callback handler...")
        masterDevice.removeCallbackHandler(masterCallback)

        print("Closing port...")
        control.closePort(mtPort.portName())

        print("Closing XsControl...")
        control.close()

    except RuntimeError as error:
        print(error)
        sys.exit(1)
    except Exception as error:
        print(error)
        sys.exit(1)
    else:
        print("Successful exit.")
