import cv2
import threading
import queue

from python_package.insightface import model_zoo
from sort import Sort


class FrameQueue:
    def __init__(self, maxsize):
        self.queue = queue.Queue(maxsize)
        self.lock = threading.Lock()

    def put(self, frame):
        with self.lock:
            if self.queue.full():
                self.queue.get()
            self.queue.put(frame)

    def get(self):
        with self.lock:
            return self.queue.get()

    def empty(self):
        with self.lock:
            return self.queue.empty()

def capture_frames(frame_queue, rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_queue.put(frame)

def process_frames(frame_queue, detector, handler, mot_tracker):    
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            print(frame_queue.queue.qsize())
            det, landmarks = detector.detect(frame)
            # Предположительно трекер не работает, я когда переносил код из старого main, где была вся обработка, просто оставил в надежде что и так сработает, 
            # но я не проверял и вряд-ли сработает. Если нам вообще нужен трекер, надо подумать как его реализовать в случае с двумя камерами и сделать его тут.
            # track_bbs_ids = mot_tracker.update(det)

            for tracker in mot_tracker.trackers:
                history = tracker.history
                if len(history) > 1:
                    for detection in range(len(history) - 1):
                        x = (int(history[detection][0][0]) + int(history[detection][0][2])) / 2
                        y = (int(history[detection][0][1]) + int(history[detection][0][3])) / 2
                        x1 = (int(history[detection + 1][0][0]) + int(history[detection + 1][0][2])) / 2
                        y1 = (int(history[detection + 1][0][1]) + int(history[detection + 1][0][3])) / 2

                        start_point = (int(x), int(y))
                        next_point = (int(x1), int(y1))
                        cv2.line(frame, start_point, next_point, color=(0, 0, 0), thickness=10)

            for i in range(det.shape[0]):
                kpts = landmarks[i]
                emb, wraped_img = handler.get(frame, kpts)
                cv2.imshow(f'crop img{i}', wraped_img)

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
