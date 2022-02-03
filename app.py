import cv2
import mediapipe as mp
import numpy as np
import open3d as o3d
import open3d.visualization.rendering as rendering
import pyvirtualcam
import numpy as np


#define and configure mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

face_mesh_precessor = mp_face_mesh.FaceMesh(max_num_faces=1,refine_landmarks=True,min_detection_confidence=0.5,min_tracking_confidence=0.5)

#start opencv video campture
cap = cv2.VideoCapture(0)
while(cap.isOpened()):
        
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

        face_mesh_array = np.array(temp_arr)
        mesh_x = face_mesh_array[:,0]
        mesh_y = face_mesh_array[:,1]
        mesh_z = face_mesh_array[:,2]

        # Pass xyz to Open3D.o3d.geometry.PointCloud and visualize
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(face_mesh_array)

#        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha)
        
        pcd.estimate_normals()
        #pcd.orient_normals_consistent_tangent_plane(100)
        pcd.orient_normals_to_align_with_direction([0,0,-1])

        #normals are generated in the wrong direction
        normals = np.asarray(pcd.normals)
        print(normals)
        # flip normals
        pcd.normals = o3d.utility.Vector3dVector(normals)


        #o3d.visualization.draw_geometries([pcd], point_show_normal=True)      

        # estimate radius for rolling ball
        radii = [0.025, 0.05]
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd, o3d.utility.DoubleVector(radii))
            

        #o3d.io.write_point_cloud("results/sync.ply", pcd)
        mesh.compute_vertex_normals()
        

        #o3d.visualization.draw_geometries([mesh], mesh_show_back_face=True)

        mesh_refined = mesh
        #mesh_refined = mesh.filter_smooth_simple(number_of_iterations=1)

        text_image = cv2.imread("img/example_texture.jpg")
        mesh_refined.textures=[o3d.geometry.Image(text_image)]
        mesh_refined.triangle_material_ids = o3d.utility.IntVector([0]*len(faces))

        o3d.visualization.draw_geometries([mesh_refined], mesh_show_back_face=False)

        # Create a renderer with the desired image size
        img_width = 640
        img_height = 480
        render = o3d.visualization.rendering.OffscreenRenderer(img_width, img_height)

        # Pick a background colour (default is light gray)

        # Define a simple unlit Material.
        # (The base color does not replace the arrows' own colors.)
        mtl = o3d.visualization.rendering.MaterialRecord()
        mtl.base_color = [1.0, 1.0, 1.0, 1.0]  # RGBA
        mtl.shader = "defaultUnlit"

        render.scene.add_geometry("MyMeshModel", mesh_refined, mtl)

        ## Optionally set the camera field of view (to zoom in a bit)
        #vertical_field_of_view = 15.0  # between 5 and 90 degrees
        #aspect_ratio = img_width / img_height  # azimuth over elevation
        #near_plane = 0.1
        #far_plane = 50.0
        #fov_type = o3d.visualization.rendering.Camera.FovType.Vertical
        #render.scene.camera.set_projection(vertical_field_of_view, aspect_ratio, near_plane, far_plane, fov_type)

        # Look at the origin from the front (along the -Z direction, into the screen), with Y as Up.
        center = [0, 0, 0]  # look_at target
        eye = [0, 0, 1]  # camera position
        up = [0, 1, 0]  # camera orientation
        render.scene.camera.look_at(center, eye, up)

        img_o3d = render.render_to_image()
        
        # Display the image in a separate window
        # (Note: OpenCV expects the color in BGR format, so swop red and blue.)
        img_cv2 = cv2.cvtColor(np.array(img_o3d), cv2.COLOR_RGBA2BGRA)
        #cv2.imshow("Preview window", img_cv2)
        cv2.waitKey()

