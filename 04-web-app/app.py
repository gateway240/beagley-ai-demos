from flask import Flask, render_template, Response, request
import cv2

app = Flask(__name__)

global capture, grey, switch, neg, out
capture = 0
grey = 0
neg = 0
switch = 1

def capture_by_frames():
    global out, capture
    while True:
        success, frame = camera.read()  # read the camera frame
        if success:
            if(grey):
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if(neg):
                frame=cv2.bitwise_not(frame)    
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
                camera = cv2.VideoCapture(0)
                switch = 1


    elif request.method == "GET":
        return render_template("index.html")
    return render_template("index.html")



camera = cv2.VideoCapture(0)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=40000)

camera.release()
cv2.destroyAllWindows()