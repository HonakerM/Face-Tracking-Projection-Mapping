import cv2
import mediapipe as mp
import numpy as np
import bpy
from mathutils import Euler
from math import sin, cos, pi
import colorsys
TAU = 2*pi

mp_face_mesh = mp.solutions.face_mesh

edges = mp_face_mesh.FACEMESH_TESSELATION
edges = edges.union(mp_face_mesh.FACEMESH_CONTOURS)
edges = edges.union(mp_face_mesh.FACEMESH_IRISES)

def rainbow_lights(r=5, n=100, freq=2, energy=100):
    for i in range(n):
        t = float(i)/float(n)
        pos = (r*sin(TAU*t), r*cos(TAU*t), r*sin(freq*TAU*t))

        # Create lamp
        bpy.ops.object.add(type='LIGHT', location=pos)
        obj = bpy.context.object
        obj.data.type = 'POINT'

        # Apply gamma correction for Blender
        color = tuple(pow(c, 2.2) for c in colorsys.hsv_to_rgb(t, 0.6, 1))

        # Set HSV color and lamp energy
        obj.data.color = color
        obj.data.energy = energy

# Remove all elements
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# Set cursor to (0, 0, 0)
bpy.context.scene.cursor.location = (0, 0, 0)

# Create camera
bpy.ops.object.add(type='CAMERA', location=(0, -3.0, 0))
camera = bpy.context.object
camera.data.lens = 35
camera.rotation_euler = Euler((pi/2, 0, 0), 'XYZ')

# Make this the current camera
bpy.context.scene.camera = camera

#create mesh
bpy.ops.object.add(type='MESH', enter_editmode=False, location=(0,0,0))
o = bpy.context.object
o.name = 'myobject'

# Add Glossy BSDF material
mat = bpy.data.materials.new('Material')
o.data.materials.append(mat)

# Create lamps
rainbow_lights(5, 100, 2, energy=100)

with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image = cv2.imread("img/example_face.jpg")
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image)

    # Draw the face mesh annotations on the image.
    #image.flags.writeable = True
    #image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    #

    if(results.multi_face_landmarks):
        face_landmarks = results.multi_face_landmarks[0]

        #face_mesh_array = np.array([[[res.x, res.y, res.z]] for res in face_landmarks.landmark]).flatten() 
        temp_arr =[]
        for res in face_landmarks.landmark:
            temp_arr.append([res.x, res.y, res.z])

        face_mesh_array = np.ndarray.tolist(np.array(temp_arr))
        edges = list(edges)
       

        o.data.from_pydata(face_mesh_array,edges,[])
        o.data.update()

        # Render image
        scene = bpy.context.scene
        scene.render.resolution_x = 512
        scene.render.resolution_y = 512
        scene.render.resolution_percentage = 100
        scene.render.engine = 'CYCLES'
        #scene.render.engine = 'BLENDER_EEVEE'
        scene.render.filepath = './results/image.png'
        bpy.ops.render.render(write_still=True)        