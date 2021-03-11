from os import path
import sys
import metavision_designer_engine as mvd_engine
from metavision_designer_engine import Controller, KeyboardEvent
import metavision_designer_core as mvd_core
import metavision_hal as mv_hal
import cv2

from Python.prophesee.pipeline.EventProcessor import EventProcessor

input_filename = "./../../../../out_2021-03-05_15-37-15.raw"  # ne fonctionne pas avec ~/
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

# Create Frame Generator with 20ms accumulation time
frame_gen = mvd_core.FrameGenerator(cd_producer)
frame_gen.set_dt(20000)
controller.add_component(frame_gen, "FrameGenerator")


# We use PythonConsumer to "grab" the output of two components: cd_producer and frame_gen
# pyconsumer will callback the application each time it receives data, using the event_callback function
frame_gen_name = "FrameGen"
cd_prod_name = "CDProd"
ev_proc = EventProcessor(event_gen_name=cd_prod_name, frame_gen_name=frame_gen_name, display=True)

pyconsumer = mvd_core.PythonConsumer(ev_proc.event_callback)
pyconsumer.add_source(cd_producer, cd_prod_name)
pyconsumer.add_source(frame_gen, frame_gen_name)
controller.add_component(pyconsumer, "PythonConsumer")

controller.set_slice_duration(10000)
controller.set_batch_duration(40000)
do_sync = True if from_file else False

# Start the camera
if not from_file:
    simple_device = device.get_i_device_control()
    simple_device.start()

# Start the streaming of events
    i_events_stream = device.get_i_events_stream()
    i_events_stream.start()

# Run pipeline & print execution statistics
while not controller.is_done():

    controller.run(do_sync)

    # Render frame
    ev_proc.draw_frame()

    # Get the last key pressed
    last_key = controller.get_last_key_pressed()

    # Exit program if requested
    if last_key == ord('q') or last_key == KeyboardEvent.Symbol.Escape:
        break

cv2.destroyAllWindows()
