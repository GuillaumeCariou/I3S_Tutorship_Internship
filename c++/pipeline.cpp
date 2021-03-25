#include <iostream>
#include <mutex>
#include <condition_variable>
#include <set>
#include <boost/program_options.hpp>
#include <metavision/sdk/base/utils/log.h>
#include <metavision/sdk/analytics/configs/tracking_algorithm_config.h>
#include <metavision/sdk/analytics/algorithms/tracking_algorithm.h>
#include <metavision/sdk/analytics/utils/events_frame_generator_algorithm.h>
#include <metavision/sdk/analytics/utils/tracking_drawing.h>
#include <metavision/sdk/core/utils/simple_displayer.h>
#include <metavision/sdk/cv/algorithms/activity_filter_algorithm.h>
#include <metavision/sdk/cv/algorithms/spatio_temporal_contrast_algorithm.h>
#include <metavision/sdk/driver/camera.h>


int main(int argc, char *argv[]) {
    std::string in_raw_file_path;

    const std::string short_program_desc("Code sample showing how the pipeline framework can be used to "
                                         "create a simple application to filter and display events.\n");

    const std::string long_program_desc(short_program_desc + "Available keyboard options:\n"
                                                             "  - r - toggle the ROI filter algorithm\n"
                                                             "  - p - show only events of positive polarity\n"
                                                             "  - n - show only events of negative polarity\n"
                                                             "  - a - show all events\n"
                                                             "  - q - quit the application\n");

    po::options_description options_desc("Options");
    // clang-format off
    options_desc.add_options()
        ("help,h", "Produce help message.")
        ("input-raw-file,i", po::value<std::string>(&in_raw_file_path), "Path to input RAW file. If not specified, the camera live stream is used.")
        ;
    // clang-format on

    po::variables_map vm;
    try {
        po::store(po::command_line_parser(argc, argv).options(options_desc).run(), vm);
        po::notify(vm);
    } catch (po::error &e) {
        MV_LOG_ERROR() << short_program_desc;
        MV_LOG_ERROR() << options_desc;
        MV_LOG_ERROR() << "Parsing error:" << e.what();
        return 1;
    }

    if (vm.count("help")) {
        MV_LOG_INFO() << short_program_desc;
        MV_LOG_INFO() << options_desc;
        return 0;
    }

    MV_LOG_INFO() << long_program_desc;

    // A pipeline for which all added stages will automatically be run in their own processing threads (if applicable)
    Metavision::Pipeline p(true);

    // Construct a camera from a recording or a live stream
    Metavision::Camera cam;
    if (!in_raw_file_path.empty()) {
        cam = Metavision::Camera::from_file(in_raw_file_path);
    } else {
        cam = Metavision::Camera::from_first_available();
    }
    const unsigned short width  = cam.geometry().width();
    const unsigned short height = cam.geometry().height();

    /// Pipeline
    //
    //  0 (Camera) -->-- 1 (ROI) -->-- 2 (Polarity) -->-- 3 (Frame Generation) -->-- 4 (Display)
    //

    // 0) Stage producing events from a camera
    auto &cam_stage = p.add_stage(std::make_unique<Metavision::CameraStage>(std::move(cam)));

    // 1) Stage wrapping an ROI filter algorithm
    auto &roi_stage = p.add_algorithm_stage(
        std::make_unique<Metavision::RoiFilterAlgorithm>(80, 80, width - 80, height - 80, false), cam_stage, false);

    // 2) Stage wrapping a polarity filter algorithm
    auto &pol_stage = p.add_algorithm_stage(std::make_unique<Metavision::PolarityFilterAlgorithm>(0), roi_stage, false);

    // 3) Stage generating a frame from filtered events
    auto &frame_stage = p.add_stage(std::make_unique<Metavision::FrameGenerationStage>(width, height, 30), pol_stage);

    // 4) Stage displaying the frame
    auto &disp_stage = p.add_stage(std::make_unique<Metavision::FrameDisplayStage>("CD events"), frame_stage);

    // Run the pipeline step by step to allow user interaction based on key pressed
    while (p.step()) {
        char last_key = disp_stage.get_last_key();
        switch (last_key) {
        case 'a':
            // show all events
            pol_stage.set_enabled(false);
            break;
        case 'n':
            // show only negative events
            pol_stage.set_enabled(true);
            pol_stage.algo().set_polarity(0);
            break;
        case 'p':
            // show only positive events
            pol_stage.set_enabled(true);
            pol_stage.algo().set_polarity(1);
            break;
        case 'r':
            // toggle ROI filter
            roi_stage.set_enabled(!roi_stage.is_enabled());
            break;
        }
    }

    return 0;
}
