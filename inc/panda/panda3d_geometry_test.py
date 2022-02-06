#!/usr/bin/env python

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Geom, GeomNode, GeomVertexFormat, \
    GeomVertexData, GeomTriangles, GeomVertexWriter, GeomVertexReader, Material

from direct.showbase.Loader import Loader
from panda3d.core import NodePath
from panda3d.core import PointLight
from panda3d.core import VBase4, Vec3
from direct.task import Task
import sys
import random
from math import sqrt, sin, cos, pi

class BrownianBlender(ShowBase):
    def __init__(self):
        # Basics
        ShowBase.__init__(self)
        #base.disableMouse()
        base.setFrameRateMeter(True)
        self.accept("escape", sys.exit)
        #self.camera.set_pos(0, -10, 0)
        #self.camera.look_at(0, 0, 0)
        # A light
        plight = PointLight('plight')
        plight.setColor(VBase4(0.5, 0.5, 0.5, 1))
        plnp = render.attachNewNode(plight)
        plnp.setPos(0, 5, 0)
        render.setLight(plnp)
        render.setShaderAuto()

        # Create the geometry
        #self.sidelength = 30
        #self.map_a = self.create_map(self.sidelength)
        #self.map_b = self.map_a
        geom = self.create_geom()
        np = NodePath(geom)
        np.setShaderAuto()
        NodePath.setHpr(np, 90)
        np.reparent_to(self.render)
        np.setColor(VBase4(0, 0, 1, 1))
        np.setTexture(self.loader.loadTexture("img/example_texture.jpg"))

        material = Material()
        material.setShininess(5) # Make this material shiny
        material.setAmbient((0, 0, 1, 0)) # Make this material blue

        np.setMaterial(material) # Apply the material to this nodePath

        # Start the task to interpolate the geometry each frame
        self.last_time = 0.0
        self.need_to_swap_maps = True

        self.angle = 0.0
        self.pitch = 0.0
        self.adjust_angle = 0
        self.adjust_pitch = 0
        self.last_time = 0.0
        # Initial camera setup
        #self.camera.set_pos(sin(self.angle)*20,-cos(self.angle)*20,0)
        #self.camera.look_at(0,0,0)
        ## Key events and camera movement task
        #self.accept("arrow_left", self.adjust_turning, [-1.0, 0.0])
        #self.accept("arrow_left-up", self.adjust_turning, [1.0, 0.0])
        #self.accept("arrow_right", self.adjust_turning, [1.0, 0.0])
        #self.accept("arrow_right-up", self.adjust_turning, [-1.0, 0.0])
        #self.accept("arrow_up", self.adjust_turning, [0.0, 1.0])
        #self.accept("arrow_up-up", self.adjust_turning, [0.0, -1.0])
        #self.accept("arrow_down", self.adjust_turning, [0.0, -1.0])
        #self.accept("arrow_down-up", self.adjust_turning, [0.0, 1.0])
        #self.accept("w", self.adjust_loc, ["forward",1])
        #self.accept("a", self.adjust_loc, ["left",1])
        #self.accept("s", self.adjust_loc, ["backward",1])
        #self.accept("d", self.adjust_loc, ["right",1])
        #self.accept("escape", sys.exit)
        #self.taskMgr.add(self.update_camera, 'adjust camera', sort = 10)
        

    def create_geom(self):
        from assets.model_data import vertices, faces
        
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

    def create_map(self, sidelength):
        map = {}
        for x in range(0, sidelength):
            for y in range(0, sidelength):
                v_x = (x - (float(sidelength) / 2.0)) / float(sidelength) * 5.0
                v_y = (y - (float(sidelength) / 2.0)) / float(sidelength) * 5.0
                v_z = random.random()
                map[(x,y)] = (v_x, v_y, v_z)
        return map


    def adjust_turning(self, heading, pitch):
        self.adjust_angle += heading
        self.adjust_pitch += pitch

    def adjust_loc(self, direction, speed):
        self.camera.set_pos(0, 0, 0)
        
    def update_camera(self, task):
        if task.time != 0.0:
            dt = task.time - self.last_time
            self.last_time = task.time
            self.angle += pi * dt * self.adjust_angle
            self.pitch += pi * dt * self.adjust_pitch
            # Why /2.001 and not an even 2.0? Because then we'd have to set_Hpr
            # explicitly, as look_at can't deduce the heading when the camera is
            # exactly above/below the spheres center.
            if self.pitch > pi/2.001:
                self.pitch = pi/2.001
            if self.pitch < -pi/2.001:
                self.pitch = -pi/2.001
            self.camera.set_pos(sin(self.angle)*cos(abs(self.pitch))*20,
                                -cos(self.angle)*cos(abs(self.pitch))*20,
                                sin(self.pitch)*20)
            self.camera.look_at(0,0,0)
        return Task.cont

demo = BrownianBlender()
demo.run()