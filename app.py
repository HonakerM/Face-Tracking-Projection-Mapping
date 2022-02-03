import cv2
import mediapipe as mp
import numpy as np
import open3d as o3d
import open3d.visualization.rendering as rendering

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh


drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
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

        face_mesh_array = np.array(temp_arr)
        mesh_x = face_mesh_array[:,0]
        mesh_y = face_mesh_array[:,1]
        mesh_z = face_mesh_array[:,2]

        # Pass xyz to Open3D.o3d.geometry.PointCloud and visualize
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(face_mesh_array)

        for val in range(0, 100):
            alpha = val/100
            print("alpha value:", alpha)
            mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha)
            '''
            pcd.estimate_normals()
                                                                
            radii = [0.05]
            mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd, o3d.utility.DoubleVector(radii))
            '''

            #o3d.io.write_point_cloud("results/sync.ply", pcd)
            mesh.compute_vertex_normals()
            o3d.visualization.draw_geometries([mesh], mesh_show_back_face=True)

        #img = o3d.geometry.Image((face_mesh_z_norm * 255).astype(np.uint8))
        #o3d.io.write_image("results/sync.png", img)
        #o3d.visualization.draw_geometries([img])
        #    
        ## Flip the image horizontally for a selfie-view display.
        #cv2.imshow('MediaPipe Face Mesh', cv2.flip(image, 1))
        #cv2.waitKey(5)

