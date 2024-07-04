# MIT License

# Copyright (c) 2024 Gabriele Esposito

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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