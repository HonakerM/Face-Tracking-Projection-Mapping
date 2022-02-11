import mediapipe as mp


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh


drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
import pygame
import pygame.camera
from pygame.locals import *
import numpy as np
import cv2

pygame.init()
pygame.camera.init()

camlist = pygame.camera.list_cameras()
if camlist:
    cam = pygame.camera.Camera(camlist[0],(640,480), "RGB")
    cam.start()
else:
    print("no camera")
    exit(1)


with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:
    while True:
        if(not cam.query_image()):
            print("Ignoring empty camera frame.")
            continue        

        raw_image = cam.get_image()
        image = pygame.surfarray.array3d(raw_image)

        # To improve performance, optionally mark the image as not writeable to
        results = face_mesh.process(image)

        # Draw the face mesh annotations on the image.
        if(results.multi_face_landmarks):
            face_landmarks = results.multi_face_landmarks[0]
            mp_drawing.draw_landmarks(
            #debug langmarks
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles
                .get_default_face_mesh_tesselation_style())
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles
                .get_default_face_mesh_contours_style())
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_IRISES,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles
                .get_default_face_mesh_iris_connections_style())
                
            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('MediaPipe Face Mesh', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                break