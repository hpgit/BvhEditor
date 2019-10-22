import sys
import math
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtOpenGL import *
from PySide2.QtWidgets import *
from gui.camera import Camera
from gui.glwidget import GLWidget
from OpenGL import GL, GLU

from util.bvh import readBvhFileAsBvh


class Window(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.glWidget = GLWidget()

        # self.xSlider = self.createSlider(SIGNAL("xRotationChanged(int)"),
        #                                  self.glWidget.setXRotation)
        # self.ySlider = self.createSlider(SIGNAL("yRotationChanged(int)"),
        #                                  self.glWidget.setYRotation)
        # self.zSlider = self.createSlider(SIGNAL("zRotationChanged(int)"),
        #                                  self.glWidget.setZRotation)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        # mainLayout.addWidget(self.xSlider)
        # mainLayout.addWidget(self.ySlider)
        # mainLayout.addWidget(self.zSlider)
        self.setLayout(mainLayout)

        # self.xSlider.setValue(170 * 16)
        # self.ySlider.setValue(160 * 16)
        # self.zSlider.setValue(90 * 16)

        self.setWindowTitle(self.tr("Hello GL"))

    def createSlider(self, changedSignal, setterSlot):
        slider = QSlider(Qt.Vertical)

        slider.setRange(0, 360 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QSlider.TicksRight)

        # self.glWidget.connect(slider, SIGNAL("valueChanged(int)"), setterSlot)
        # self.connect(self.glWidget, changedSignal, slider, SLOT("setValue(int)"))

        return slider


if __name__ == '__main__':
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
