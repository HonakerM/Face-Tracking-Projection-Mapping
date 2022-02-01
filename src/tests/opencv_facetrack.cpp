#include "opencv_util.h"


std::vector<cv::Rect> detect_face_rectangles(const cv::Mat &frame);

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

FaceDetector::FaceDetector() :
    confidence_threshold_(0.5), 
    input_image_height_(300), 
    input_image_width_(300),
    scale_factor_(1.0),
    mean_values_({104., 177.0, 123.0}) {
        // Note: The variables MODEL_CONFIGURATION_FILE
        // and MODEL_WEIGHTS_FILE are passed in via cmake
        network_ = cv::dnn::readNetFromCaffe(FACE_DETECTION_CONFIGURATION,
                FACE_DETECTION_WEIGHTS);

    if (network_.empty()) {
        std::ostringstream ss;
        ss << "Failed to load network with the following settings:\n"
           << "Configuration: " + std::string(FACE_DETECTION_CONFIGURATION) + "\n"
           << "Binary: " + std::string(FACE_DETECTION_WEIGHTS) + "\n";
        throw std::invalid_argument(ss.str());
    }


int main(int argc, char **argv) {

    if ( argc != 2 )
    {
        printf("usage: FaceTrackImg <Image_Path>\n");
        return -1;
    }
    cv::Mat image;
    image = cv::imread( argv[1], 1 );

    return 0;
}