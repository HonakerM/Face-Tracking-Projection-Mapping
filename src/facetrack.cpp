#include "facetrack.h"



FaceTrack::FaceTrack(uint width, uint height) : image_width(width), image_height(height) {
	network = cv::dnn::readNetFromCaffe(FACE_DETECTION_CONFIGURATION, FACE_DETECTION_WEIGHTS);
}


uint FaceTrack::detect_face(const cv::Mat& frame) {
    cv::Mat input_blob = cv::dnn::blobFromImage(frame, FT_SCALE_FACTOR, cv::Size(image_width, image_height),
        FT_MODEL_MEAN_VALUES, false, false);

    network.setInput(input_blob, "data");
    cv::Mat detection = network.forward("detection_out");
    cv::Mat detection_matrix(detection.size[2], detection.size[3], CV_32F, detection.ptr<float>());

    uint num_of_faces=0;
    for (int i = 0; i < detection_matrix.rows; i++) {
        float confidence = detection_matrix.at<float>(i, 2);

        if (confidence < FT_CONFIDENCE_THRESHOLD) {
            continue;
        }

        num_of_faces++;
    }
    return num_of_faces;
}
