from os import path
import sys
import metavision_designer_engine as mvd_engine
from metavision_designer_engine import Controller, KeyboardEvent
import metavision_designer_cv as mvd_cv
import metavision_designer_core as mvd_core
import metavision_hal as mv_hal
import cv2
from Python.Event_Processor.EventProcessor import EventProcessor
from Python.Foveation import Foveation
from Python.Log_Luminance import Log_Luminance
from metavision_designer_core import RoiFilter

input_filename = "./../../out_2021-03-25_17-33-13.raw"  # ne fonctionne pas avec ~/
# input_filename = "PATH_TO_RAW"

cam = input("Do you want to use cam ? Y or N ")

if cam == "Y" or cam == "y":
    from_file = False
    controller = Controller()

    device = mv_hal.DeviceDiscovery.open('')

    # Add the device interface to the pipeline
    interface = mvd_core.HalDeviceInterface(device)
    controller.add_device_interface(interface)

    cd_producer = mvd_core.CdProducer(interface)

else:
    # input_filename = input("File path from main ")
    from_file = True
    # Check validity of input arguments
    if not (path.exists(input_filename) and path.isfile(input_filename)):
        print("Error: provided input path '{}' does not exist or is not a file.".format(input_filename))
        sys.exit(1)

    is_raw = input_filename.endswith('.raw')

    if not is_raw:
        print("Error: provided input path '{}' does not have the right extension. ".format(input_filename) +
              "It has either to be a .raw or a .dat file")
        sys.exit(1)

    controller = mvd_engine.Controller()

    device = mv_hal.DeviceDiscovery.open_raw_file(input_filename)
    if not device:
        print("Error: could not open file '{}'.".format(input_filename))
        sys.exit(1)

    # Add the device interface to the pipeline
    interface = mvd_core.HalDeviceInterface(device)
    controller.add_device_interface(interface)

    cd_producer = mvd_core.CdProducer(interface)

    # Start the streaming of events
    i_events_stream = device.get_i_events_stream()
    i_events_stream.start()

# Add cd_producer to the pipeline
controller.add_component(cd_producer, "CD Producer")

# Get the sensor size.
geometry = device.get_i_geometry()
width = geometry.get_width()
height = geometry.get_height()
print("Sensor size width = {}   height = {}".format(width, height))

# resize
roi_width = int(100)
roi_height = int(100)
x0 = int(width / 2 - roi_width / 2)
y0 = int(height / 2 - roi_height / 2)
x1 = x0 + roi_width
y1 = y0 + roi_height
roi_filter = RoiFilter(cd_producer, x0, y0, x1, y1)
controller.add_component(roi_filter)
print("ROI size width = {}   height = {}".format(roi_width, roi_height))
print("Number of pixels = {}".format(roi_width * roi_height))

# ActivityNoiseFilter configuration
time_window_length = 1500  # duration in us plus c'est bas plus c'est filtré
cd_filtered = mvd_cv.ActivityNoiseFilter(roi_filter, time_window_length)
controller.add_component(cd_filtered, "Noise filter")
filtered_frame_gen = mvd_core.FrameGenerator(cd_filtered)
controller.add_component(filtered_frame_gen, "Filtered frame generator")

# Create Frame Generator with 20ms accumulation time
frame_gen = mvd_core.FrameGenerator(cd_filtered)
frame_gen.set_dt(20000)
controller.add_component(frame_gen, "FrameGenerator")

# We use PythonConsumer to "grab" the output of two components: cd_producer and frame_gen
# pyconsumer will callback the application each time it receives data, using the event_callback function
frame_gen_name = "FrameGen"
cd_prod_name = "CDProd"
ev_proc = EventProcessor(event_gen_name=cd_prod_name, frame_gen_name=frame_gen_name, width=width, height=height,
                         display_callback=False)

pyconsumer = mvd_core.PythonConsumer(ev_proc.event_callback)
pyconsumer.add_source(cd_filtered, cd_prod_name)  # filtered (cd_filtered) or not filtered (cd_producer)
pyconsumer.add_source(filtered_frame_gen, frame_gen_name)  # filtered (filtered_frame_gen) or not filtered (frame_gen)
controller.add_component(pyconsumer, "PythonConsumer")

controller.set_slice_duration(10000)
controller.set_batch_duration(50000)
do_sync = True if from_file else False

# Start the camera
if not from_file:
    simple_device = device.get_i_device_control()
    simple_device.start()

# Start the streaming of events
i_events_stream = device.get_i_events_stream()
i_events_stream.start()

#################################Parameters#################################
# on part du principe que l'image est carré
divide_matrix_by = 2
matrix_level_HQ = Log_Luminance.gen_matrix_PixelState(roi_width, roi_height)
matrix_level_LQ = Log_Luminance.gen_matrix_PixelState(int(roi_width / divide_matrix_by), int(roi_height / divide_matrix_by))



while not controller.is_done():
    controller.run(do_sync)

    # Render frame
    events = ev_proc.get_event()  # tableau d'event
    Log_Luminance.log_luminance(events, matrix_level_HQ, matrix_level_LQ, divide_matrix_by, (width, height), (roi_width, roi_height))


    # Get the last key pressed
    last_key = controller.get_last_key_pressed()

    # Exit program if requested
    if last_key == ord('q') or last_key == KeyboardEvent.Symbol.Escape:
        break

cv2.destroyAllWindows()
