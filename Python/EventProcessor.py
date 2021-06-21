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

    def __init__(self, event_gen_name, frame_gen_name, width, height, display_callback=False):
        """
        Constructor
        """
        self.__event_gen_name = event_gen_name
        self.__frame_gen_name = frame_gen_name
        self.width = width
        self.height = height
        self.__frame = None
        self.event_2d_arrays = None
        self.matrix = np.zeros((self.height, self.width))
        self.display_callback = display_callback

    def draw_frame(self):
        cv2.imshow('Events Display OpenCV', self.__frame)
        cv2.waitKey(1)  # 1 ms to yield ui

    def get_frame(self):
        return self.__frame

    def get_cut_frame(self, x0, x1, y0, y1):
        return self.__frame[y0:y1, x0:x1]

    def get_matrix(self):
        return self.matrix

    def get_cut_matrix(self, x0, x1, y0, y1):
        return self.matrix[y0:y1, x0:x1]

    def get_event_2d_arrays(self):
        return self.event_2d_arrays

    def get_cut_event_2d_arrays(self, x0, x1, y0, y1):
        return self.event_2d_arrays[y0:y1, x0:x1]

    def event_callback(self, t, src_events, src_2d_arrays):
        if self.__event_gen_name in src_events:
            event_buffer = src_events[self.__event_gen_name][2]
            if len(event_buffer) != 0:
                if self.display_callback:
                    # event format (x, y, polarity, timestamp)
                    print("This callback contains {} events. The first event is {}".format(len(event_buffer), event_buffer[0]))
                self.matrix = np.zeros((self.height, self.width))
                for e in event_buffer:
                    self.matrix[e[1]][e[0]] += 1


        if self.__frame_gen_name in src_2d_arrays:
            self.event_2d_arrays = src_2d_arrays[self.__frame_gen_name][2]
            self.__frame = self.event_2d_arrays.squeeze()
