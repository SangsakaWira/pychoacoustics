# -*- coding: utf-8 -*- 
#   Copyright (C) 2010-2015 Samuele Carcagno <sam.carcagno@gmail.com>
#   This file is part of pychoacoustics

#    pychoacoustics is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    pychoacoustics is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with pychoacoustics.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, unicode_literals
import matplotlib

from .pyqtver import*
if pyqtversion == 4:
    from PyQt4 import QtGui, QtCore
    from PyQt4.QtGui import QCheckBox, QHBoxLayout, QMainWindow, QVBoxLayout, QWidget
    # import the Qt4Agg FigureCanvas object, that binds Figure to
    # Qt4Agg backend. It also inherits from QWidget
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    # import the NavigationToolbar Qt4Agg widget
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
    matplotlib.rcParams['backend'] = "Qt4Agg"
    matplotlib.rcParams['backend.qt4'] = "PyQt4"
elif pyqtversion == -4:
    from PySide import QtGui, QtCore
    from PySide.QtGui import QCheckBox, QHBoxLayout, QMainWindow, QVBoxLayout, QWidget
    # import the Qt4Agg FigureCanvas object, that binds Figure to
    # Qt4Agg backend. It also inherits from QWidget
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    # import the NavigationToolbar Qt4Agg widget
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
    matplotlib.rcParams['backend'] = "Qt4Agg"
    matplotlib.rcParams['backend.qt4'] = "PySide"
elif pyqtversion == 5:
    from PyQt5 import QtGui, QtCore
    from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QMainWindow, QVBoxLayout, QWidget
    # import the Qt4Agg FigureCanvas object, that binds Figure to
    # Qt4Agg backend. It also inherits from QWidget
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    # import the NavigationToolbar Qt4Agg widget
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    matplotlib.rcParams['backend'] = "Qt5Agg"
# Matplotlib Figure object
from matplotlib.figure import Figure

from matplotlib.widgets import Cursor
import numpy as np
import copy, os
from numpy import arange, ceil, floor, linspace, log10
from matplotlib.lines import Line2D

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import matplotlib.font_manager as fm

from .pysdt import*

#mpl.rcParams['font.family'] = 'sans-serif'

#fontPath = os.path.abspath(os.path.dirname(__file__)+'/../') + '/data/Ubuntu-R.ttf'
#fontPath = '/media/ntfsShared/lin_home/auditory/code/pychoacoustics/pychoacoustics-qt4/development/dev/data/Ubuntu-R.ttf'
#prop = fm.FontProperties(fname=fontPath)
#mpl.rcParams.update({'font.size': 16})



def log_10_product(x, pos):
    """The two args are the value and tick position.
    Label ticks with the product of the exponentiation"""
    return '%1i' % (x)
def nextPow10Up(val):
    p = int(ceil(log10(val)))
    return p

def nextPow10Down(val):
    p = int(floor(log10(val)))
    return p

