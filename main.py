from panda3d.core import *

loadPrcFile("config\conf.prc")

from direct.showbase.ShowBase import ShowBase


class PointCloudRegistration(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.view_changed = None
        props = WindowProperties()
        self.win.requestProperties(props)

        source = self.loader.loadModel("data/model.obj")
        source.setPos(0, 1, 0)
        source.reparentTo(self.render)

        target = self.loader.loadModel("data/scene.obj")
        target.setPos(0, 1, 0)
        target.reparentTo(self.render)

        # set light
        point = PointLight('Point Light')
        point.set_color((1, 1, 1, 1))
        point = self.render.attachNewNode(point)
        point.reparentTo(self.render)
        point.setPos(0, 0, 1)
        self.render.setLight(point)

        """Disable the mouse and set up mouse-view functions"""
        self.disableMouse()

        """ Define camera parameters """
        # Camera angles
        self.camHorAng = 40
        self.camVerAng = 30
        self.camLens.setFov(self.camHorAng, self.camVerAng)
        # Near/Far plane
        self.camNear = 0.1
        self.camLens.setNear(self.camNear)
        self.camFar = 10
        self.camLens.setFar(self.camFar)
        # Camera pivot
        self.camPivot = self.render.attachNewNode("cam_pivot")
        self.camPivot.setPos(target.getBounds().getCenter())
        self.cam.reparent_to(self.camPivot)
        self.cam.set_y(-1)
        # Camera step for changes
        self.camSpeed = .05
        self.camZoomStep = 1

        # Set up camera zoom
        self.accept('wheel_up', self.zoom_in)
        self.accept('wheel_down', self.zoom_out)

        # Set up camera rotation
        self.accept('mouse1', self.wheel_down)
        self.accept('mouse1-up', self.wheel_up)
        self.lastMousePos = None
        self.wheel_pressed = False
        self.taskMgr.add(self.rotate_view, 'Rotate Camera View', extraArgs=[], appendTask=True)

    # Functions for camera zoom
    def zoom_out(self):
        """Translate the camera along the y axis of its matrix to zoom out the view"""
        self.view_changed = True
        self.cam.setPos(self.cam.getMat().xform((0, -self.camZoomStep, 0, 1)).getXyz())

    def zoom_in(self):
        """Translate the camera along the y axis its matrix to zoom in the view"""
        self.view_changed = True
        camPos = self.cam.getPos()
        newCamPos = self.cam.getMat().xform((0, self.camZoomStep, 0, 1)).getXyz()
        self.cam.setPos(newCamPos)

    # Functions for camera rotation
    def wheel_down(self):
        self.wheel_pressed = True
        self.lastMousePos = None

    def wheel_up(self):
        self.wheel_pressed = False
        self.lastMousePos = None

    def rotate_view(self, task):
        if self.wheel_pressed and self.mouseWatcherNode.hasMouse():
            mouse_pos = self.mouseWatcherNode.getMouse()
            if self.lastMousePos is None:
                self.lastMousePos = Point2(mouse_pos)
            else:
                d_heading, d_pitch = (mouse_pos - self.lastMousePos) * 100.
                pivot = self.camPivot
                pivot.set_hpr(pivot.get_h() - d_heading, pivot.get_p() + d_pitch, 0.)
                self.view_changed = True
                self.lastMousePos = Point2(mouse_pos)
        return task.again


app = PointCloudRegistration()
app.run()
