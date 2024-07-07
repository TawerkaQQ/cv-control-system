import time
import argparse
import cv2


from python_package.insightface import model_zoo
from qdrant_client import QdrantClient
from sort import Sort


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default=0)
    parser.add_argument('--detector', type=str, default='./models/buffalo_l/det_10g.onnx')
    parser.add_argument('--recognition', type=str, default='./models/buffalo_l/w600k_r50.onnx')
    return parser.parse_args()


args = parse_args()

client = QdrantClient("localhost", port=6333)

detector = model_zoo.get_model(args.detector)
detector.prepare(ctx_id=0, input_size=(640, 640))

handler = model_zoo.get_model(args.recognition)
handler.prepare(ctx_id=0)

mot_tracker = Sort()

rtsp_url = 'url'
cap = cv2.VideoCapture(args.input)


def main():
    prev_frame_time = 0
    new_frame_time = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (1200, 800))
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        fps = int(fps)
        fps = str(fps)

        # putting the FPS count on the frame
        cv2.putText(frame, f'FPS: {fps}', (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 3, cv2.LINE_AA)

        # detect image
        det, landmarks = detector.detect(frame)
        # print(landmarks)

        track_bbs_ids = mot_tracker.update(det)

        for trecker in mot_tracker.trackers:
            history = trecker.history

            if len(history) > 1:
                for detection in range(len(history)-1):

                    x = (int(history[detection][0][0]) + int(history[detection][0][2])) / 2
                    y = (int(history[detection][0][1]) + int(history[detection][0][3])) / 2
                    x1 = (int(history[detection][0][0]) + int(history[detection][0][2])) / 2
                    y1 = (int(history[detection][0][1]) + int(history[detection][0][3])) / 2

            # set points
                    start_point = (int(x), int(y))
                    next_point = (int(x1), int(y1))
                    cv2.line(frame, start_point, next_point, color=(0, 0, 0), thickness=10)

            # Put Id into window
            # cv2.putText(frame, f'id: {d[4]}', (150,150),  cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 255, 0), 3, cv2.LINE_AA)

        # indetification with arcface
        for i in range(det.shape[0]):
            kpts = landmarks[i]
            emb, wraped_img = handler.get(frame, kpts)
            # print(emb) show emb

            # search emb and
            search_result = client.search(
                collection_name="skb_workers", query_vector=emb, limit=1
            )

            # show result
            if search_result[0].score > 150:
                print(search_result)

            # show all crop image
            cv2.imshow(f'crop img{i}', wraped_img)

        # Show BBox on image
        for bbox in range(len(det)):
            start_point = (((det[bbox])[0]).astype(int), ((det[bbox])[1]).astype(int))
            end_point = (((det[bbox])[2]).astype(int), ((det[bbox])[3]).astype(int))
            cv2.rectangle(frame, start_point, end_point, (0, 255, 0), 2)

        # for face in range(len(landmarks)):
        #     for marks in range(len(landmarks[face])):
        #         x = int(landmarks[face][marks][0])
        #         y = int(landmarks[face][marks][1])
        #         cv2.circle(frame, (x, y), radius=4, color=(0, 0, 255), thickness=-1)

        cv2.imshow('Face Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
