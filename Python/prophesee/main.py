from metavision_hal import DeviceDiscovery
import metavision_designer_engine as mvd_engine
import metavision_designer_core as mvd_core
import metavision_designer_analytics as mvd_analytics

device = DeviceDiscovery.open("")

# Create HalDeviceInterface
interface = mvd_core.HalDeviceInterface(device)

# Read CD events from the camera
prod_cd = mvd_core.CdProducer(interface)

# Display the input events image.
img_display_cd = mvd_core.ImageDisplayCV(prod_cd)
img_display_cd.set_name("Input CD events")

controller = mvd_engine.Controller()

controller.add_device_interface(interface)
controller.add_component(prod_cd)
controller.add_component(img_display_cd, "img_display_cd")

# Set up rendering at 25 frames per second
controller.add_renderer(img_display_cd, mvd_engine.Controller.RenderingMode.SimulationClock, 25.)
controller.enable_rendering(True)

# Set controller parameters for running :
controller.set_slice_duration(10000)
controller.set_batch_duration(100000)
sync_controller = False

# Start camera
simple_device = device.get_i_device_control()
simple_device.start()

# Start the streaming of events
i_events_stream = device.get_i_events_stream()
i_events_stream.start()

# Main loop
cnt = 0
while not (controller.is_done()):
    controller.run(sync_controller)
    last_key = controller.get_last_key_pressed()
    if last_key == ord('q'):
        break
    if cnt % 100 == 0:
        controller.print_stats()
    cnt = cnt + 1
