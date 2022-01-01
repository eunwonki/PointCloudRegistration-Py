from direct.gui.DirectButton import DirectButton
from panda3d.core import *

import o3dmodule
import util

loadPrcFile("config\conf.prc")

from direct.showbase.ShowBase import ShowBase

default_source_path = "data/model.obj"
default_target_path = "data/scene.obj"

class App(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.dr1 = None
        self.dr2 = None
        self.dr3 = None
        self.dr4 = None
        self.dr5 = None
        self.view_changed = None

        props = WindowProperties()
        self.win.requestProperties(props)

        self.setLight()
        self.setDisplayRegion()

        # Models
        self.voxel_size = 0.005

        self.source = self.loader.loadModel(default_source_path).findAllMatches('**/+GeomNode')[0]
        self.source.setColorScale(1, 0.5, 0.5, 1)
        self.source.reparentTo(self.render)

        self.target = self.loader.loadModel(default_target_path).findAllMatches('**/+GeomNode')[0]
        self.target.setColorScale(0.5, 1, 0.5, 1)
        self.target.reparentTo(self.render)

        source_pc_node = util.mesh_node_to_point_cloud_node(self.source)
        source_pc_node.reparentTo(self.render)
        source_pc_node.setPos(5, 0, 5)

        self.source_pc_processed = util.process(source_pc_node, self.voxel_size)
        self.source_pc_processed.reparentTo(self.render)
        self.source_pc_processed.setPos(10, 0, 10)

        target_pc_node = util.mesh_node_to_point_cloud_node(self.target)
        target_pc_node.reparentTo(self.render)
        target_pc_node.setPos(15, 0, 15)

        self.target_pc_processed = util.process(target_pc_node, self.voxel_size)
        self.target_pc_processed.reparentTo(self.render)
        self.target_pc_processed.setPos(20, 0, 20)

        """ Define camera parameters """
        lens = self.defaultLens()
        # Camera step for changes
        self.camSpeed = .05
        self.camZoomStep = 1

        # Camera
        cam1 = Camera("cam1")
        cam1.setLens(lens)
        camera1 = self.render.attachNewNode(cam1)
        camPivot1 = self.render.attachNewNode("cam_pivot1")
        camPivot1.setPos(source_pc_node.getBounds().getCenter())
        camera1.reparent_to(camPivot1)
        camera1.set_y(-2)

        cam2 = Camera("cam2")
        cam2.setLens(lens)
        camera2 = self.render.attachNewNode(cam2)
        camPivot2 = self.render.attachNewNode("cam_pivot2")
        camPivot2.setPos(self.source_pc_processed.getBounds().getCenter())
        camera2.reparent_to(camPivot2)
        camera2.set_y(-2)

        cam3 = Camera("cam3")
        cam3.setLens(lens)
        camera3 = self.render.attachNewNode(cam3)
        camPivot3 = self.render.attachNewNode("cam_pivot3")
        camPivot3.setPos(target_pc_node.getBounds().getCenter())
        camera3.reparent_to(camPivot3)
        camera3.set_y(-2)

        cam4 = Camera("cam4")
        cam4.setLens(lens)
        camera4 = self.render.attachNewNode(cam4)
        camPivot4 = self.render.attachNewNode("cam_pivot4")
        camPivot4.setPos(self.target_pc_processed.getBounds().getCenter())
        camera4.reparent_to(camPivot4)
        camera4.set_y(-2)

        self.cam5 = Camera("cam5")
        self.cam5.setLens(lens)
        self.camera5 = self.render.attachNewNode(self.cam5)
        self.camPivot5 = self.render.attachNewNode("cam_pivot5")
        self.camPivot5.setPos(self.target.getBounds().getCenter())
        self.camera5.reparent_to(self.camPivot5)
        self.camera5.set_y(-2)

        # Setup each camera.
        self.dr1.setCamera(camera1)
        self.dr2.setCamera(camera2)
        self.dr3.setCamera(camera3)
        self.dr4.setCamera(camera4)
        self.dr5.setCamera(self.camera5)

        """Disable the mouse and set up mouse-view functions"""
        self.disableMouse()

        # Set up camera zoom
        self.accept('wheel_up', self.zoom_in)
        self.accept('wheel_down', self.zoom_out)

        # Set up camera rotation
        self.accept('mouse1', self.wheel_down)
        self.accept('mouse1-up', self.wheel_up)
        self.lastMousePos = None
        self.wheel_pressed = False
        self.taskMgr.add(self.rotate_view, 'Rotate Camera View', extraArgs=[], appendTask=True)

    def defaultLens(self):
        # Camera angles
        lens = PerspectiveLens()
        camHorAng = 40
        camVerAng = 30
        lens.setFov(camHorAng, camVerAng)
        # Near/Far plane
        camNear = 0.01
        lens.setNear(camNear)
        camFar = 5
        lens.setFar(camFar)
        return lens

    def setLight(self):
        light = DirectionalLight('Light')
        light.set_color((1, 1, 1, 1))
        light = self.render.attachNewNode(light)
        light.reparentTo(self.render)
        light.setHpr(0, -60, 0)
        self.render.setLight(light)

    def setDisplayRegion(self):
        # Disable the default DisplayRegion, which covers the whole screen.
        dr = self.camNode.getDisplayRegion(0)
        dr.setActive(0)

        # Now, make a new pair of side-by-side DisplayRegions.
        window = dr.getWindow()
        self.dr1 = window.makeDisplayRegion(0, 4 / 19, 0.5, 1)
        self.dr1.setSort(dr.getSort())
        self.dr1.setClearColorActive(True)
        self.dr1.setClearColor((0, 0, 0, 0))

        self.dr2 = window.makeDisplayRegion(4 / 19, 8 / 19, 0.5, 1)
        self.dr2.setSort(dr.getSort())
        self.dr2.setClearColorActive(True)
        self.dr2.setClearColor((0.1, 0.1, 0.1, 0.1))

        self.dr3 = window.makeDisplayRegion(0, 4 / 19, 0, 0.5)
        self.dr3.setSort(dr.getSort())
        self.dr3.setClearColorActive(True)
        self.dr3.setClearColor((0.2, 0.2, 0.2, 0.2))

        self.dr4 = window.makeDisplayRegion(4 / 19, 8 / 19, 0, 0.5)
        self.dr4.setSort(dr.getSort())
        self.dr4.setClearColorActive(True)
        self.dr4.setClearColor((0.3, 0.3, 0.3, 0.3))

        self.dr5 = window.makeDisplayRegion(8 / 19, 16 / 19, 0, 1)
        self.dr5.setSort(dr.getSort())
        self.dr5.setClearColorActive(True)
        self.dr5.setClearColor((0.4, 0.4, 0.4, 0.4))

        self.dr6 = window.makeDisplayRegion(16 / 19, 1, 0, 1)
        self.dr6.setSort(dr.getSort())
        self.dr6.setClearColorActive(True)
        self.dr6.setClearColor((0.5, 0.5, 0, 1))

        button = DirectButton(text=["global registration"], pos=(2,0,0.1), scale=0.05, command=self.global_registration)
        button = DirectButton(text=["local registration"], pos=(2,0,0), scale=0.05, command=self.local_registration)

    def global_registration(self):
        result = util.global_registration(self.source_pc_processed, self.target_pc_processed, self.voxel_size)
        self.source.setMat(util.numpy_array_to_mat4(result.transformation))

    def local_registration(self):
        result = util.local_registration(self.source_pc_processed, self.target_pc_processed, util.numpy_array_to_mat4(self.source.getMat()), self.voxel_size)
        self.source.setMat(util.numpy_array_to_mat4(result.transformation))

    # Functions for camera zoom
    def zoom_out(self):
        """Translate the camera along the y axis of its matrix to zoom out the view"""
        self.view_changed = True
        self.camera5.setPos(self.camera5.getMat().xform((0, -self.camZoomStep, 0, 1)).getXyz())

    def zoom_in(self):
        """Translate the camera along the y axis its matrix to zoom in the view"""
        self.view_changed = True
        camPos = self.camera5.getPos()
        newCamPos = self.camera5.getMat().xform((0, self.camZoomStep, 0, 1)).getXyz()
        self.camera5.setPos(newCamPos)

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
                pivot = self.camPivot5
                pivot.set_hpr(pivot.get_h() - d_heading, pivot.get_p() + d_pitch, 0.)
                self.view_changed = True
                self.lastMousePos = Point2(mouse_pos)
        return task.again

app = App()
app.run()