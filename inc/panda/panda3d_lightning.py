
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Geom, GeomNode, GeomVertexFormat, \
    GeomVertexData, GeomTriangles, GeomVertexWriter, GeomVertexReader, TextureStage, TexGenAttrib
from panda3d.core import NodePath, Spotlight
from panda3d.core import AmbientLight, PointLight, DirectionalLight, PerspectiveLens
from panda3d.core import VBase4, Vec3, Vec4, LVector3
from direct.task import Task
import sys
import random
from math import sqrt, sin, cos, pi

#to large to be included
from model_data import vertices, faces

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
        self.render.setShaderAuto()
        #self.render.setTwoSided(True)

        self.accept("escape", sys.exit)


        # Create the geometry
        self.geom_node = self.create_geom()
        self.face_model_np = NodePath(self.geom_node)

        #update rendering settings
        self.face_model_np.setDepthOffset(1)
        self.face_model_np.reparent_to(self.render)

        # ambient light
        #alight = AmbientLight('alight')
        #alight.setColor((0.2, 0.2, 0.2, 0.1))
        #alnp = self.render.attachNewNode(alight)
        #self.render.setLight(alnp)

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
        

        self.camera.set_pos(0, 0, -2)
        self.camera.look_at(0,0,0)


    def create_geom(self):
        
        #bpy.ops.mesh.primitive_cube_add()
        vertex_format = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData('face_vertex_data', vertex_format, Geom.UHDynamic)
        vdata.setNumRows(len(vertices))

        #create vertex writer and add vertices
        vertex_writer = GeomVertexWriter(vdata, 'vertex')
        normal_writer = GeomVertexWriter(vdata, 'normal')

        landmark_x = np.array([])
        landmark_y = np.array([])
        landmark_z = np.array([])
        for landmark in vertices:
            landmark_x = np.append(landmark_x, landmark[0])
            landmark_y = np.append(landmark_y, landmark[1])
            landmark_z = np.append(landmark_z, landmark[2])


        #center locations in 3d space
        self.average_x = np.mean(landmark_x)
        self.average_y = np.mean(landmark_y)
        self.average_z = np.mean(landmark_z)

        centered_pos_x = landmark_x - self.average_x  
        centered_pos_y = landmark_y - self.average_y
        centered_pos_z = landmark_z - self.average_z

        for i in range(len(vertices)):
            x = centered_pos_x[i]
            y = centered_pos_y[i]
            z = centered_pos_z[i]
            vertex_writer.addData3(x, y, z)
            normal_writer.addData3(normalized(2 * x - 1, 2 * y - 1, 2 * z - 1))

        #    texcoord_writer.addData2(*uv_map[i])

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
        
        self.vdata = vdata
        
        return node

   
demo = BrownianBlender()
demo.run()