
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Geom, GeomNode, GeomVertexFormat, \
    GeomVertexData, GeomTriangles, GeomVertexWriter, GeomVertexReader
from panda3d.core import NodePath
from panda3d.core import PointLight
from panda3d.core import VBase4, Vec3
from direct.task import Task
import sys
import random
from math import sqrt
from model_data import vertices, faces


import cv2
import mediapipe as mp

class BrownianBlender(ShowBase):
    def __init__(self):
        # Basics
        ShowBase.__init__(self)
        base.disableMouse()
        base.setFrameRateMeter(True)
        self.accept("escape", sys.exit)
        self.camera.set_pos(0.3759736716747284, 0.499371200799942, -1.889259696006775)
        self.camera.setHpr(-16.5869, 82.7357, 30.1287)
        # A light
        plight = PointLight('plight')
        print(plight.setShadowCaster(True, 4096, 4096))
        plight.setColor(VBase4(0.5, 0.5, 0.5, 1))
        plnp = self.render.attachNewNode(plight)
        plnp.setPos(5, 5, 5)
        plnp.look_at(0.3759736716747284, 0.499371200799942, -1.889259696006775)
        self.render.setLight(plnp)
        self.render.setShaderAuto()

        # Create the geometry
        geom = self.create_geom()
        np = NodePath(geom)
        np.reparent_to(self.render)

        self.accept("space", self.print_camera, [])



        #create mediapipe
        self.face_mesh_processor =  mp.solutions.face_mesh.FaceMesh( max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)

        #create video capture
        self.live_cam = cv2.VideoCapture(0)
        print("Waiting for camera to open")
        while(not self.live_cam.isOpened()):
            pass
        print("Camera on")


        # Start the task to interpolate the geometry each frame
        self.taskMgr.add(self.regen_face, 'generate_new_vertecies', sort = 5)
        #self.need_to_swap_maps = True
        #self.taskMgr.add(self.swap_maps, 'swap_geometry', sort = 5)
        #self.taskMgr.add(self.interpolate_maps, 'interpolate_geometry', sort = 10)


        
   
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
            return
        
        success, image = self.live_cam.read()
        if(not success):
            return

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh_processor.process(image)

        if(not results.multi_face_landmarks):
            return
            
        face_landmarks = results.multi_face_landmarks[0].landmark

        vertex_writer = GeomVertexWriter(self.vdata, 'vertex')

        for landmark in face_landmarks:
            vertex_writer.setData3f(landmark.x, landmark.y, landmark.z)

        return task.cont

demo = BrownianBlender()
demo.run()