from os import path
import sys
import metavision_designer_engine as mvd_engine
from metavision_designer_engine import Controller
import metavision_designer_cv as mvd_cv
import metavision_designer_core as mvd_core
import metavision_hal as mv_hal
import cv2
from Python.Event_Processor.EventProcessor import EventProcessor
from Python.Log_Luminance import Log_Luminance, Gen_Image
from metavision_designer_core import RoiFilter

# ce fichier est le ficher d'input raw si on choisis de ne pas utiliser la caméra événementielle
input_filename = "../../Movie/Log_Luminance/out_2021-07-07_13-13-28.raw"  # ne fonctionne pas avec ~/

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

# crop pour la caméra événementielle
roi_width = int(100)
roi_height = int(100)
x0 = int(width / 2 - roi_width / 2)
y0 = int(height / 2 - roi_height / 2)
x1 = x0 + roi_width
y1 = y0 + roi_height
roi_filter = RoiFilter(cd_producer, x0, y0, x1, y1)
controller.add_component(roi_filter)
print("ROI size width = {}   height = {}   Number of pixels = {}".format(roi_width, roi_height, roi_width * roi_height))

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
divide_matrix_by = 2  # de combien on divise la taille de l'image, si on part d'une résolution 100*100 on obtient du 50*50 si divisé par 2
print("divide size width = {}   height = {}   Number of pixels = {}".format(int(roi_width/divide_matrix_by), int(roi_height/divide_matrix_by),
                                                                            int(roi_width/divide_matrix_by) * int(roi_height/divide_matrix_by)))
# les deux matrices de niveaux qui permet de faire fonctionner la log luminance
# on les garde d'un batch à l'autre ce qui fait que si on a qu'un seul gros batch qui contient tous les événements l'algo fonctionne quand même
matrix_level_HQ = Log_Luminance.gen_matrix_PixelState(roi_width, roi_height)  # correspond à la haute résolution
matrix_level_LQ = Log_Luminance.gen_matrix_PixelState(int(roi_width / divide_matrix_by), int(roi_height / divide_matrix_by))  # correspond à la basse résolution

#Make Video
# si ce paramétre est mis en true, on ajoute les image créer à chaque batch dans un tableau puis on les enregistre sur le disque avec le nom spécifié dans nom_video
# le nombre de seconde est le nombre de second que la vidéo va duré, j'ai paramétré la video pour qu'elle soit cadancé à 28fps
# le temps de filmé correspond donc au temps pour acquérir nb_second_de_video*28 images  au total
make_video_at_the_end = False
nb_second_de_video = 15
nom_video = 'ahahah'  # juste mettre le nom, le fichier sortira en .avi à la fin du programme
array_img = []

while not controller.is_done():
    controller.run(do_sync)

    events = ev_proc.get_event()  # tableau d'event
    events_LQ = Log_Luminance.log_luminance(events, matrix_level_HQ, matrix_level_LQ, divide_matrix_by, (width, height),
                                            (roi_width, roi_height), treshold=1, interpolation=0)

    # cette fonction ne marche pas et je ne comprend pas POURQUOI AAAAAAAAHHHHH: elle fonctionne maintenant mais le commentaire me fait sourir
    img_original = ev_proc.get_cut_event_2d_arrays(x0, x1, y0, y1)
    img = Gen_Image.create_image_rgb_from_log_luminance(events_LQ, int(roi_width/divide_matrix_by), int(roi_height/divide_matrix_by))
    img_original = cv2.resize(img_original, (200, 200))
    img = cv2.resize(img, (200, 200))
    cv2.imshow("Original", img_original)
    cv2.imshow("Log Luminance", img)

    # les deux ligne de code en dessous permettes de visualiser le fonctionnement des matrices de niveaux mais consomme beaucoup de ressources
    #cv2.imshow("pixelstateHQ", cv2.resize(Gen_Image.create_image_rgb_from_pixel_state(matrix_level_HQ), (400, 400)))
    #cv2.imshow("pixelstateLQ", cv2.resize(Gen_Image.create_image_rgb_from_pixel_state(matrix_level_LQ), (400, 400)))

    if make_video_at_the_end:
        array_img.append(img)

    cv2.waitKey(1)  # ne jamais oublié cet ligne de code qui empêche l'image de s'afficher si elle n'est pas la

    if nb_second_de_video*28 == len(array_img) and make_video_at_the_end:
        break

cv2.destroyAllWindows()

if make_video_at_the_end:
    Gen_Image.convert_array_of_image_in_video(array_img, nom_video)
