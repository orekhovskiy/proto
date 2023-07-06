from concurrent import futures
import grpc
import image_pb2
import image_pb2_grpc
import time
import cv2
from google.protobuf.timestamp_pb2 import Timestamp


class ImageService(image_pb2_grpc.ImageServiceServicer):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.frame_id = 0

    def StreamImages(self, request, context):
        while True:
            ret, frame = self.cap.read()
            ret, jpeg = cv2.imencode('.jpg', frame)
            data = jpeg.tostring()

            current_time = time.time()  # Generate a timestamp based on current time

            timestamp = Timestamp()
            timestamp.seconds = int(current_time)
            timestamp.nanos = int((current_time - timestamp.seconds) * 1e9)

            response = image_pb2.ImageResponse(
                id=self.frame_id,
                image=data,
                timestamp=timestamp
            )

            print(f"Frame ID: {response.id}")
            print(f"Frame Timestamp: seconds: {response.timestamp.seconds}, "
                  f"nanos: {response.timestamp.nanos}")

            self.frame_id += 1

            yield response
            time.sleep(0.1)  # Adjust this sleep time to control the rate of images


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    image_pb2_grpc.add_ImageServiceServicer_to_server(ImageService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
