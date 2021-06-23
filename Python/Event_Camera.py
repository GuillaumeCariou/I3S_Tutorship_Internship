from os import path
import sys
import Foveation
import metavision_designer_engine as mvd_engine
import numpy as np
from metavision_designer_engine import Controller, KeyboardEvent
import metavision_designer_cv as mvd_cv
import metavision_designer_core as mvd_core
import metavision_hal as mv_hal
import cv2
from Python.EventProcessor import EventProcessor
from metavision_designer_core import RoiFilter

input_filename = "./../../out_2021-03-25_17-33-13.raw"  # ne fonctionne pas avec ~/

# cam = input("Do you want to use cam ? Y or N ")

# if cam == "Y" or cam == "y":
from_file = False
controller = Controller()

device = mv_hal.DeviceDiscovery.open('')

# Add the device interface to the pipeline
interface = mvd_core.HalDeviceInterface(device)
controller.add_device_interface(interface)

cd_producer = mvd_core.CdProducer(interface)

frame_gen_name = "FrameGenerator"
cd_prod_name = "CD Producer"
# Get the sensor size.
geometry = device.get_i_geometry()
width = geometry.get_width()
height = geometry.get_height()
print("Sensor size width = {}   height = {}".format(width, height))

# Add cd_producer to the pipeline
controller.add_component(cd_producer, cd_prod_name)

roi_width = int(100)
roi_height = int(100)
x0 = int(width/2 - roi_width/2)
y0 = int(height/2 - roi_height/2)
x1 = x0 + roi_width
y1 = y0 + roi_height
roi_filter = RoiFilter(cd_producer, x0, y0, x1, y1)
controller.add_component(roi_filter)

# ActivityNoiseFilter configuration
time_window_length = 1500  # duration in us plus c'est bas plus c'est filtré
cd_filtered = mvd_cv.ActivityNoiseFilter(roi_filter, time_window_length)
controller.add_component(cd_filtered, "Noise filter")
filtered_frame_gen = mvd_core.FrameGenerator(cd_filtered)
controller.add_component(filtered_frame_gen, "Filtered frame generator")
######################################OR######################################
# Create Frame Generator with 20ms accumulation time
frame_gen = mvd_core.FrameGenerator(roi_filter)
frame_gen.set_dt(20000)
controller.add_component(frame_gen, frame_gen_name)

# We use PythonConsumer to "grab" the output of two components: cd_producer and frame_gen
# pyconsumer will callback the application each time it receives data, using the event_callback function
ev_proc = EventProcessor(event_gen_name=cd_prod_name, frame_gen_name=frame_gen_name, width=width, height=height,
                         display_callback=False, make_matrix_sum_event=True)

pyconsumer = mvd_core.PythonConsumer(ev_proc.event_callback)
pyconsumer.add_source(cd_filtered, cd_prod_name)  # filtered (cd_filtered) or not filtered (cd_producer)
pyconsumer.add_source(filtered_frame_gen, frame_gen_name)  # filtered (filtered_frame_gen) or not filtered (frame_gen)
controller.add_component(pyconsumer, "PythonConsumer")

controller.set_slice_duration(20000)
controller.set_batch_duration(50000)
do_sync = True if from_file else False

# Start the camera
if not from_file:
    simple_device = device.get_i_device_control()
    simple_device.start()

# Start the streaming of events
i_events_stream = device.get_i_events_stream()
i_events_stream.start()


#commencer par créer une matrice d'event avec chaque case contien l'object d'event
#ensuite réduire la matrice
#décider des zone a mettre en high en fonction du nombre d'event

# scan pour des groupe d'event pour calculer le nombre d'event par groupe pour pouvoir décider de l'afficher ou pas
# OU
# scanner pour la densité par pixel est suffisant ? On peut mettre le seuil a 1 ce qui afficherai tous les évenements
# ON pourrais aussi essayer de relier des groupe ensemble pour afficher l'entre 2 mais esque c'est util ?
while not controller.is_done():
    controller.run(do_sync)


    matrix_bool = Foveation.scan_for_event_density(ev_proc.get_cut_matrix_sum_event(x0, x1, y0, y1), threshold=3)
    # j'ai une matrice contenant le nombre d'événement par pixel
    # une matrice qui contient les événements sur chaque pixel
    # il faut que je nétoie les truc inutiles
    # partir de low pour faire des zone de high

    #réduire résolution
    cv2.imshow('high', ev_proc.get_cut_matrix_sum_event(x0, x1, y0, y1))
    cv2.imshow('low ', Foveation.high_to_low_resolution(ev_proc.get_cut_matrix_sum_event(x0, x1, y0, y1), divide_size_by=2, fonction=Foveation.FOR_INT))

    cv2.imshow('frame ', cv2.resize(ev_proc.get_cut_event_2d_arrays(x0, x1, y0, y1), (400, 400)))
    cv2.imshow('matrix', cv2.resize(ev_proc.get_cut_matrix_sum_event(x0, x1, y0, y1), (400, 400)))
    cv2.imshow('bool  ', cv2.resize(Foveation.convert_bool_matrix_to_int_matrix(matrix_bool), (400, 400)))
    cv2.waitKey(1)

    last_key = controller.get_last_key_pressed()
    if last_key == ord('q') or last_key == KeyboardEvent.Symbol.Escape:
        break

cv2.destroyAllWindows()











"""
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
        
    def print_matrix(matrix):
        sourcefile = open("ahah.txt", "w")
        for i in range(len(matrix)):
            string = ""
            for j in range(len(matrix[i])):
                string += str("[{}, {}, {}]".format(j, i, matrix[i][j][0]))
            print(string, file=sourcefile)
"""
