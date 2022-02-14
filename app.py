
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Geom, GeomNode, GeomVertexFormat, \
    GeomVertexData, GeomTriangles, GeomVertexWriter, GeomVertexReader, TextureStage, TexGenAttrib
from panda3d.core import NodePath
from panda3d.core import AmbientLight, PointLight, DirectionalLight
from panda3d.core import VBase4, Vec3, LVector3, Spotlight, PerspectiveLens 
from direct.task import Task
import sys
import random
from math import sqrt, sin, cos, pi
from assets.model_data import vertices, faces, uv_map


import cv2
import mediapipe as mp
import numpy as np

# You can't normalize inline so this is a helper function
def normalized(*args):
    myVec = LVector3(*args)
    myVec.normalize()
    return myVec

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
        #ambientLight = AmbientLight('ambientLight')
        #ambientLight.setColor((0.3, 0.3, 0.3, 1))
        #ambientLightNP = self.render.attachNewNode(ambientLight)
        #self.render.setLight(ambientLightNP)


        
        # Light
        light = Spotlight('light')
        light.setShadowCaster(True, 512, 512)
        lens = PerspectiveLens()
        light.setLens(lens)
        light_np = self.render.attachNewNode(light)
        light_np.set_pos(0, 2, -20)
        light_np.look_at(0, 0, 0)
        # Model-light interaction
        self.render.setLight(light_np)

        #adjust render settings
        self.render.setShaderAuto()

        # Create the geometry
        self.geom_node = self.create_geom()
        self.face_model_np = NodePath(self.geom_node)
        self.face_model_np.setColor(0,0,1,1,1)

        #update rendering settings
        self.face_model_np.setDepthOffset(1)
        self.face_model_np.reparent_to(self.render)



        #udate texture settings
        self.face_model_np.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
        self.face_model_np.setTexProjector(TextureStage.getDefault(), self.render, self.face_model_np)

        #load texture
        model_texture = self.loader.loadTexture("img/example_texture.jpg")
        self.face_model_np.setTexture(model_texture)


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
        self.not_processing = False
   
    def open_camera(self):
        self.live_cam = cv2.VideoCapture(0)
        print("Waiting for camera to open")
        while(not self.live_cam.isOpened()):
            pass
        print("Camera on")

    def print_camera(self):
        x = self.face_landmarks[4].x
        y = self.face_landmarks[4].y
        z = self.face_landmarks[4].z

        #print(self.average_x)
        #print(self.average_y)
        #print(self.average_z)
        #print(x-0.5,y,z)
        print(np.degrees(self.refernce_yaw_angle), np.degrees(self.refernce_pitch_angle))
        
        #print(self.average_x, self.average_y, self.average_z)
        #print(self.render.getTransform(self.face_model_np))


    def create_geom(self):
        
        #bpy.ops.mesh.primitive_cube_add()
        vertex_format = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData('face_vertex_data', vertex_format, Geom.UHDynamic)
        vdata.setNumRows(len(vertices))

        #create vertex writer and add vertices
        vertex_writer = GeomVertexWriter(vdata, 'vertex')
        normal_writer = GeomVertexWriter(vdata, 'normal')

        #texcoord_writer = GeomVertexWriter(vdata, 'texcoord')
        for i in range(len(vertices)):
            vertex_writer.addData3(*vertices[i])
            x = vertices[i][0]
            y = vertices[i][1]
            z = vertices[i][2]
            normal_writer.addData3(normalized(2 * x - 1, 2 * y - 1, 2 * z - 1))

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
            if(not self.not_processing):
                print("unable to process")
                self.not_processing = True

            return task.cont

        self.not_processing = False
            
        self.face_landmarks = results.multi_face_landmarks[0].landmark

        vertex_writer = GeomVertexWriter(self.vdata, 'vertex')
        normal_writer = GeomVertexWriter(self.vdata, 'normal')


        landmark_x = np.array([])
        landmark_y = np.array([])
        landmark_z = np.array([])
        for landmark in self.face_landmarks:
            landmark_x = np.append(landmark_x, landmark.x)
            landmark_y = np.append(landmark_y, landmark.y)
            landmark_z = np.append(landmark_z, landmark.z)


        #rotate first


        #center locations in 3d space
        self.average_x = np.mean(landmark_x)
        self.average_y = np.mean(landmark_y)
        self.average_z = np.mean(landmark_z)

        centered_pos_x = landmark_x - self.average_x  
        centered_pos_y = landmark_y - self.average_y
        centered_pos_z = landmark_z - self.average_z


        refernce_noose = {"x":centered_pos_x[4], "y":centered_pos_y[4], "z":centered_pos_z[4]}
        self.refernce_yaw_angle = np.arctan(refernce_noose["x"]/refernce_noose["z"])
        self.refernce_pitch_angle = np.arctan(refernce_noose["y"]/refernce_noose["z"])
        
        
        yaw_centered_x = np.multiply(centered_pos_x, np.cos(self.refernce_yaw_angle)) - np.multiply(centered_pos_z, np.sin(self.refernce_yaw_angle))
        yaw_centered_y = centered_pos_y
        yaw_centered_z = np.multiply(centered_pos_z, np.cos(self.refernce_yaw_angle)) + np.multiply(centered_pos_x, np.sin(self.refernce_yaw_angle))

        #pitch_centered_x = yaw_centered_x
        #pitch_centered_y = np.multiply(yaw_centered_y, np.cos(self.refernce_pitch_angle)) + np.multiply(yaw_centered_z, np.sin(self.refernce_pitch_angle))
        #pitch_centered_z = np.multiply(yaw_centered_z, np.cos(self.refernce_pitch_angle)) - np.multiply(yaw_centered_y, np.sin(self.refernce_pitch_angle))

        
        for i in range(len(vertices)):

            x = centered_pos_x[i]
            y = centered_pos_y[i]
            z = centered_pos_z[i]
            vertex_writer.addData3(x, y, z)
            normal_writer.addData3(normalized(2 * x - 1, 2 * y - 1, 2 * z - 1))


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

        self.face_model_np.setHpr(self.yaw,self.pitch,0)

demo = BrownianBlender()
demo.run()