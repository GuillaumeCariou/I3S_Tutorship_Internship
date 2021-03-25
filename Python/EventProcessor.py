from os import path
import sys
import metavision_designer_engine as mvd_engine
import metavision_designer_core as mvd_core
import metavision_hal as mv_hal
import cv2
import numpy as np


class EventProcessor:
    """
    Simple wrapper around Python Consumer
    """

    def __init__(self, event_gen_name, frame_gen_name, width, height, display_callback=False, make_matrix=False):
        """
        Constructor
        """
        self.__event_gen_name = event_gen_name
        self.__frame_gen_name = frame_gen_name
        self.__frame = None
        self.width = width
        self.height = height
        self.display_callback = display_callback
        self.image_matrix = np.zeros((self.height, self.width))
        self.make_matrix = make_matrix

    def draw_frame(self):
        """
        Called from main thread to Display frame
        """
        cv2.imshow('Events Display OpenCV', self.__frame)

        if self.make_matrix:
            cv2.imshow("Matrix", self.image_matrix.squeeze())
            self.image_matrix = np.zeros((self.height, self.width))
        cv2.waitKey(1)  # 1 ms to yield ui

        return self.__frame

    def get_frame(self):
        return self.__frame

    def event_callback(self, t, src_events, src_2d_arrays):
        """
        Python Callback for PythonConsumer component in a
        Metavision Designer pipeline
        """
        if self.__event_gen_name in src_events:
            # the shape of the frame in the analog buffer
            event_type = src_events[self.__event_gen_name][0]
            # the encoding information. These are just for information, as the data in src_events[2]
            # is already decoded
            dtype_obj = src_events[self.__event_gen_name][1]
            # the actual event buffer data
            event_buffer = src_events[self.__event_gen_name][2]
            # get the number of events in this callback
            if len(event_buffer) != 0:
                if self.display_callback:
                    print("This callback contains {} events. The first event is {}".format(len(event_buffer), event_buffer[0]))  # event format (x, y, polarity, timestamp)
                if self.make_matrix:
                    for x, y, polarity, timesamp in event_buffer:
                        self.image_matrix[y][x] += polarity

        if self.__frame_gen_name in src_2d_arrays:
            # the shape of the frame in the analog buffer
            buffer_shape = src_2d_arrays[self.__frame_gen_name][0]
            # the encoding information. These are just for information, as the data in src_2d_arrays[2]
            # is already decoded
            dtype_obj = src_2d_arrays[self.__frame_gen_name][1]
            # the actual analog buffer data
            frame_buffer = src_2d_arrays[self.__frame_gen_name][2]
            # convert the frame data into a format compatible with OpenCV
            self.__frame = frame_buffer.squeeze()
