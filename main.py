import sys
import math
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtOpenGL import *
from PySide2.QtWidgets import *
from gui.camera import Camera
from OpenGL import GL, GLU


class Window(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.glWidget = GLWidget()

        self.xSlider = self.createSlider(SIGNAL("xRotationChanged(int)"),
                                         self.glWidget.setXRotation)
        self.ySlider = self.createSlider(SIGNAL("yRotationChanged(int)"),
                                         self.glWidget.setYRotation)
        self.zSlider = self.createSlider(SIGNAL("zRotationChanged(int)"),
                                         self.glWidget.setZRotation)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        mainLayout.addWidget(self.xSlider)
        mainLayout.addWidget(self.ySlider)
        mainLayout.addWidget(self.zSlider)
        self.setLayout(mainLayout)

        self.xSlider.setValue(170 * 16)
        self.ySlider.setValue(160 * 16)
        self.zSlider.setValue(90 * 16)

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


class GLWidget(QGLWidget):
    def __init__(self, parent=None):
        QGLWidget.__init__(self, parent)

        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.lastPos = QPoint()

        self.trolltechGreen = QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.trolltechPurple = QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)

        # self.camera = Camera()

        self.camera = Camera()
        self.mouseX = 0
        self.mouseY = 0
        self.mousePrevX = 0
        self.mousePrevY = 0

        self.projectionOrtho = False
        self.projectionChanged = False
        self.prevRotX = 0
        self.prevRotY = 0

        self.w = self.width()
        self.h = self.height()

    def xRotation(self):
        return self.xRot

    def yRotation(self):
        return self.yRot

    def zRotation(self):
        return self.zRot

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.emit(SIGNAL("xRotationChanged(int)"), angle)
            self.updateGL()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.emit(SIGNAL("yRotationChanged(int)"), angle)
            self.updateGL()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.emit(SIGNAL("zRotationChanged(int)"), angle)
            self.updateGL()

    def initializeGL(self):
        self.qglClearColor(self.trolltechPurple.darker())
        self.object = self.makeObject()
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        self.projectPerspective()

    def projectOrtho(self, distance):
        self.projectionMode = True
        glViewport(0, 0, self.w(), self.h())
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        x = float(self.w()) / float(self.h()) * distance
        y = 1. * distance
        # glOrtho(-x/2., x/2., -y/2., y/2., .1 ,1000.)
        glOrtho(-x / 2., x / 2., -y / 2., y / 2., -1000., 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def projectPerspective(self):
        self.projectionMode = False
        GL.glViewport(0, 0, self.w, self.h)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45., float(self.w) / float(self.h), 0.1, 1000.)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        if self.projectionChanged:
            if self.projectionOrtho:
                self.projectOrtho(self.camera.distance)
            else:
                self.projectPerspective()
            self.projectionChanged = False

        GL.glLoadIdentity()
        self.camera.transform()
        # GL.glTranslated(0.0, 0.0, -10.0)
        # GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        # GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        # GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        GL.glCallList(self.object)

    def resizeGL(self, width, height):
        super(GLWidget, self).resizeGL(width, height)
        self.projectionChanged = True
        self.w = width
        self.h = height
        # side = min(width, height)
        # GL.glViewport(0, 0, width, height)
        # # GL.glViewport(int((width - side) / 2),int((height - side) / 2), side, side)
        # GL.glMatrixMode(GL.GL_PROJECTION)
        # GL.glLoadIdentity()
        # GLU.gluPerspective(45., float(self.width()) / float(self.height()), 0.1, 1000.)
        # GL.glMatrixMode(GL.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = QPoint(event.pos())

    def mouseMoveEvent(self, event):
        dx = event.pos().x() - self.lastPos.x()
        dy = event.pos().y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.camera.rotateY -= math.radians(dx)
            self.camera.rotateX -= math.radians(dy)
            self.repaint()
        elif event.buttons() & Qt.MiddleButton:
            self.camera.center[1] += self.camera.distance * .05 * dy / 12.0
            self.repaint()
        elif event.buttons() & Qt.RightButton:
            # right
            self.camera.center[0] -= self.camera.distance * .05 * math.cos(self.camera.rotateY) * dx / 12.0
            self.camera.center[2] -= self.camera.distance * .05 * -math.sin(self.camera.rotateY) * dx / 12.0
            # look
            self.camera.center[0] -= self.camera.distance * .05 * math.sin(self.camera.rotateY) * dy / 12.0
            self.camera.center[2] -= self.camera.distance * .05 * math.cos(self.camera.rotateY) * dy / 12.0
            self.repaint()

        self.lastPos = QPoint(event.pos())

    def mouseReleaseEvent(self, event):
        self.lastPos = QPoint(event.pos())

    def wheelEvent(self, event):
        self.camera.distance -= self.camera.distance * .2 * event.delta() / 120.0
        if self.camera.distance < 0.0001:
            self.camera.distance = 0.0001
        self.projectionChanged = True
        self.repaint()

    def makeObject(self):
        genList = GL.glGenLists(1)
        GL.glNewList(genList, GL.GL_COMPILE)

        GL.glBegin(GL.GL_QUADS)

        x1 = +0.06
        y1 = -0.14
        x2 = +0.14
        y2 = -0.06
        x3 = +0.08
        y3 = +0.00
        x4 = +0.30
        y4 = +0.22

        self.quad(x1, y1, x2, y2, y2, x2, y1, x1)
        self.quad(x3, y3, x4, y4, y4, x4, y3, x3)

        self.extrude(x1, y1, x2, y2)
        self.extrude(x2, y2, y2, x2)
        self.extrude(y2, x2, y1, x1)
        self.extrude(y1, x1, x1, y1)
        self.extrude(x3, y3, x4, y4)
        self.extrude(x4, y4, y4, x4)
        self.extrude(y4, x4, y3, x3)

        Pi = 3.14159265358979323846
        NumSectors = 200

        for i in range(NumSectors):
            angle1 = (i * 2 * Pi) / NumSectors
            x5 = 0.30 * math.sin(angle1)
            y5 = 0.30 * math.cos(angle1)
            x6 = 0.20 * math.sin(angle1)
            y6 = 0.20 * math.cos(angle1)

            angle2 = ((i + 1) * 2 * Pi) / NumSectors
            x7 = 0.20 * math.sin(angle2)
            y7 = 0.20 * math.cos(angle2)
            x8 = 0.30 * math.sin(angle2)
            y8 = 0.30 * math.cos(angle2)

            self.quad(x5, y5, x6, y6, x7, y7, x8, y8)

            self.extrude(x6, y6, x7, y7)
            self.extrude(x8, y8, x5, y5)

        GL.glEnd()
        GL.glEndList()

        return genList

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.qglColor(self.trolltechGreen)

        GL.glVertex3d(x1, y1, +0.05)
        GL.glVertex3d(x2, y2, +0.05)
        GL.glVertex3d(x3, y3, +0.05)
        GL.glVertex3d(x4, y4, +0.05)

        GL.glVertex3d(x4, y4, -0.05)
        GL.glVertex3d(x3, y3, -0.05)
        GL.glVertex3d(x2, y2, -0.05)
        GL.glVertex3d(x1, y1, -0.05)

    def extrude(self, x1, y1, x2, y2):
        self.qglColor(self.trolltechGreen.darker(250 + int(100 * x1)))

        GL.glVertex3d(x1, y1, -0.05)
        GL.glVertex3d(x2, y2, -0.05)
        GL.glVertex3d(x2, y2, +0.05)
        GL.glVertex3d(x1, y1, +0.05)

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle


if __name__ == '__main__':
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
