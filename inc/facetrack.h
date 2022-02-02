
#ifndef FACETRACK_H
#define FACETRACK_H

// standard
#include "common.h"

//opencv includes
#include <opencv2/opencv.hpp> //general opencv
#include <opencv2/dnn.hpp> //nueral network
#include <opencv2/videoio.hpp> // opencv video

//model configuration
#ifndef FT_CONFIDENCE_THRESHOLD
#define FT_CONFIDENCE_THRESHOLD 0.5
#endif

#ifndef FT_SCALE_FACTOR
#define FT_SCALE_FACTOR 0.5
#endif


#ifndef FT_MODEL_MEAN_VALUES
#define FT_MODEL_MEAN_VALUES {104., 177.0, 123.0}
#endif

class FaceTrack {
public:
	FaceTrack(uint width, uint height);

	uint detect_face(const cv::Mat& frame);

private:
	/// Face detection network
	cv::dnn::Net network;

	const uint image_width;
	const uint image_height;
};

#endif
