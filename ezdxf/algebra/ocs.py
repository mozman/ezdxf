# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from .vector import Vector


class OCS(object):
    Ax = Vector(1, 0, 0)
    Ay = Vector(0, 1, 0)
    Az = Vector(0, 0, 1)
    Wx = Vector(1, 0, 0)
    Wy = Vector(0, 1, 0)
    Wz = Vector(0, 0, 1)

    def __init__(self, extrusion=(0, 0, 1)):
        self.transform = extrusion != (0, 0, 1)
        if self.transform:
            self.Az = Vector(extrusion).normalize()
            if (abs(self.Az.x) < 1/64.) and (abs(self.Az.y) < 1/64.):
                Ax = Vector(0, 1, 0).cross(self.Az)
            else:
                Ax = Vector(0, 0, 1).cross(self.Az)
            self.Ax = Ax.normalize()
            self.Ay = self.Az.cross(Ax).normalize()
            self.Wx = self.wcs_to_ocs((1, 0, 0))
            self.Wy = self.wcs_to_ocs((0, 1, 0))
            self.Wz = self.wcs_to_ocs((0, 0, 1))

    def wcs_to_ocs(self, point):
        if not self.transform:
            return point
        px, py, pz = Vector(point)
        ax = self.Ax
        ay = self.Ay
        az = self.Az
        x = px * ax.x + py * ax.y + pz * ax.z
        y = px * ay.x + py * ay.y + pz * ay.z
        z = px * az.x + py * az.y + pz * az.z
        return Vector(x, y, z)

    def ocs_to_wcs(self, point):
        if not self.transform:
            return point
        wx = self.Wx
        wy = self.Wy
        wz = self.Wz
        px, py, pz = Vector(point)
        x = px * wx.x + py * wx.y + pz * wx.z
        y = px * wy.x + py * wy.y + pz * wy.z
        z = px * wz.x + py * wz.y + pz * wz.z
        return Vector(x, y, z)


def wcs_to_ocs(point, extrusion=(0, 0, 1)):
    return OCS(extrusion).wcs_to_ocs(point)


def ocs_to_wcs(point, extrusion=(0, 0, 1)):
    return OCS(extrusion).ocs_to_wcs(point)
