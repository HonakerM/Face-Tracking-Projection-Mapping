#include "test.h"
#include <opencv2/dnn.hpp>
#include <opencv2/opencv.hpp>

int opencv_inc_test(std::string filename)
{

    cv::Mat image;
    image = cv::imread(filename, 1 );
    if ( !image.data )
    {
        printf("No image data \n");
        return -1;
    }
    cv::namedWindow("Display Image", cv::WINDOW_AUTOSIZE );
    cv::imshow("Display Image", image);
    cv::waitKey(0);
    return 0;
}