class psychListenerPlot(QMainWindow):
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.prm = prm
     
            
        self.pchs = ["o", "s", "v", "p", "h", "8", "*", "x", "+", "d", ",", "^", "<", ">", "1", "2", "3", "4", "H", "D", ".", "|", "_"]  


        mpl.rcParams['xtick.major.size'] = 6
        mpl.rcParams['xtick.minor.size'] = 4
        mpl.rcParams['xtick.major.width'] = 1
        mpl.rcParams['xtick.minor.width'] = 1
        mpl.rcParams['ytick.major.size'] = 9
        mpl.rcParams['ytick.minor.size'] = 5
        mpl.rcParams['ytick.major.width'] = 0.8
        mpl.rcParams['ytick.minor.width'] = 0.8
        mpl.rcParams['xtick.direction'] = 'out'
        mpl.rcParams['ytick.direction'] = 'out'
        mpl.rcParams['font.size'] = 14
        mpl.rcParams['figure.facecolor'] = 'white'
        mpl.rcParams['lines.color'] = 'black'
        mpl.rcParams['axes.color_cycle'] = ["#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]#['k', 'b', 'g', 'r', 'c', 'm', 'y']

        self.mw = QWidget(self)
        self.vbl = QVBoxLayout(self.mw)
        self.fig = Figure(figsize=(8,8))#facecolor=self.canvasColor, dpi=self.dpi)
        self.fig = Figure(figsize=(8,8))#facecolor=self.canvasColor, dpi=self.dpi)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.mw)
        self.ntb = NavigationToolbar(self.canvas, self.mw)
        self.gridOn = QCheckBox(self.tr("Grid"))
        self.gridOn.stateChanged[int].connect(self.toggleGrid)
        self.ntbBox = QHBoxLayout()
        self.ntbBox.addWidget(self.ntb)
        self.ntbBox.addWidget(self.gridOn)
        self.vbl.addWidget(self.canvas)
        self.vbl.addLayout(self.ntbBox)
        self.mw.setFocus()
        self.setCentralWidget(self.mw)

        self.getPsyFun()
        self.plotData()

        # if pdfPlot == True:
        #      self.fig.savefig(self.fName.split('.')[0] + '.pdf', format='pdf')
        # if winPlot == True:
        self.show()
        self.canvas.draw()
        #else:
        #    self.deleteLater()

    def getPsyFun(self):
        psyFun = self.parent().psyListFunChooser.currentText()
        psyFunFit = self.parent().psyListFunFitChooser.currentText()
        alphax = self.parent().currLocale.toDouble(self.parent().psyListMidpoint.text())[0]
        betax = self.parent().currLocale.toDouble(self.parent().psyListSlope.text())[0]
        lambdax = self.parent().currLocale.toDouble(self.parent().psyListLapse.text())[0]
        gammax = 1/self.parent().currLocale.toDouble(self.parent().nAlternativesChooser.currentText())[0]
        pcCorr = numpy.round(numpy.arange(numpy.round(gammax, 3), 1.001, 0.001), 3)
        self.pcCorr = pcCorr
        self.psyFunFit = psyFunFit
        if psyFun == "Logistic":
            if psyFunFit == "Linear":
                self.stim = invLogisticPsy(pcCorr, alphax, betax, gammax, lambdax)
            elif psyFunFit == "Logarithmic":
                self.stim = invLogisticPsy(pcCorr, log(alphax), betax, gammax, lambdax)
                self.stim = numpy.exp(self.stim)
        elif psyFun == "Gaussian":
            if psyFunFit == "Linear":
                self.stim = invGaussianPsy(pcCorr, alphax, betax, gammax, lambdax)
            elif psyFunFit == "Logarithmic":
                self.stim = invGaussianPsy(pcCorr, log(alphax), betax, gammax, lambdax)
                self.stim = numpy.exp(self.stim)
        elif psyFun == "Gumbel":
            if psyFunFit == "Linear":
                self.stim = invGumbelPsy(pcCorr, alphax, betax, gammax, lambdax)
            elif psyFunFit == "Logarithmic":
                self.stim = invGumbelPsy(pcCorr, log(alphax), betax, gammax, lambdax)
                self.stim = numpy.exp(self.stim)
        elif psyFun == "Weibull":
            if psyFunFit == "Linear":
                self.stim = invWeibullPsy(pcCorr, alphax, betax, gammax, lambdax)
            elif psyFunFit == "Logarithmic":
                self.stim = invWeibullPsy(pcCorr, log(alphax), betax, gammax, lambdax)
                self.stim = numpy.exp(self.stim)
    
        
    def plotData(self):
        if self.psyFunFit == "Linear":
            self.ax.plot(self.stim, self.pcCorr)
        elif self.psyFunFit == "Logarithmic":
            self.ax.plot(log10(self.stim), self.pcCorr)
            powd = nextPow10Down(10**(self.ax.get_xlim()[0]))
            powup = nextPow10Up(10**(self.ax.get_xlim()[1]))
            majTicks = arange(powd, powup+1)
            self.ax.set_xticks(majTicks)
            xTickLabels = []
            for tick in majTicks:
                xTickLabels.append(str(10**tick))
            self.ax.set_xticklabels(xTickLabels)
            minTicks = []
            for i in range(len(majTicks)-1):
                minTicks.extend(log10(linspace(10**majTicks[i], 10**majTicks[i+1], 10)))
            self.ax.set_xticks(minTicks, minor=True)

    def toggleGrid(self, state):
        self.ax.grid(True)
        if self.gridOn.isChecked():
            self.ax.grid(True)#True, color=self.gridColor, linewidth=self.gridLineWidth)
            self.ax.grid(True, 'minor', linewidth=0.6)#True, color=self.gridColor, linewidth=self.gridLineWidth)
            try:
                self.ax2.grid(True)#True, color=self.gridColor, linewidth=self.gridLineWidth)
                self.ax2.grid(True, 'minor', linewidth=0.6)#True, color=self.gridColor, linewidth=self.gridLineWidth)
            except:
                pass
        else:
            self.ax.grid(False)
            self.ax.grid(False, 'minor')
            try:
                self.ax2.grid(False)
                self.ax2.grid(False, 'minor')
            except:
                pass

        self.canvas.draw()
