import os.path
import tkinter.filedialog
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import *

import util

from direct.showbase.ShowBase import ShowBase


default_source_path = "data/ColoredICP/skin_classic_left_red.ply"
default_target_path = "data/ColoredICP/scene_blue.ply"


class App(ShowBase):
    def __init__(self):
        ShowBase.__init__(self, windowType='none')

        self.source_path_label = None
        self.target_path_label = None

        self.source_parent_node = NodePath("source_parent")
        self.source_parent_node.reparentTo(self.render)

        self.source_mesh_node = None
        self.source_pc_node = None
        self.source_processed_pc_node = None

        self.target_parent_node = NodePath("target_parent")
        self.target_parent_node.reparentTo(self.render)

        self.target_mesh_node = None
        self.target_pc_node = None
        self.target_processed_pc_node = None

        self.source_pc_view = None
        self.source_processed_pc_view = None
        self.target_pc_view = None
        self.target_processed_pc_view = None
        self.registration_view = None
        self.ui_view = None

        self.start_tk()

        frame = self.tkRoot
        frame.geometry('1280x960')
        frame.title('PointCLoudRegistration')

        menu_bar = tkinter.Menu(frame)
        file_menu = tkinter.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Change Source", command=self.change_source)
        file_menu.add_command(label="Change Target", command=self.change_target)
        view_menu = tkinter.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        self.mesh_view_var = tkinter.IntVar(value=1)
        view_menu.add_checkbutton(label="Source Mesh", command=self.switch_mesh, variable=self.mesh_view_var)
        self.pc_view_var = tkinter.IntVar(value=1)
        view_menu.add_checkbutton(label="Source Point Cloud", command=self.switch_source_pc, variable=self.pc_view_var)
        self.filtered_pc_view_var = tkinter.IntVar(value=1)
        view_menu.add_checkbutton(label="Filtered Point Cloud", command=self.switch_source_processed_pc
                                  , variable=self.filtered_pc_view_var)
        registration_menu = tkinter.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Registration", menu=registration_menu)
        registration_menu.add_command(label="set source transform", command=self.set_source_transform)

        frame.config(menu=menu_bar)
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

        self.set_light()
        self.set_display_region()

        # Parameters
        self.voxel_size = 0.005

        self.setCamera()

        self.load_source(default_source_path)
        self.load_target(default_target_path)


    def setCamera(self):
        """ Define camera parameters """
        lens = self.default_lens()
        # Camera step for changes
        self.camSpeed = .05
        self.camZoomStep = 1

        # Camera
        self.cam = Camera("cam5")
        self.cam.setLens(lens)
        self.camera = self.render.attachNewNode(self.cam)
        self.camPivot = self.render.attachNewNode("cam_pivot")
        self.camera.reparent_to(self.camPivot)
        self.camera.set_y(-2)

        # Setup each camera.
        self.registration_view.setCamera(self.camera)

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

        if self.source_mesh_node is not None:
            self.source_mesh_node.removeNode()
        self.source_mesh_node = self.loader.loadModel(filepath).findAllMatches('**/+GeomNode')[0]
        self.source_mesh_node.setColorScale(1, 0.5, 0.5, 1)
        self.source_mesh_node.setTransparency(TransparencyAttrib.MAlpha)
        self.source_mesh_node.setAlphaScale(0.5)
        self.source_mesh_node.reparentTo(self.source_parent_node)
        # set to default hidden setting (synchronize between source and target)
        if self.target_mesh_node is not None:
            self.target_mesh_node.show()

        if self.source_pc_node is not None:
            self.source_pc_node.removeNode()
        self.source_pc_node = util.mesh_node_to_point_cloud_node(self.source_mesh_node)
        self.source_pc_node.reparentTo(self.source_parent_node)
        if self.target_pc_node is not None:
            self.target_pc_node.show()

        if self.source_processed_pc_node is not None:
            self.source_processed_pc_node.removeNode()
        self.source_processed_pc_node = util.process(self.source_pc_node, self.voxel_size)
        self.source_processed_pc_node.reparentTo(self.source_parent_node)
        if self.target_processed_pc_node is not None:
            self.target_processed_pc_node.show()

        self.init_transform()

        self.source_path_label["text"] = filepath

        self.mesh_view_var.set(1)
        self.pc_view_var.set(1)
        self.filtered_pc_view_var.set(1)


    def load_target(self, filepath):
        filepath = os.path.abspath(filepath)
        filepath = Filename.fromOsSpecific(filepath).getFullpath()

        if self.target_mesh_node is not None:
            self.target_mesh_node.removeNode()
        self.target_mesh_node = self.loader.loadModel(filepath).findAllMatches('**/+GeomNode')[0]
        self.target_mesh_node.setColorScale(0.5, 1, 0.5, 1)
        self.target_mesh_node.reparentTo(self.target_parent_node)
        if self.source_mesh_node is not None:
            self.source_mesh_node.show()  # set to default hidden setting (synchronize between source and target)

        if self.target_pc_node is not None:
            self.target_pc_node.removeNode()
        self.target_pc_node = util.mesh_node_to_point_cloud_node(self.target_mesh_node)
        self.target_pc_node.reparentTo(self.target_parent_node)
        if self.source_pc_node is not None:
            self.source_pc_node.show()
        self.camPivot.setPos(self.target_pc_node.getBounds().getCenter())

        if self.target_processed_pc_node is not None:
            self.target_processed_pc_node.removeNode()
        self.target_processed_pc_node = util.process(self.target_pc_node, self.voxel_size)
        self.target_processed_pc_node.reparentTo(self.target_parent_node)
        if self.source_processed_pc_node is not None:
            self.source_processed_pc_node.show()

        self.target_path_label["text"] = filepath

        self.mesh_view_var.set(1)
        self.pc_view_var.set(1)
        self.filtered_pc_view_var.set(1)


    def default_lens(self):
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



    def set_light(self):
        light = PointLight('Light')
        light.set_color((1, 1, 1, 1))
        light = self.render.attachNewNode(light)
        light.reparentTo(self.render)
        light.setPos(-1, -1, -1)
        self.render.setLight(light)

        light = PointLight('Light')
        light.set_color((1, 1, 1, 1))
        light = self.render.attachNewNode(light)
        light.reparentTo(self.render)
        light.setPos(1, 1, 1)
        self.render.setLight(light)

        light = PointLight('Light')
        light.set_color((1, 1, 1, 1))
        light = self.render.attachNewNode(light)
        light.reparentTo(self.render)
        light.setPos(1, -1, 1)
        self.render.setLight(light)

        light = PointLight('Light')
        light.set_color((1, 1, 1, 1))
        light = self.render.attachNewNode(light)
        light.reparentTo(self.render)
        light.setPos(1, 1, -1)
        self.render.setLight(light)


    def set_display_region(self):
        # Disable the default DisplayRegion, which covers the whole screen.
        dr = self.camNode.getDisplayRegion(0)
        dr.setActive(0)

        # Now, make a new pair of side-by-side DisplayRegions.
        window = dr.getWindow()

        self.registration_view = window.makeDisplayRegion(0, 3 / 4, 0, 1)
        self.registration_view.setSort(dr.getSort())
        self.registration_view.setClearColorActive(True)
        self.registration_view.setClearColor((0.4, 0.4, 0.4, 0.4))

        self.ui_view = window.makeDisplayRegion(3 / 4, 1, 0, 1)
        self.ui_view.setSort(dr.getSort())
        self.ui_view.setClearColorActive(True)
        self.ui_view.setClearColor((0.5, 0.5, 0, 1))

        camera2d = NodePath(Camera('cam2d'))
        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1000, 1000)
        camera2d.node().setLens(lens)

        render2d = NodePath('render2d')
        render2d.setDepthTest(False)
        render2d.setDepthWrite(False)
        camera2d.reparentTo(render2d)
        self.ui_view.setCamera(camera2d)

        aspect2d = render2d.attachNewNode(PGTop('aspect2d'))
        mw_node = MouseWatcher("mouse_watcher")
        mw_node.set_display_region(self.ui_view)
        input_ctrl = self.mouseWatcher.parent
        mw = input_ctrl.attach_new_node(mw_node)
        bt_node = ButtonThrower("btn_thrower")
        mw.attach_new_node(bt_node)
        aspect2d.node().setMouseWatcher(mw_node)

        font = self.loader.loadFont('config/arial.ttf', 0)
        font.setPointSize(10)

        self.source_path_label = DirectLabel(text="", text_font=font, text_wordwrap=20, text_scale=0.1, parent=aspect2d, frameSize=(-1, 1, -.2, .1), pos=(0,0,0.9))
        self.target_path_label = DirectLabel(text="", text_font=font, text_wordwrap=20, text_scale=0.1, parent=aspect2d, frameSize=(-1, 1, -.2, .1), pos=(0,0,0.55))

        DirectButton(text=["init"], parent=aspect2d, frameSize=(-.5, .5, -.05, .1), text_scale=0.1, pos=(0,0,0.2), command=self.init_transform)
        DirectButton(text=["global registration"], parent=aspect2d, frameSize=(-.5, .5, -.05, .1), text_scale=0.1, pos=(0,0,0), command=self.global_registration)
        DirectButton(text=["local registration"], parent=aspect2d, frameSize=(-.5, .5, -.05, .1), text_scale=0.1, pos=(0,0,-0.2), command=self.local_registration)

    def change_source(self):
        file = tkinter.filedialog.askopenfilename(initialdir="/", title="Select file")

        if file == '':
            return

        self.load_source(file)

    def change_target(self):
        file = tkinter.filedialog.askopenfilename(initialdir="/", title="Select file")

        if file == '':
            return

        self.load_target(file)


    def switch_mesh(self):
        self.switch_node(self.source_mesh_node)
        self.switch_node(self.target_mesh_node)

    def switch_source_pc(self):
        self.switch_node(self.source_pc_node)
        self.switch_node(self.target_pc_node)

    def switch_source_processed_pc(self):
        self.switch_node(self.source_processed_pc_node)
        self.switch_node(self.target_processed_pc_node)


    def switch_node(self, node):
        if node.isHidden():
            node.show()
        else:
            node.hide()

    def set_source_transform(self):
        input = tkinter.simpledialog.askstring("Input Dialog", "Transform Matrix", parent=self.tkRoot)

        if input is None:
            return

        f_list = str(input).split(' ')
        f_list = list(map(float, f_list))

        if len(f_list) != 16:
            print("size of transform matrix should be 16")
            return

        self.source_parent_node.setMat(util.array_to_mat4(f_list))

    def init_transform(self):
        self.source_parent_node.setMat(LMatrix4f.identMat())

    def global_registration(self):
        fast = False
        result = util.global_registration(self.source_processed_pc_node, self.target_processed_pc_node, self.voxel_size,
                                          fast)
        self.source_parent_node.setMat(util.numpy_array_to_mat4(result))

    def local_registration(self):
        result = util.local_registration(self.source_processed_pc_node, self.target_processed_pc_node,
                                         util.numpy_array_to_mat4(self.source_parent_node.getMat()), self.voxel_size)
        self.source_parent_node.setMat(util.numpy_array_to_mat4(result))

    # Functions for camera zoom
    def zoom_out(self):
        """Translate the camera along the y axis of its matrix to zoom out the view"""
        self.view_changed = True
        self.camera.setPos(self.camera.getMat().xform((0, -self.camZoomStep, 0, 1)).getXyz())

    def zoom_in(self):
        """Translate the camera along the y axis its matrix to zoom in the view"""
        self.view_changed = True
        camPos = self.camera.getPos()
        newCamPos = self.camera.getMat().xform((0, self.camZoomStep, 0, 1)).getXyz()
        self.camera.setPos(newCamPos)

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


app = App()
app.run()
