import os
import argparse
import cv2
import numpy as np
import time
from threading import Thread
import importlib.util
from typing import List
import sys
from tflite_runtime.interpreter import Interpreter, load_delegate

video_driver_id = 3
class VideoStream:
    """Handles video streaming from the webcam."""
    def __init__(self, resolution=(640, 480), framerate=30):
        self.stream = cv2.VideoCapture(video_driver_id)
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'RGGB'))
#        self.stream.set(3, resolution[0])
#        self.stream.set(4, resolution[1])
        print('Backend: ',self.stream.get(cv2.CAP_PROP_BACKEND))
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False

    def start(self):
        """Starts the thread that reads frames from the video stream."""
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        """Continuously updates the frame from the video stream."""
        while True:
            if self.stopped:
                self.stream.release()
                return
            self.grabbed, self.frame = self.stream.read()

    def read(self):
        """Returns the most recent frame."""
        return self.frame

    def stop(self):
        """Stops the video stream and closes resources."""
        self.stopped = True
    
    def get_fourcc(self):
        fourcc = int(self.stream.get(cv2.CAP_PROP_FOURCC))
        fourcc = bytes([
            v & 255 for v in (fourcc, fourcc >> 8, fourcc >> 16, fourcc >> 24)
        ]).decode()
        return fourcc

def load_labels(labelmap_path: str) -> List[str]:
    """Loads labels from a label map file."""
    try:
        with open(labelmap_path, 'r') as f:
            labels = [line.strip() for line in f.readlines()]
        if labels[0] == '???':
            labels.pop(0)
        return labels
    except IOError as e:
        print(f"Error reading label map file: {e}")
        sys.exit()


def main():
    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('--modeldir', required=True, help='Folder the .tflite file is located in')
    parser.add_argument('--graph', default='detect.tflite', help='Name of the .tflite file')
    parser.add_argument('--labels', default='labelmap.txt', help='Name of the labelmap file')
    parser.add_argument('--threshold', default='0.5', help='Minimum confidence threshold')
    parser.add_argument('--resolution', default='1280x720', help='Desired webcam resolution')
    args = parser.parse_args()

    # Configuration
    model_path = os.path.join(os.getcwd(), args.modeldir, args.graph)
    labelmap_path = os.path.join(os.getcwd(), args.modeldir, args.labels)
    min_conf_threshold = float(args.threshold)
    resW, resH = map(int, args.resolution.split('x'))

    # Load labels and interpreter
    labels = load_labels(labelmap_path)
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Get model details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height, width = input_details[0]['shape'][1:3]
    floating_model = (input_details[0]['dtype'] == np.float32)

    outname = output_details[0]['name']
    boxes_idx, classes_idx, scores_idx = (1, 3, 0) if 'StatefulPartitionedCall' in outname else (0, 1, 2)

    # Initialize video stream
    videostream = VideoStream(resolution=(resW, resH), framerate=30).start()
    time.sleep(1)

    frame_rate_calc = 1
    freq = cv2.getTickFrequency()
    fourcc =videostream.get_fourcc()
    print(f"FOURCC: {fourcc}")

    count = 0
    while True:
        count = count + 1
        t1 = cv2.getTickCount()
        frame = videostream.read()
        cv2.imwrite("frame%d.jpg" % count, frame)     # save frame as JPEG file 
#        print(frame)
        print(frame.shape)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height))
        input_data = np.expand_dims(frame_resized, axis=0)

        if floating_model:
            input_data = (np.float32(input_data) - 127.5) / 127.5

        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        boxes = interpreter.get_tensor(output_details[boxes_idx]['index'])[0]
        classes = interpreter.get_tensor(output_details[classes_idx]['index'])[0]
        scores = interpreter.get_tensor(output_details[scores_idx]['index'])[0]

        for i in range(len(scores)):
            if min_conf_threshold < scores[i] <= 1.0:
                ymin, xmin, ymax, xmax = [int(coord) for coord in (boxes[i] * [resH, resW, resH, resW])]
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
                object_name = labels[int(classes[i])]
                label = f'{object_name}: {int(scores[i] * 100)}%'
                print(label)
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                label_ymin = max(ymin, labelSize[1] + 10)
                cv2.rectangle(frame, (xmin, label_ymin - labelSize[1] - 10), (xmin + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cv2.putText(frame, f'FPS: {frame_rate_calc:.2f}', (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
#        cv2.imshow('Object detector', frame)

        t2 = cv2.getTickCount()
        time1 = (t2 - t1) / freq
        frame_rate_calc = 1 / time1

        if cv2.waitKey(1) == ord('q'):
            break

#    cv2.destroyAllWindows()
    videostream.stop()

if __name__ == "__main__":
    main()
