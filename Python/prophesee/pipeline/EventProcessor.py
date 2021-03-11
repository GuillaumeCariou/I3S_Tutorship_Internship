from os import path
import sys
import metavision_designer_engine as mvd_engine
import metavision_designer_core as mvd_core
import metavision_hal as mv_hal
import cv2


class EventProcessor:
    """
    Simple wrapper around Python Consumer
    """

    def __init__(self, event_gen_name, frame_gen_name, display=False):
        """
        Constructor
        """
        self.__event_gen_name = event_gen_name
        self.__frame_gen_name = frame_gen_name
        self.__frame = None
        self.display = display

    def draw_frame(self):
        """
        Called from main thread to Display frame
        """
        cv2.imshow('Events Display OpenCV', self.__frame)
        cv2.waitKey(1)  # 1 ms to yield ui

    def event_callback(self, ts, src_events, src_2d_arrays):
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
            if len(event_buffer) != 0 and self.display:
                print("This callback contains {} events. The first event is {}".format(len(event_buffer),
                                                                                       event_buffer[0]))  # format de event x y event timestep

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
