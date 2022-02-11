
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Geom, GeomNode, GeomVertexFormat, \
    GeomVertexData, GeomTriangles, GeomVertexWriter, GeomVertexReader
from panda3d.core import NodePath
from panda3d.core import AmbientLight, PointLight, DirectionalLight
from panda3d.core import VBase4, Vec3
from direct.task import Task
import sys
import random
from math import sqrt, sin, cos, pi
from model_data import vertices, faces


import cv2
import mediapipe as mp
import numpy as np

class BrownianBlender(ShowBase):
    def __init__(self):
        # Basics
        ShowBase.__init__(self)
        base.disableMouse()
        base.setFrameRateMeter(True)
        self.accept("escape", sys.exit)
        self.camera.set_pos(0, 0, -2)
        self.camera.look_at(0,0,0)
        #self.camera.setHpr(-16.5869, 82.7357, 30.1287)
        
        # Add ambient light
        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientLightNP = self.render.attachNewNode(ambientLight)
        self.render.setLight(ambientLightNP)
        
        #plight = DirectionalLight('plight')
        #plight.setShadowCaster(True, 512, 512)
        #plight.setColor(VBase4(1, 1, 1, 1))
        #self.plnp = self.render.attachNewNode(plight)
        #self.plnp.setPos(0.3759736716747284, 0.499371200799942, -1.889259696006775)
        #self.plnp.look_at(-16.5869, 82.7357, 30.1287)
        #self.render.setLight(self.plnp)


        #adjust render settings
        self.render.setShaderAuto()

        # Create the geometry
        geom = self.create_geom()
        np = NodePath(geom)
        np.setDepthOffset(1)
        np.reparent_to(self.render)




        #create mediapipe
        self.face_mesh_processor =  mp.solutions.face_mesh.FaceMesh( max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)

        #create video capture
        self.open_camera()

        # Start the task to interpolate the geometry each frame
        self.taskMgr.add(self.regen_face, 'generate_new_vertecies', sort = 5)
        #self.need_to_swap_maps = True
        #self.taskMgr.add(self.swap_maps, 'swap_geometry', sort = 5)
        #self.taskMgr.add(self.interpolate_maps, 'interpolate_geometry', sort = 10)

        self.accept("space", self.print_camera, [])


        #CAMERA CONTROLS
        self.yaw = 0
        self.pitch= 0
        self.accept("arrow_left", self.adjust_turning, [-1.0, 0.0])
        self.accept("arrow_right", self.adjust_turning, [1.0, 0.0])
        self.accept("arrow_up", self.adjust_turning, [0.0, 1.0])
        self.accept("arrow_down", self.adjust_turning, [0.0, -1.0])
        self.accept("w", self.adjust_loc, ["forward",1])
        self.accept("a", self.adjust_loc, ["left",1])
        self.accept("s", self.adjust_loc, ["backward",1])
        self.accept("d", self.adjust_loc, ["right",1])
   
    def open_camera(self):
        self.live_cam = cv2.VideoCapture(0)
        print("Waiting for camera to open")
        while(not self.live_cam.isOpened()):
            pass
        print("Camera on")

    def print_camera(self):
        x = self.camera.getPos().getX()
        y = self.camera.getPos().getY()
        z = self.camera.getPos().getZ()
        print(x, y, z)


    def create_geom(self):
        
        #bpy.ops.mesh.primitive_cube_add()
        vertex_format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('face_vertex_data', vertex_format, Geom.UHDynamic)
        vdata.setNumRows(len(vertices))

        #create vertex writer and add vertices
        vertex_writer = GeomVertexWriter(vdata, 'vertex')
        for vertex in vertices:
            vertex_writer.addData3(*vertex)

        geom = Geom(vdata)

        for face in faces:
            if(len(face) != 3):
                print("bad face")

            prim = GeomTriangles(Geom.UHStatic)
            prim.addVertices(*face)
            prim.closePrimitive()
            geom.addPrimitive(prim)

        # Create the actual node
        node = GeomNode('gnode')
        node.addGeom(geom)
        
        # Remember GeomVertexWriters to adjust vertex data later
        #self.vertex_writer = vertex
        #self.color_writer = color
        self.vdata = vdata
        
        return node

    def regen_face(self, task):
        if(not self.live_cam.isOpened()):
            print("camera is closed")
            self.open_camera()
            return task.cont
        
        success, image = self.live_cam.read()
        if(not success):
            print("unable to read image")
            return task.cont

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh_processor.process(image)

        if(not results.multi_face_landmarks):
            print("unable to process")
            return task.cont
            
        face_landmarks = results.multi_face_landmarks[0].landmark

        vertex_writer = GeomVertexWriter(self.vdata, 'vertex')


        landmark_x = np.array([])
        landmark_y = np.array([])
        landmark_z = np.array([])
        for landmark in face_landmarks:
            landmark_x = np.append(landmark_x, landmark.x)
            landmark_y = np.append(landmark_y, landmark.y)
            landmark_z = np.append(landmark_z, landmark.z)

        average_x = np.mean(landmark_x)
        average_y = np.mean(landmark_y)
        average_z = np.mean(landmark_z)

        centered_x = landmark_x - average_x  
        centered_y = landmark_y - average_y
        centered_z = landmark_z - average_z


        for i in range(len(centered_x)):
            vertex_writer.setData3f(centered_x[i], centered_y[i], centered_z[i])


        return task.cont

    def adjust_loc(self, direction, speed):
        loc = self.plnp.getPos()
        print("moving", loc)
        if(direction == "forward"):
            loc.addY(speed)
            self.plnp.setPos(loc)
        if(direction == "left"):
            loc.addX(speed)
            self.plnp.setPos(loc)
        if(direction == "backward"):
            loc.addY(-1*speed)
            self.plnp.setPos(loc)
        if(direction == "right"):
            loc.addX(-1*speed)
            self.plnp.setPos(loc)

    def adjust_turning(self, yaw, pitch):
        self.yaw += yaw
        self.pitch += pitch

        print(self.yaw,self.pitch )

        self.plnp.setHpr(self.yaw,self.pitch,0)

demo = BrownianBlender()
demo.run()