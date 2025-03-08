import os
import argparse
from flask import Flask, render_template, request, Response
import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter, load_delegate

# Toggle depending on environment
video_driver_id = 0
# video_driver_id = 3

app = Flask(__name__)

global camera, model_path
global args, capture, grey, switch, neg, out, frame_rate_calc, obj_detect
capture = 0
grey = 0
neg = 0
obj_detect = 0
switch = 1
frame_rate_calc = 1

def load_labels(labelmap_path: str):
    """Loads labels from a label map file."""
    try:
        with open(labelmap_path, 'r') as f:
            labels = [line.strip() for line in f.readlines()]
        if labels[0] == '???':
            labels.pop(0)
        return labels
    except IOError as e:
        print(f"Error reading label map file: {e}")

def capture_by_frames():
    global model_path
    global args, out, capture, frame_rate_calc
    freq = cv2.getTickFrequency()
    
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    # Get model details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height, width = input_details[0]['shape'][1:3]
    floating_model = (input_details[0]['dtype'] == np.float32)

    outname = output_details[0]['name']
    boxes_idx, classes_idx, scores_idx = (1, 3, 0) if 'StatefulPartitionedCall' in outname else (0, 1, 2)

    while True:
        t1 = cv2.getTickCount()
        success, frame = camera.read()  # read the camera frame
        if success:
            if(grey):
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if(neg):
                frame=cv2.bitwise_not(frame)  
            if(obj_detect):
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

            t2 = cv2.getTickCount()
            time1 = (t2 - t1) / freq
            frame_rate_calc = 1 / time1
            try: 
                ret, buffer = cv2.imencode(".jpg", frame)
                frame = buffer.tobytes()
                yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            except Exception as e:
                pass
        else:
            pass

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_capture")
def video_capture():
    return Response(
        capture_by_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/requests", methods=["POST", "GET"])
def tasks():
    global switch, camera
    if request.method == "POST":
        if request.form.get("click") == "Capture":
            global capture
            capture = 1
        elif request.form.get("grey") == "Grey":
            global grey
            grey = not grey
        elif request.form.get("neg") == "Negative":
            global neg
            neg = not neg
        elif request.form.get("objDetect") == "Object Detect":
            global obj_detect
            obj_detect = not obj_detect
        elif request.form.get("face") == "Face Only":
            global face
            face = not face
            if face:
                time.sleep(4)
        elif request.form.get("stop") == "Stop/Start":
            if switch == 1:
                switch = 0
                camera.release()
                cv2.destroyAllWindows()
            else:
                camera = cv2.VideoCapture(video_driver_id)
                # camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'RGGB'))
                switch = 1


    elif request.method == "GET":
        return render_template("index.html")
    return render_template("index.html")

if __name__ == "__main__":
    global model_path
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
    app.run(host="0.0.0.0", debug=True, use_reloader=False, port=40000)

camera.release()
cv2.destroyAllWindows()