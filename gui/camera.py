import numpy as np
import math
from scipy.spatial.transform.rotation import Rotation
from OpenGL.GL import *
from OpenGL.GLU import *


def getSE3ByTransV(_v):
    ret = np.eye(4)
    ret[:3, 3] = _v
    return ret

def getSE3ByRotY(_rot_y):
    ret = np.eye(4)
    ret[:3, :3] = Rotation.from_rotvec(_rot_y * np.array([0., 1., 0.])).as_dcm()
    return ret

def getSE3ByRotX(_rot_x):
    ret = np.eye(4)
    ret[:3, :3] = Rotation.from_rotvec(_rot_x * np.array([1., 0., 0.])).as_dcm()
    return ret

def invertSE3(_T):
    ret = np.eye(4)
    ret[:3, :3] = _T[:3, :3].T
    ret[:3, 3] = -np.dot(_T[:3, :3].T, _T[:3, 3])
    return ret


class Camera(object):
    def __init__(self):
        self.center = np.array([0., 0.0, 0.])
        self.rotateY = math.radians(0.)
        self.rotateX = math.radians(-15.0)
        self.distance = 3.1

    def getSE3(self):
        SE3_1 = getSE3ByTransV(self.center)
        SE3_2 = getSE3ByRotY(self.rotateY)
        SE3_3 = getSE3ByRotX(self.rotateX)
        SE3_4 = getSE3ByTransV([0, 0, self.distance])
        SE3 = np.dot(np.dot(np.dot(SE3_1, SE3_2), SE3_3), SE3_4)
        return SE3

    def getUpRightVectors(self):
        SE3_2 = getSE3ByRotY(self.rotateY)
        SE3_3 = getSE3ByRotX(self.rotateX)
        SO3 = np.dot(SE3_2, SE3_3)[:3, :3]
        return np.dot(SO3, (0, 1, 0)), np.dot(SO3, (1, 0, 0))

    def transform(self):
        glMultMatrixf(invertSE3(self.getSE3()).transpose())


class Camera2(object):
    # viewing - z direction, right - handed coordinate
    def __init__(self):
        self.T = np.eye(4)
        self.T[:3, 3] = np.array([0., 3., 4.])
        self.T[:3, :3] = Rotation.from_rotvec(-math.atan(0.75) * np.array([1., 0., 0.])).as_dcm()

        self.transforming_T = self.T.copy()
        self.distance = 5.
        self.transforming = False

        self.eye = np.zeros(3)
        self.view = np.zeros(3)
        self.obj = np.zeros(3)
        self.up = np.zeros(3)

    def camera_lookat(self):
        look_T = self.T if self.transforming else self.transforming_T
        self.vec_invalidate(look_T)
        gluLookAt(self.eye[0], self.eye[1], self.eye[2], self.obj[0], self.obj[1], self.obj[2], self.up[0], self.up[1], self.up[2])

    def set_distance(self, d):
        rate = d / self.distance
        self.vec_invalidate(self.T)
        self.T[:3, 3] = (1. - rate) * self.obj + rate * self.eye
        if d > 0:
            self.distance = d

    def set_pos_on_sphere_after_screen_rotate(self, mousedx, mousedy, screenw, screenh):
        theta = (math.pi / 5.) * math.sqrt((float(4*mousedx * mousedx))/(screenw*screenw) + (float(4*mousedy * mousedy))/(screenh*screenh))
        rotate_phi = 0.

        if mousedx == 0:
            if mousedy > 0:
                rotate_phi = math.pi/2.
            else:
                rotate_phi = -math.pi/2.
        else:
            rotate_phi = math.atan2(mousedy, mousedx)

        rot_vec = -np.dot(self.T[:3, :3], np.dot(Rotation.from_rotvec(rotate_phi * np.array([0., 0., 1.])).as_dcm(), np.array([0., 1., 0.])))
        self.vec_invalidate(self.T)
        self.transforming_T[:] = self.T[:]

        translate_temp = np.eye(4)
        translate_temp[:3, 3] = -self.obj
        self.transforming_T = np.dot(translate_temp, self.transforming_T)
        rotate_temp = np.eye(4)
        rotate_temp[:3, :3] = Rotation.from_rotvec(theta * rot_vec).as_dcm()
        self.transforming_T = np.dot(rotate_temp, self.transforming_T)
        self.transforming_T = np.dot(-translate_temp, self.transforming_T)

    def add_pos_after_screen_shift(self, mousedx, mousedy, screenh, fovy_rad):
        rate = 2. * self.distance * math.tan(fovy_rad / 2.)
        displacement = np.array((float(mousedx) / screenh, float(mousedy) / screenh, 0))
        self.transforming_T[:] = self.T[:]
        translate_temp = np.eye(4)
        translate_temp[:3, 3] = -displacement
        self.transforming_T = np.dot(self.transforming_T, translate_temp)

    def set_transforming(self):
        self.transforming = True

    def unset_transforming(self):
        self.transforming = False

    def invalidate(self):
        self.T[:] = self.transforming_T[:]
        self.vec_invalidate(self.T)

    def yview(self):
        pass

    def xview(self):
        pass

    def zview(self):
        pass

    def vec_invalidate(self, _T):
        self.eye = _T[:3, 3]
        self.view = np.dot(_T[:3, :3], np.array([0., 0., -1.]))
        self.obj = self.eye + (self.distance + self.view)
        self.up = np.dot(_T[:3, :3], np.array([0., 1., 0.]))
