import cv2
import numpy as np


class EventProcessor:

    def __init__(self, event_gen_name, frame_gen_name, width, height, display_callback=False,
                 make_matrix_sum_event=False, make_matrix_event=False):
        self.__event_gen_name = event_gen_name
        self.__frame_gen_name = frame_gen_name
        self.width = width
        self.height = height
        self.event_2d_arrays = None
        self.make_matrix_sum_event = make_matrix_sum_event
        self.matrix_sum_event = np.zeros((self.height, self.width))
        self.make_matrix_event = make_matrix_event
        self.matrix_event = np.empty((self.height, self.width), dtype=np.ndarray)
        self.display_callback = display_callback

    def draw_frame(self):
        cv2.imshow('Events Display OpenCV', self.event_2d_arrays.squeeze())
        cv2.waitKey(1)  # 1 ms to yield ui

    def get_event_2d_arrays(self):
        return self.event_2d_arrays

    def get_cut_event_2d_arrays(self, x0, x1, y0, y1):
        return self.event_2d_arrays[y0:y1, x0:x1]

    def get_matrix_sum_event(self):
        if self.make_matrix_sum_event:
            return self.matrix_sum_event

    def get_cut_matrix_sum_event(self, x0, x1, y0, y1):
        if self.make_matrix_sum_event:
            return self.matrix_sum_event[y0:y1, x0:x1]

    def get_matrix_event(self):
        if self.make_matrix_event:
            return self.matrix_event

    def get_cut_matrix_event(self, x0, x1, y0, y1):
        if self.make_matrix_event:
            return self.matrix_event[y0:y1, x0:x1]

    def multiprocess_matrix_generation(self, e):
        if self.make_matrix_sum_event:
            self.matrix_sum_event[e[1]][e[0]] += 1
        if self.make_matrix_event:
            self.matrix_event[e[1]][e[0]].add(e)

    def event_callback(self, t, src_events, src_2d_arrays):
        if self.__event_gen_name in src_events:
            event_buffer = src_events[self.__event_gen_name][2]
            if len(event_buffer) != 0:
                if self.display_callback:
                    # event format (x, y, polarity, timestamp)
                    print("This callback contains {} events. The first event is {}".format(len(event_buffer),
                                                                                           event_buffer[0]))

                if self.make_matrix_sum_event:
                    self.matrix_sum_event = np.zeros((self.height, self.width))
                if self.make_matrix_event:
                    self.matrix_event = np.empty((self.height, self.width), dtype=np.ndarray)

                for e in event_buffer:
                    if self.make_matrix_sum_event:
                        self.matrix_sum_event[e[1]][e[0]] += 1
                    if self.make_matrix_event:
                        if self.matrix_event[e[1]][e[0]] is None:
                            self.matrix_event[e[1]][e[0]] = []
                        self.matrix_event[e[1]][e[0]].append(e)
                    if self.make_matrix_event == False and self.make_matrix_sum_event == False:
                        break


        if self.__frame_gen_name in src_2d_arrays:
            self.event_2d_arrays = src_2d_arrays[self.__frame_gen_name][2]
