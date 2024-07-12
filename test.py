import time
import argparse
import cv2
import threading
import queue

from python_package.insightface import model_zoo
# from qdrant_client import QdrantClient
from sort import Sort

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--detector', type=str, default='./models/buffalo_l/det_10g.onnx')
    parser.add_argument('--recognition', type=str, default='./models/buffalo_l/w600k_r50.onnx')
    return parser.parse_args()


args = parse_args()

# client = QdrantClient("localhost", port=6333)

detector = model_zoo.get_model(args.detector)
detector.prepare(ctx_id=0, input_size=(640, 640))

handler = model_zoo.get_model(args.recognition)
handler.prepare(ctx_id=0)

mot_tracker = Sort()

# rtsp_url = "rtsp://admin:darviqR2QLion@10.131.63.120:554/ISAPI/Streaming/Channels/101"
rtsp_url1 = 0
rtsp_url2 = 2

class FrameQueue:
    def __init__(self, maxsize):
        self.queue = queue.Queue(maxsize)
        self.lock = threading.Lock()

    def put(self, frame):
        with self.lock:
            self.queue.put(frame)

    def get(self):
        with self.lock:
            return self.queue.get()

    def empty(self):
        with self.lock:
            return self.queue.empty()

# Если у нас достиг максайза количество кадров, то мы последний не добавляем, либо убираем первый и добавляем последний
# Холодный старт сделать 
         
def main():
    frame_queue = FrameQueue(maxsize=900000000)

    camera1_thread = threading.Thread(target=capture_frames, args=(frame_queue, rtsp_url1))
    camera2_thread = threading.Thread(target=capture_frames, args=(frame_queue, rtsp_url2))

    processing_thread = threading.Thread(target=process_frames, args=(frame_queue,))

    camera1_thread.start()
    camera2_thread.start()
    processing_thread.start()

    camera1_thread.join()
    camera2_thread.join()
    processing_thread.join()

def capture_frames(frame_queue, rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_queue.put(frame)

def process_frames(frame_queue):    
    while True:
        if not frame_queue.empty():

            frame = frame_queue.get()
            print(frame_queue.queue.qsize())
            time.sleep(0.1)

            # detect image
            det, landmarks = detector.detect(frame)
            # print(landmarks)

            track_bbs_ids = mot_tracker.update(det)

            for trecker in mot_tracker.trackers:
                history = trecker.history

                if len(history) > 1:
                    for detection in range(len(history) - 1):
                        x = (int(history[detection][0][0]) + int(history[detection][0][2])) / 2
                        y = (int(history[detection][0][1]) + int(history[detection][0][3])) / 2
                        x1 = (int(history[detection][0][0]) + int(history[detection][0][2])) / 2
                        y1 = (int(history[detection][0][1]) + int(history[detection][0][3])) / 2

                        # set points
                        start_point = (int(x), int(y))
                        next_point = (int(x1), int(y1))
                        cv2.line(frame, start_point, next_point, color=(0, 0, 0), thickness=10)

            # indetification with arcface
            for i in range(det.shape[0]):
                kpts = landmarks[i]
                emb, wraped_img = handler.get(frame, kpts)

                # show all crop image
                cv2.imshow(f'crop img{i}', wraped_img)

            # Show BBox on image
            for bbox in range(len(det)):
                start_point = (((det[bbox])[0]).astype(int), ((det[bbox])[1]).astype(int))
                end_point = (((det[bbox])[2]).astype(int), ((det[bbox])[3]).astype(int))
                cv2.rectangle(frame, start_point, end_point, (0, 255, 0), 2)

            for face in range(len(landmarks)):
                for marks in range(len(landmarks[face])):
                    x = int(landmarks[face][marks][0])
                    y = int(landmarks[face][marks][1])
                    cv2.circle(frame, (x, y), radius=4, color=(0, 0, 255), thickness=-1)

            cv2.imshow('Face Detection', frame)


            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()