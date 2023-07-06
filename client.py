import grpc
import cv2
import numpy as np
import image_pb2
import image_pb2_grpc
import time
import threading
from google.protobuf.timestamp_pb2 import Timestamp


class ImageClient:
    def __init__(self, server_address, delay=1):
        self.server_address = server_address
        self.delay = delay
        self.latest_frame_id = None
        self.latest_frame_timestamp = None
        self.latest_frame = None
        self._stop_event = threading.Event()  # Event to signal the thread to stop
        self._display_thread = threading.Thread(target=self._display_loop, args=(self.delay,))  # Display thread
        self._display_thread.start()

    def process_frame(self, response):
        self.latest_frame_id = response.id
        self.latest_frame_timestamp = response.timestamp
        nparr = np.frombuffer(response.image, np.uint8)
        self.latest_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    def display_latest_frame(self):
        if self.latest_frame is not None:
            print(f"Latest Frame ID: {self.latest_frame_id}")
            print(f"Latest Frame Timestamp: seconds: {self.latest_frame_timestamp.seconds}, "
                  f"nanos: {self.latest_frame_timestamp.nanos}")
            # You can perform further operations with the latest frame here

    def _display_loop(self, delay):
        while not self._stop_event.is_set():
            self.display_latest_frame()
            time.sleep(delay)

    def run(self):
        channel = grpc.insecure_channel(self.server_address)
        stub = image_pb2_grpc.ImageServiceStub(channel)

        try:
            responses = stub.StreamImages(image_pb2.StreamRequest())
            for response in responses:
                self.process_frame(response)
        except grpc.RpcError as e:
            print(f"RPC Error: {e}")
        finally:
            self._stop_event.set()  # Signal the display thread to stop when done
            self._display_thread.join()  # Wait for the display thread to finish


if __name__ == '__main__':
    client = ImageClient('localhost:50051')
    client.run()
