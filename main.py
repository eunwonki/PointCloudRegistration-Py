import os.path
import tkinter.filedialog
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import *

import util

from direct.showbase.ShowBase import ShowBase

default_source_path = "data/model.obj"
default_target_path = "data/scene.obj"


class App(ShowBase):
    def __init__(self):
        ShowBase.__init__(self, windowType='none')

        self.target_path_label = None
        self.source = None
        self.source_pc_node = None
        self.source_processed_pc = None

        self.target = None
        self.target_pc_node = None
        self.target_processed_pc = None

        self.source_pc_view = None
        self.source_processed_pc_view = None
        self.target_pc_view = None
        self.target_processed_pc_view = None
        self.registration_view = None
        self.ui_view = None

        self.start_tk()

        frame = self.tkRoot
        frame.geometry('1900x800')
        frame.title('PointCLoudRegistration')

        menubar = tkinter.Menu(frame)
        filemenu = tkinter.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Change Source", command=self.change_source)
        filemenu.add_command(label="Change Target", command=self.change_target)
        frame.config(menu=menubar)

        frame.update()

        frame_id = frame.winfo_id()
        width = frame.winfo_width()
        height = frame.winfo_height()

        props = WindowProperties()
        props.setParentWindow(frame_id)
        props.setOrigin(0, 0)
        props.setSize(width, height)

        self.makeDefaultPipe()
        self.openDefaultWindow(props=props)
        self.setFrameRateMeter(True)

        '''set panda3d scene'''

        self.setLight()
        self.setDisplayRegion()

        # Models
        self.voxel_size = 0.005

        self.load_source(default_source_path)
        self.load_target(default_target_path)

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
        camPivot1.setPos(self.source_pc_node.getBounds().getCenter())
        camera1.reparent_to(camPivot1)
        camera1.set_y(-2)

        cam2 = Camera("cam2")
        cam2.setLens(lens)
        camera2 = self.render.attachNewNode(cam2)
        camPivot2 = self.render.attachNewNode("cam_pivot2")
        camPivot2.setPos(self.source_processed_pc.getBounds().getCenter())
        camera2.reparent_to(camPivot2)
        camera2.set_y(-2)

        cam3 = Camera("cam3")
        cam3.setLens(lens)
        camera3 = self.render.attachNewNode(cam3)
        camPivot3 = self.render.attachNewNode("cam_pivot3")
        camPivot3.setPos(self.target_pc_node.getBounds().getCenter())
        camera3.reparent_to(camPivot3)
        camera3.set_y(-2)

        cam4 = Camera("cam4")
        cam4.setLens(lens)
        camera4 = self.render.attachNewNode(cam4)
        camPivot4 = self.render.attachNewNode("cam_pivot4")
        camPivot4.setPos(self.target_processed_pc.getBounds().getCenter())
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
        self.source_pc_view.setCamera(camera1)
        self.source_processed_pc_view.setCamera(camera2)
        self.target_pc_view.setCamera(camera3)
        self.target_processed_pc_view.setCamera(camera4)
        self.registration_view.setCamera(self.camera5)

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


    def load_source(self, filepath):
        filepath = os.path.abspath(filepath)
        filepath = Filename.fromOsSpecific(filepath).getFullpath()

        if self.source is not None:
            self.source.removeNode()
        self.source = self.loader.loadModel(filepath).findAllMatches('**/+GeomNode')[0]
        self.source.setColorScale(1, 0.5, 0.5, 1)
        self.source.reparentTo(self.render)

        if self.source_pc_node is not None:
            self.source_pc_node.removeNode()
        self.source_pc_node = util.mesh_node_to_point_cloud_node(self.source)
        self.source_pc_node.reparentTo(self.render)
        self.source_pc_node.setPos(5, 0, 5)

        if self.source_processed_pc is not None:
            self.source_processed_pc.removeNode()
        self.source_processed_pc = util.process(self.source_pc_node, self.voxel_size)
        self.source_processed_pc.reparentTo(self.render)
        self.source_processed_pc.setPos(10, 0, 10)

        self.init_transform()

        self.source_path_label["text"] = filepath


    def load_target(self, filepath):
        filepath = os.path.abspath(filepath)
        filepath = Filename.fromOsSpecific(filepath).getFullpath()

        if self.target is not None:
            self.target.removeNode()
        self.target = self.loader.loadModel(filepath).findAllMatches('**/+GeomNode')[0]
        self.target.setColorScale(0.5, 1, 0.5, 1)
        self.target.reparentTo(self.render)

        if self.target_pc_node is not None:
            self.target_pc_node.removeNode()
        self.target_pc_node = util.mesh_node_to_point_cloud_node(self.target)
        self.target_pc_node.reparentTo(self.render)
        self.target_pc_node.setPos(15, 0, 15)

        if self.target_processed_pc is not None:
            self.target_processed_pc.removeNode()
        self.target_processed_pc = util.process(self.target_pc_node, self.voxel_size)
        self.target_processed_pc.reparentTo(self.render)
        self.target_processed_pc.setPos(20, 0, 20)

        self.target_path_label["text"] = filepath


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
        light = PointLight('Light')
        light.set_color((1, 1, 1, 1))
        light = self.render.attachNewNode(light)
        light.reparentTo(self.render)
        light.setPos(0, 0, 0)
        self.render.setLight(light)

        light = PointLight('Light')
        light.set_color((1, 1, 1, 1))
        light = self.render.attachNewNode(light)
        light.reparentTo(self.render)
        light.setPos(10, 0, 10)
        self.render.setLight(light)

        light = PointLight('Light')
        light.set_color((1, 1, 1, 1))
        light = self.render.attachNewNode(light)
        light.reparentTo(self.render)
        light.setPos(20, 0, 20)
        self.render.setLight(light)

    def setDisplayRegion(self):
        # Disable the default DisplayRegion, which covers the whole screen.
        dr = self.camNode.getDisplayRegion(0)
        dr.setActive(0)

        # Now, make a new pair of side-by-side DisplayRegions.
        window = dr.getWindow()
        self.source_pc_view = window.makeDisplayRegion(0, 4 / 19, 0.5, 1)
        self.source_pc_view.setSort(dr.getSort())
        self.source_pc_view.setClearColorActive(True)
        self.source_pc_view.setClearColor((0, 0, 0, 0))

        self.source_processed_pc_view = window.makeDisplayRegion(4 / 19, 8 / 19, 0.5, 1)
        self.source_processed_pc_view.setSort(dr.getSort())
        self.source_processed_pc_view.setClearColorActive(True)
        self.source_processed_pc_view.setClearColor((0.1, 0.1, 0.1, 0.1))

        self.target_pc_view = window.makeDisplayRegion(0, 4 / 19, 0, 0.5)
        self.target_pc_view.setSort(dr.getSort())
        self.target_pc_view.setClearColorActive(True)
        self.target_pc_view.setClearColor((0.2, 0.2, 0.2, 0.2))

        self.target_processed_pc_view = window.makeDisplayRegion(4 / 19, 8 / 19, 0, 0.5)
        self.target_processed_pc_view.setSort(dr.getSort())
        self.target_processed_pc_view.setClearColorActive(True)
        self.target_processed_pc_view.setClearColor((0.3, 0.3, 0.3, 0.3))

        self.registration_view = window.makeDisplayRegion(8 / 19, 16 / 19, 0, 1)
        self.registration_view.setSort(dr.getSort())
        self.registration_view.setClearColorActive(True)
        self.registration_view.setClearColor((0.4, 0.4, 0.4, 0.4))

        self.ui_view = window.makeDisplayRegion(16 / 19, 1, 0, 1)
        self.ui_view.setSort(dr.getSort())
        self.ui_view.setClearColorActive(True)
        self.ui_view.setClearColor((0.5, 0.5, 0, 1))

        myCamera2d = NodePath(Camera('myCam2d'))
        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1000, 1000)
        myCamera2d.node().setLens(lens)

        myRender2d = NodePath('myRender2d')
        myRender2d.setDepthTest(False)
        myRender2d.setDepthWrite(False)
        myCamera2d.reparentTo(myRender2d)
        self.ui_view.setCamera(myCamera2d)

        myAspect2d = myRender2d.attachNewNode(PGTop('myAspect2d'))
        mw_node = MouseWatcher("my_mouse_watcher")
        mw_node.set_display_region(self.ui_view)
        input_ctrl = self.mouseWatcher.parent
        mw = input_ctrl.attach_new_node(mw_node)
        bt_node = ButtonThrower("my_btn_thrower")
        mw.attach_new_node(bt_node)
        myAspect2d.node().setMouseWatcher(mw_node)

        font = self.loader.loadFont('config/arial.ttf', 0)
        font.setPointSize(10)

        self.source_path_label = DirectLabel(text="", text_font=font, text_wordwrap=20, text_scale=0.1, parent=myAspect2d, frameSize=(-1, 1, -.2, .1), pos=(0,0,0.9))
        self.target_path_label = DirectLabel(text="", text_font=font, text_wordwrap=20, text_scale=0.1, parent=myAspect2d, frameSize=(-1, 1, -.2, .1), pos=(0,0,0.55))

        DirectButton(text=["init"], parent=myAspect2d, frameSize=(-.5, .5, -.05, .1), text_scale=0.1, pos=(0,0,0.2), command=self.init_transform)
        DirectButton(text=["global registration"], parent=myAspect2d, frameSize=(-.5, .5, -.05, .1), text_scale=0.1, pos=(0,0,0), command=self.global_registration)
        DirectButton(text=["local registration"], parent=myAspect2d, frameSize=(-.5, .5, -.05, .1), text_scale=0.1, pos=(0,0,-0.2), command=self.local_registration)

    def change_source(self):
        file = tkinter.filedialog.askopenfilename(initialdir="/", title="Select file",
                                                  filetypes=(("Wavefront files", "*.obj"),
                                                             ("all files", "*.*")))
        self.load_source(file)

    def change_target(self):
        file = tkinter.filedialog.askopenfilename(initialdir="/", title="Select file",
                                                  filetypes=(("Wavefront files", "*.obj"),
                                                             ("all files", "*.*")))
        self.load_target(file)

    def init_transform(self):
        self.source.setMat(LMatrix4f.identMat())

    def global_registration(self):
        result = util.global_registration(self.source_processed_pc, self.target_processed_pc, self.voxel_size)
        self.source.setMat(util.numpy_array_to_mat4(result.transformation))

    def local_registration(self):
        result = util.local_registration(self.source_processed_pc, self.target_processed_pc,
                                         util.numpy_array_to_mat4(self.source.getMat()), self.voxel_size)
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
