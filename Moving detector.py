import argparse
import pathlib

import cv2
import numpy as np


#Default RTSP stream url
RTSP_URL = 'rtsp://admin:darviqR2QLion@10.131.63.120:554/ISAPI/Streaming/Channels/101'
FPS = 30
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default=RTSP_URL)
    parser.add_argument('--output', type=pathlib.Path, default='output.mp4')
    parser.add_argument('--threshold', type=float, default=1000.0)
    parser.add_argument('--show', action='store_true')
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.output.exists():
        raise RuntimeError('The output file exists, try to use another filename')

    if len(args.input) == 1:
        try:
            input = eval(args.input)
        except:
            raise RuntimeError('Wrong input for video')
    else:
        input = args.input


    # Prepare videocapture and vriter
    cap = cv2.VideoCapture(input)
    backSub = cv2.createBackgroundSubtractorMOG2()
    
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    size = (frame_width, frame_height)
    
    codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    writer = cv2.VideoWriter(str(args.output), codec, 30, size)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                raise RuntimeError('Could not read frame')

            # Apply background subtraction
            fg_mask = backSub.apply(frame)
            #add threshold to mask (to avoid shadows)
            retval, mask_thresh = cv2.threshold( fg_mask, 180, 255, cv2.THRESH_BINARY)

            # Apply erosion (to avoid blue points)
            mask_eroded = cv2.morphologyEx(mask_thresh, cv2.MORPH_OPEN, kernel)

            counter = np.count_nonzero(mask_eroded)
            if counter > args.threshold:
                writer.write(frame)


            if args.show:
                mask_eroded = cv2.resize(mask_eroded, (800,600))
                cv2.imshow('Frame_final', mask_eroded)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cap.release()
        writer.release()
        cv2.destroyAllWindows()
        
    except KeyboardInterrupt:
        cap.release()
        writer.release()
        cv2.destroyAllWindows()

    print("The video was successfully saved")

if __name__ == '__main__':
    main()