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
import serial
from Python.EventProcessor import EventProcessor
from metavision_designer_core import RoiFilter

# Elegoo
width = 640
height = 480
roi_width = int(width)
roi_height = int(height * 0.50)
power_forward = 100
power_sideway_minimal = 180
power_sideway_maximal = 225
left_begin = 0
left_end = int(roi_width/2)
right_begin = int(roi_width/2)
right_end = roi_width
compteur_did_not_find_lines = 0
imprimer_taille_image = True

middle_of_the_frame = int(width/2)


def power_engine_from_angle(x, y):
    if x < middle_of_the_frame:
        diff = x / middle_of_the_frame
    elif middle_of_the_frame < x:
        diff = (x - middle_of_the_frame) / middle_of_the_frame
    power = power_sideway_minimal + ((power_sideway_maximal - power_sideway_minimal) * diff)

    if power > 255:
        power = 255
    return int(power)


def send_command(left, right):
    try:
        cmd = str(left) + ',' + str(right) + ','
        arduino.write(cmd.encode())

        arduino.flushOutput()
        arduino.flushInput()
    except Exception as ex:
        print(ex)


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

x0 = 0
y0 = height - roi_height
roi_filter = RoiFilter(cd_producer, x0, y0, x0 + roi_width, y0 + roi_height)
controller.add_component(roi_filter)

polarity_filter = mvd_core.PolarityFilter(roi_filter, 0)
controller.add_component(polarity_filter, "Polarity filter")

# ActivityNoiseFilter configuration
time_window_length = 10000  # duration in us plus c'est bas plus c'est filtré
cd_filtered = mvd_cv.ActivityNoiseFilter(polarity_filter, time_window_length)
controller.add_component(cd_filtered, "Noise filter")
filtered_frame_gen = mvd_core.FrameGenerator(cd_filtered)
controller.add_component(filtered_frame_gen, "Filtered frame generator")

# Create Frame Generator with 20ms accumulation time
frame_gen = mvd_core.FrameGenerator(polarity_filter)
frame_gen.set_dt(20000)
controller.add_component(frame_gen, "FrameGenerator")

# Get the sensor size
geometry = device.get_i_geometry()
width = geometry.get_width()
height = geometry.get_height()

# We use PythonConsumer to "grab" the output of two components: cd_producer and frame_gen
# pyconsumer will callback the application each time it receives data, using the event_callback function
frame_gen_name = "FrameGen"
cd_prod_name = "CDProd"
ev_proc = EventProcessor(event_gen_name=cd_prod_name, frame_gen_name=frame_gen_name, width=width, height=height,
                         display_callback=False, make_matrix=False)

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

# Variable line detection
hist_size = input("Quelle taille d'historique voulez vous ?  > 0 ")
angle_hist = line.Historique(hist_size=int(hist_size))

compteur = 0
ips = 0
after = time.time() + 1

arduino = serial.Serial("/dev/ttyACM0", 9600, timeout=1)

suivi = input("Voulez vous le suivi de commande ? Y or N ")
if suivi == "Y" or suivi == "y":
    suivi = True
else:
    suivi = False

if arduino.isOpen():
    print("{} connected!".format(arduino.port))

    while not controller.is_done():
        controller.run(do_sync)
        frame = ev_proc.draw_frame()

        ips, compteur, after = line.calculate_ips(ips, compteur, after)
        angle, line_mean, size, img_line_plus_mean, did_not_find_lines = line.line_detection(
            original_picture=frame.astype('uint8') * 255,
            hist=angle_hist, ips=ips, display_image=False, display_mean=True)

        if imprimer_taille_image:
            print(size)
            imprimer_taille_image = False

        if did_not_find_lines:
            compteur_did_not_find_lines += 1
        else:
            compteur_did_not_find_lines = 0

        x, y = line_mean.get_line_coordinates()
        # Reaction to angle
        # Les moteur sont inversé
        # ENA, ENB
        if did_not_find_lines and compteur_did_not_find_lines > 10:
            commande = "Backward"
            send_command(10, 10)  # ceci est un code
            power = power_forward
        elif left_end > x >= left_begin:
            commande = "left"
            power = power_engine_from_angle(x, y)
            send_command(power, 0)  # Le robot tourna a droite peu efficace
        elif right_end >= x > right_begin:
            commande = "right"
            power = power_engine_from_angle(x, y)
            send_command(0, power)  # Le robot toune a gauche tres efficace
        elif right_begin >= x >= left_end:
            commande = "Forward"
            send_command(power_forward, power_forward)
            power = power_forward

        if suivi:
            print("Commande = " + commande + " " * (10 - len(commande)) + "   Angle = " + str(angle) + " " * (
                    10 - len(str(angle))) + "   Power_engine = " + str(power))

        last_key = controller.get_last_key_pressed()
        if last_key == ord('q') or last_key == KeyboardEvent.Symbol.Escape:
            break

cv2.destroyAllWindows()
