#include "opencv_util.h"
#include <sstream>
#include <vector>
#include <string>
#include <opencv2/dnn.hpp>


class FaceDetector {
public:
    explicit FaceDetector();

/// Detect faces in an image frame
/// \param frame Image to detect faces in
/// \return Vector of detected faces
    std::vector<cv::Rect> detect_face_rectangles(const cv::Mat &frame);

private:
    /// Face detection network
    cv::dnn::Net network_;
    /// Input image width
    const int input_image_width_;
    /// Input image height
    const int input_image_height_;
    /// Scale factor when creating image blob
    const double scale_factor_;
    /// Mean normalization values network was trained with
    const cv::Scalar mean_values_;
    /// Face detection confidence threshold
    const float confidence_threshold_;

};

FaceDetector::FaceDetector() : confidence_threshold_(0.5), input_image_height_(300), input_image_width_(300),
                               scale_factor_(1.0), mean_values_({104., 177.0, 123.0}) {

// Note: The varibles MODEL_CONFIGURATION_FILE and MODEL_WEIGHTS_FILE are passed in via cmake
    network_ = cv::dnn::readNetFromCaffe(FACE_DETECTION_CONFIGURATION, FACE_DETECTION_WEIGHTS);

    if (network_.empty()) {
        std::ostringstream ss;
        ss << "Failed to load network with the following settings:\n"
           << "Configuration: " + std::string(FACE_DETECTION_CONFIGURATION) + "\n"
           << "Binary: " + std::string(FACE_DETECTION_WEIGHTS) + "\n";
        throw std::invalid_argument(ss.str());
    }
}

std::vector<cv::Rect> FaceDetector::detect_face_rectangles(const cv::Mat &frame) {
    cv::Mat input_blob = cv::dnn::blobFromImage(frame, scale_factor_, cv::Size(input_image_width_, input_image_height_),
                                                mean_values_, false, false);
    network_.setInput(input_blob, "data");
    cv::Mat detection = network_.forward("detection_out");
    cv::Mat detection_matrix(detection.size[2], detection.size[3], CV_32F, detection.ptr<float>());

    std::vector<cv::Rect> faces;

    for (int i = 0; i < detection_matrix.rows; i++) {
        float confidence = detection_matrix.at<float>(i, 2);

        if (confidence < confidence_threshold_) {
            continue;
        }
        int x_left_bottom = static_cast<int>(detection_matrix.at<float>(i, 3) * frame.cols);
        int y_left_bottom = static_cast<int>(detection_matrix.at<float>(i, 4) * frame.rows);
        int x_right_top = static_cast<int>(detection_matrix.at<float>(i, 5) * frame.cols);
        int y_right_top = static_cast<int>(detection_matrix.at<float>(i, 6) * frame.rows);

        faces.emplace_back(x_left_bottom, y_left_bottom, (x_right_top - x_left_bottom), (y_right_top - y_left_bottom));
    }

    return faces;
}

int main(int argc, char **argv) {

 cv::VideoCapture video_capture;
    if (!video_capture.open(0)) {
        return 0;
    }

    FaceDetector face_detector;

    cv::Mat frame;
    while (true) {
        video_capture >> frame;

        auto rectangles = face_detector.detect_face_rectangles(frame);
        cv::Scalar color(0, 105, 205);
        int frame_thickness = 4;
        for(const auto & r : rectangles){
            cv::rectangle(frame, r, color, frame_thickness);
        }
        imshow("Image", frame);
        const int esc_key = 27;
        if (cv::waitKey(10) == esc_key) {
            break;
        }
    }

    cv::destroyAllWindows();
    video_capture.release();

    return 0;
}