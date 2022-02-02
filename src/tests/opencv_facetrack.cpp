#include "test.h"
#include "facetrack.h"


int opencv_facetrack_test() {
    cv::VideoCapture video_capture;
    if (!video_capture.open(0)) {
        return 0;
    }


    //uint width = video_capture.get(cv::CAP_PROP_FRAME_WIDTH);
    //uint height = video_capture.get(cv::CAP_PROP_FRAME_HEIGHT);

    FaceTrack face_tracker(300, 300);

    cv::Mat frame;
    uint frame_count = 0;
    while (true) {
        video_capture >> frame;

        uint num_rect = face_tracker.detect_face(frame);
        cv::Scalar color(0, 105, 205);
        int frame_thickness = 4;
        //for(const auto & r : rectangles){
        //    cv::rectangle(frame, r, color, frame_thickness);
        //}

        cv::imshow("Image", frame);
        const int esc_key = 27;
        if (cv::waitKey(1) == esc_key) {
            break;
        }
    }

    cv::destroyAllWindows();
    video_capture.release();

    return 0;
}