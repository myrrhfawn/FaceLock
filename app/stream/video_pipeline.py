#!/usr/bin/env python
import cv2
import numpy as np
import yaml

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GObject
#from gi.repository import GdkX11, GstVideo
from threading import Event, Thread
from fl_utils.base_logging import setup_logging
from logging import getLogger
import queue
from app.constants import MIN_DETECTION_FPS, SHOW_DETECTION
from app.common.frame import Frame
from app.detector.simple_facerec import SimpleFaceRec

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
setup_logging(file_name="video_stream.log")
logger = getLogger(__name__)

class GStreamerPipeline(Thread):

    CONFIG_FILE = "/data/FaceLock/app/stream/config_gstream.yaml"

    def __init__(self):
        Thread.__init__(self, daemon=True)

        Gst.init(None)

        config = self.__load_config()

        self.player = Gst.Pipeline.new("player")
        self.source = Gst.ElementFactory.make(config["gstreamer_source"], "vsource")
        self.conv = Gst.ElementFactory.make("videoconvert", "colorspace")
        self.scaler = Gst.ElementFactory.make("videoscale", "fvidscale")
        self.crop = Gst.ElementFactory.make('videocrop', 'VideoCrop')
        self.appsink = Gst.ElementFactory.make("appsink", "video-output")
        self.source.set_property("device", config["input_device"])
        self.appsink.set_property("emit-signals", True)

        caps = Gst.caps_from_string(config["app_sink_caps"])
        self.appsink.set_property("caps", caps)
        self.appsink.connect("new-sample", self.__new_frame, self.appsink)

        self.__add_many(
            [self.source, self.conv, self.scaler, self.crop, self.appsink])
        self.__link_many(
            [self.source, self.conv, self.scaler, self.crop, self.appsink])

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.__on_message)
        bus.connect("sync-message::element", self.__on_sync_message)

        self.detection_queue = queue.Queue()
        self.detector = SimpleFaceRec(self.detection_queue)

        self._stop_event = Event()
        self.frame_buffor = None
        #self.start()
        logger.info("Pipeline thread started.")

    def stopped(self):
        """TODO: Add docstring."""
        return self._stop_event.is_set()

    def stop(self):
        self.detector.stop()
        self._stop_event.set()

    def run(self) -> None:
        self.detector.start()
        self.player.set_state(Gst.State.PLAYING)

    def __load_config(self):
        config_dict = dict()
        with open(self.CONFIG_FILE, "r") as config_file:
            try:
                config_dict = yaml.safe_load(config_file)
            except yaml.YAMLError as err:
                print(err)

        return config_dict

    def __gst_to_np(self, sample):
        '''
        Converts gst to numpy ndarray

        '''
        buf = sample.get_buffer()
        caps = sample.get_caps()
        arr = np.ndarray(
            (caps.get_structure(0).get_value('height'),
             caps.get_structure(0).get_value('width'),
             3),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype=np.uint8)
        arr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        return arr

    def __add_many(self, pipeline_list):
        '''
        Add list of Gst elements to pipeline
        '''

        for node in pipeline_list:
            self.player.add(node)

    def __link_many(self, pipeline_list):
        '''
        Links ordered (left to right) components in pipeline
        '''

        for n in range(len(pipeline_list) - 1):
            pipeline_list[n].link(pipeline_list[n + 1])

    def __new_frame(self, sink, data):
        '''
        Produces new frame for appsink and stores it in curr frame

        '''

        buff = sink.emit("pull-sample")
        frame = Frame(img=self.__gst_to_np(buff))
        if self.detection_queue.qsize() > MIN_DETECTION_FPS:
            with self.detection_queue.mutex:
                self.detection_queue.queue.clear()
        self.detection_queue.put(frame)
        self.frame_buffor = frame
        return Gst.FlowReturn.OK

    def __on_message(self, bus, message):
        '''

        '''

        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err} ", debug)
            self.player.set_state(Gst.State.NULL)

    def __on_sync_message(self, bus, message):
        '''
        '''

        if message.get_structure().get_name() == 'prepare-window-handle':
            win_id = self.windowId
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            # if not window id then create new window
            if win_id is None:
                win_id = self.movie_window.get_property('window').get_xid()
            imagesink.set_window_handle(win_id)

    def isFrameReady(self):
        '''
        Allows to check if new frame is ready to be obtained from stream.
        '''

        return not (self.frame_buffor is None)

    def get_frame(self, detection: bool = False, show_det: bool = SHOW_DETECTION):
        '''
        Returns latest frame from frame buffor
        Frame is stored as numpy array.

        Out:
        frame - numpy ndarray
        '''
        if detection:
            ret_frame = self.detector.get_image_with_detection(self.frame_buffor, show_det)
        else:
            ret_frame = self.frame_buffor
        self.frame_buffor = None
        return ret_frame


    def startPrev(self):
        '''
        Starts the feed from gstream pipe.
        '''

        self.player.set_state(Gst.State.PLAYING)

