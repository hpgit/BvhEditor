from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtOpenGL import *
from PySide2.QtWidgets import *
from gui.camera import Camera
import math
from OpenGL import GL, GLU

class GLWidget(QGLWidget):
    def __init__(self, parent=None):
        QGLWidget.__init__(self, parent)

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

    def minimumSizeHint(self):
        return QSize(320, 240)

    def sizeHint(self):
        return QSize(800, 600)

    def initializeGL(self):
        self.qglClearColor(self.trolltechPurple.darker())
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
        # GL.glCallList(self.object)

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
