import os
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow import keras
import numpy as np
import cv2

os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'

# run on gpu
physical_devices = tf.config.experimental.list_physical_devices('GPU')
assert len(physical_devices) > 0, "Not enough GPU hardware devices available"
config = tf.config.experimental.set_memory_growth(physical_devices[0], True)

height = 320  # 640
dim = (height, height)
color = (255, 0, 0)

vid = cv2.VideoCapture(0)
detector = tf.keras.models.load_model("./ssd_mobile_net/")
# detector = hub.load("https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2")
# detector = hub.load("https://tfhub.dev/tensorflow/ssd_mobilenet_v1/fpn_640x640/1")

while True:
    ret, frame = vid.read()
    # image_np_expanded = np.expand_dims(frame, axis=0)
    frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    input_tensor = tf.convert_to_tensor(np.expand_dims(frame, 0), dtype=tf.uint8)
    detections = detector(input_tensor)

    # print("nombre: {}, size: {}".format(detections["num_detections"][0], detections["detection_boxes"][0][0]))
    # print(detections["detection_scores"])
    for i in range(int(detections["num_detections"][0])):
        if detections["detection_scores"][0][i] >= 0.50:
            # print(detections["detection_scores"][0][i])
            xmin = int(detections["detection_boxes"][0][i][1] * height)
            ymin = int(detections["detection_boxes"][0][i][0] * height)
            xmax = int(detections["detection_boxes"][0][i][3] * height)
            ymax = int(detections["detection_boxes"][0][i][2] * height)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
    cv2.imshow('personne_detection', frame)

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
