#!/usr/bin/env python
import os
import cv2
import numpy as np
import gi
import queue
from threading import Thread, Event

from app.common.fps_logger import FPSCounter

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst
from logging import getLogger
from app.constants import MIN_DETECTION_FPS, RES, INPUT_SOURCE, INPUT_DEVICE
from app.common.frame import Frame

logger = getLogger(__name__)

os.environ["XDG_RUNTIME_DIR"] = "/tmp/xdg"
os.environ["LIBVA_DRIVER_NAME"] = "dummy"
os.makedirs("/tmp/xdg", exist_ok=True)


class GStreamerPipeline(Thread):
    def __init__(self):
        super().__init__()
        Gst.init(None)

        self.player = Gst.Pipeline.new("player")
        self.frame_buffer = None
        self.detection_queue = queue.Queue()

        if INPUT_SOURCE == "web":
            self.build_webcam_pipeline()
        else:
            self.build_file_pipeline()

        self.loop = GLib.MainLoop()
        self.stopped = Event()
        self.fps_logger = FPSCounter()

        logger.info("GStreamer pipeline initialized")

    def build_file_pipeline(self):
        self.source = Gst.ElementFactory.make("uridecodebin", "source")
        if not os.path.exists(INPUT_DEVICE):
            raise RuntimeError("Input file does not exist")
        self.source.set_property("uri", f"file://{INPUT_DEVICE}")
        self.source.connect("pad-added", self.__on_pad_added)

        self.conv = Gst.ElementFactory.make("videoconvert", "videoconvert")
        self.appsink = Gst.ElementFactory.make("appsink", "appsink")

        self.__setup_appsink()

        self.__add_many([self.source, self.conv, self.appsink])
        self.__link_many([self.conv, self.appsink])

    def build_webcam_pipeline(self):
        self.source = Gst.ElementFactory.make("v4l2src", "vsource")
        self.source.set_property("device", INPUT_DEVICE)

        self.conv = Gst.ElementFactory.make("videoconvert", "colorspace")
        self.appsink = Gst.ElementFactory.make("appsink", "appsink")
        self.__setup_appsink()

        self.__add_many([self.source, self.conv, self.appsink])
        self.__link_many([self.source, self.conv, self.appsink])

    def __setup_appsink(self):
        self.appsink.set_property("emit-signals", True)
        caps = Gst.caps_from_string("video/x-raw,format=BGR")
        self.appsink.set_property("caps", caps)
        self.appsink.connect("new-sample", self.__new_frame, self.appsink)

    def __on_pad_added(self, src, pad):
        caps = pad.get_current_caps()
        name = caps.to_string()
        logger.info(f"New pad: {name}")
        if name.startswith("video/"):
            sink_pad = self.conv.get_static_pad("sink")
            pad.link(sink_pad)

    def __gst_to_np(self, sample):
        """
        Converts gst to numpy ndarray

        """
        buf = sample.get_buffer()
        caps = sample.get_caps()
        arr = np.ndarray(
            (
                caps.get_structure(0).get_value("height"),
                caps.get_structure(0).get_value("width"),
                3,
            ),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype=np.uint8,
        )
        arr = cv2.resize(arr, RES)
        return arr

    def __add_many(self, pipeline_list):
        """
        Add list of Gst elements to pipeline
        """

        for node in pipeline_list:
            self.player.add(node)

    def __link_many(self, pipeline_list):
        """
        Links ordered (left to right) components in pipeline
        """

        for n in range(len(pipeline_list) - 1):
            pipeline_list[n].link(pipeline_list[n + 1])

    def __new_frame(self, sink, data):
        """
        Produces new frame for appsink and stores it in curr frame
        """
        buff = sink.emit("pull-sample")
        frame = Frame(img=self.__gst_to_np(buff))
        # cv2.imwrite("/data/now/test.jpg", frame.img)
        if self.detection_queue.qsize() > MIN_DETECTION_FPS:
            with self.detection_queue.mutex:
                self.detection_queue.queue.clear()
        self.detection_queue.put(frame)
        self.frame_buffer = frame
        self.fps_logger.increment()
        return Gst.FlowReturn.OK

    def __on_message(self, bus, message):
        """"""
        t = message.type
        if t == Gst.MessageType.EOS:
            if INPUT_SOURCE == "file":
                logger.info("End of stream reached, restarting...")
                self.player.seek_simple(
                    Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0
                )
                self.player.set_state(Gst.State.PLAYING)
            else:
                self.player.set_state(Gst.State.NULL)

        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            logger.error(f"Error: {err} ", debug)
            self.player.set_state(Gst.State.NULL)

    def __on_sync_message(self, bus, message):
        """"""
        if message.get_structure().get_name() == "prepare-window-handle":
            win_id = self.windowId
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            # if not window id then create new window
            if win_id is None:
                win_id = self.movie_window.get_property("window").get_xid()
            imagesink.set_window_handle(win_id)

    def run(self):
        """"""
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.__on_message)
        bus.connect("sync-message::element", self.__on_sync_message)

        # self.player.set_state(Gst.State.PLAYING)

        # use this to render a dot file and then a nice graph of the pipeline
        # see https://developer.ridgerun.com/wiki/index.php/How_to_generate_a_GStreamer_pipeline_diagram
        # Gst.debug_bin_to_dot_file(self.pipeline, Gst.DebugGraphDetails.ALL, "pipeline")
        try:
            self.loop.run()
        except Exception:
            logger.info(f"Main loop stopped")

        if not self.stopped.is_set():
            self.stop()

    def stop(self):
        """"""
        self.stopped.set()
        self.fps_logger.stop()
        logger.info(f"Pipeline is stopping")
        self.player.set_state(Gst.State.NULL)
        if self.loop.is_running():
            self.loop.quit()
