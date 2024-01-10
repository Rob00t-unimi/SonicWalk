import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.style as mplstyle
import numpy as np

class Plotter():
    def __terminate(self):
        #BUG: on window closing matplotlib animation complains with an attribute error
        print('plotter daemon terminated...')
        self.__ani.event_source.stop()
        plt.close(self.__fig)
    
    def __animate(self, i):
        if self.__data0[self.__index0.value] == 1000:
            self.__terminate()
            return

        pitch0 = np.array(self.__data0)
        pitch1 = np.array(self.__data1)

        self.__ax.clear()
        l0, = self.__ax.plot(self.__data0, 'b')
        l1, = self.__ax.plot(self.__data1, 'c')
        return l0, l1
    
    def __call__(self, data0, data1, index0, index1):
        print('starting plotter daemon..')
        mplstyle.use('fast')
        self.__data0 = data0
        self.__data1 = data1
        self.__index0 = index0 
        self.__index1 = index1
        self.__fig, self.__ax = plt.subplots()
        self.__ani = animation.FuncAnimation(self.__fig, self.__animate, interval=50, cache_frame_data=False, blit=True, repeat=False)
        print('...plotter daemon started')
        plt.show()