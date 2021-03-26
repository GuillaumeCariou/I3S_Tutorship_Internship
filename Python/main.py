from os import path
import sys
import metavision_designer_engine as mvd_engine
from metavision_designer_engine import Controller, KeyboardEvent
import metavision_designer_cv as mvd_cv
import metavision_designer_core as mvd_core
import metavision_hal as mv_hal
import cv2
from Line_Following import line
import time

from Python.EventProcessor import EventProcessor

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
    is_dat = input_filename.endswith('.dat')

    if not (is_raw or is_dat):
        print("Error: provided input path '{}' does not have the right extension. ".format(input_filename) +
              "It has either to be a .raw or a .dat file")
        sys.exit(1)

    controller = mvd_engine.Controller()

    if is_dat:
        cd_producer = mvd_core.FileProducer(input_filename)
    else:
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

# ActivityNoiseFilter configuration
time_window_length = 1500  # duration in us
cd_filtered = mvd_cv.ActivityNoiseFilter(cd_producer, time_window_length)
controller.add_component(cd_filtered, "Noise filter")
filtered_frame_gen = mvd_core.FrameGenerator(cd_filtered)
controller.add_component(filtered_frame_gen, "Filtered frame generator")

# Create Frame Generator with 20ms accumulation time
frame_gen = mvd_core.FrameGenerator(cd_producer)
frame_gen.set_dt(20000)
controller.add_component(frame_gen, "FrameGenerator")

# Get the sensor size.
geometry = device.get_i_geometry()
width = geometry.get_width()
height = geometry.get_height()

# We use PythonConsumer to "grab" the output of two components: cd_producer and frame_gen
# pyconsumer will callback the application each time it receives data, using the event_callback function
frame_gen_name = "FrameGen"
cd_prod_name = "CDProd"
ev_proc = EventProcessor(event_gen_name=cd_prod_name, frame_gen_name=frame_gen_name, width=width, height=height,
                         display_callback=True, make_matrix=False)

pyconsumer = mvd_core.PythonConsumer(ev_proc.event_callback)
pyconsumer.add_source(cd_filtered, cd_prod_name)  # filtered (cd_filtered) or not filtered (cd_producer)
pyconsumer.add_source(filtered_frame_gen, frame_gen_name) # filtered (filtered_frame_gen) or not filtered (frame_gen)
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


hist_size = input("Quelle taille d'historique voulez vous ?  > 0 ")
angle_hist = line.Historique(hist_size=int(hist_size))

compteur = 0
ips = 0
after = time.time() + 1

img_array = []

# Run pipeline & print execution statistics
while not controller.is_done():

    controller.run(do_sync)

    # Render frame
    frame = ev_proc.draw_frame()

    ips, compteur, after = line.caclulate_ips(ips, compteur, after)

    # https://stackoverflow.com/questions/55128386/python-opencv-depth-of-image-unsupported-cv-64f
    angle, size, img_line_plus_mean, did_not_find_lines = line.line_detection(original_picture=frame.astype('uint8') * 255,
                                                                              hist=angle_hist, ips=ips, display_image=False, display_mean=True)
    img_array.append(img_line_plus_mean)

    # Get the last key pressed
    last_key = controller.get_last_key_pressed()

    # Exit program if requested
    if last_key == ord('q') or last_key == KeyboardEvent.Symbol.Escape:
        break

cv2.destroyAllWindows()


# Save video
output_file_name = "cable_line_event2_filtered"
want_to_save_video = input("Voulez vous sauvegarder la video ? ")
if want_to_save_video == "Y" or want_to_save_video == "y":
    size = (0, 0)

    fps = 25
    out = cv2.VideoWriter(output_file_name + '.avi', cv2.VideoWriter_fourcc(*'XVID'), fps, size)
    print("==================Write Image to Disk==================")
    for i in range(len(img_array)):
        out.write(img_array[i])
        cv2.imshow('frame', img_array[i])
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    out.release()

