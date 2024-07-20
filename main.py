import argparse
import threading
import queue_stream
from python_package.insightface import model_zoo
from sort import Sort


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--detector', type=str, default='./models/buffalo_l/det_10g.onnx')
    parser.add_argument('--recognition', type=str, default='./models/buffalo_l/w600k_r50.onnx')
    return parser.parse_args()

args = parse_args()

detector = model_zoo.get_model(args.detector)
detector.prepare(ctx_id=0, input_size=(640, 640))

handler = model_zoo.get_model(args.recognition)
handler.prepare(ctx_id=0)

mot_tracker = Sort()

rtsp_url1 = 0
rtsp_url2 = 1

def main():
    frame_queue = queue_stream.FrameQueue(maxsize=100)

    camera1_thread = threading.Thread(target=queue_stream.capture_frames, args=(frame_queue, rtsp_url1))
    camera2_thread = threading.Thread(target=queue_stream.capture_frames, args=(frame_queue, rtsp_url2))

    processing_thread = threading.Thread(target=queue_stream.process_frames, args=(frame_queue, detector, handler, mot_tracker))

    camera1_thread.start()
    camera2_thread.start()
    processing_thread.start()

    camera1_thread.join()
    camera2_thread.join()
    processing_thread.join()

if __name__ == '__main__':
    main()
