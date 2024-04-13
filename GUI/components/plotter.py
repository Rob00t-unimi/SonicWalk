import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter 
import numpy as np

from multiprocessing import Process, Queue
import time

class PlotProcess(Process):
    def __init__(self, data0, data1, index0, index1, queue):
        super().__init__()
        self.__data0 = data0
        self.__data1 = data1
        self.__index0 = index0
        self.__index1 = index1
        self.queue = queue

    def run(self):
        while self.__data0[self.__index0.value] != 1000:
            data0_copy = self.__data0[:]
            data1_copy = self.__data1[:]
            self.queue.put((data0_copy, data1_copy))
            time.sleep(0.05)

class Plotter(QWidget):
    def __init__(self, data0, data1, index0, index1):
        super().__init__()
        self.__data0 = data0
        self.__data1 = data1
        self.__index0 = index0
        self.__index1 = index1

        self.queue = Queue()
        self.plot_process = PlotProcess(data0, data1, index0, index1, self.queue)

        self._initialize_plotter()

    def _initialize_plotter(self):
        # Create a chart
        self.chart = QChart()
        self.chart.setTitle("Data Plot")

        # Create series
        self.series0 = QLineSeries()
        self.series1 = QLineSeries()

        # Add series to the chart
        self.chart.addSeries(self.series0)
        self.chart.addSeries(self.series1)

        # Create axes
        self.axisX = QValueAxis()
        self.axisY = QValueAxis()
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.chart.addAxis(self.axisY, Qt.AlignLeft)

        # Attach axes to series
        self.series0.attachAxis(self.axisX)
        self.series0.attachAxis(self.axisY)
        self.series1.attachAxis(self.axisX)
        self.series1.attachAxis(self.axisY)

        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.chart_view)
        self.setLayout(layout)

    def start_stream(self):
        self.plot_process.start()
        self.update_plot()

    def update_plot(self):
        while not self.queue.empty():
            data0, data1 = self.queue.get()
            self._update_plot(data0, data1)

        QTimer.singleShot(50, self.update_plot)

    def _update_plot(self, data0, data1):
        # Clear previous data
        self.series0.clear()
        self.series1.clear()

        # Plot data0
        for i, val in enumerate(data0):
            self.series0.append(i, val)

        # Plot data1
        for i, val in enumerate(data1):
            self.series1.append(i, val)

    def _terminate_stream(self):
        # Stop the process
        self.plot_process.terminate()
        self.plot_process.join()

        # Clear data
        self.series0.clear()
        self.series1.clear()