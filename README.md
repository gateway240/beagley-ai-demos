# BeagleY-AI Demos

A collection of demos showing the functionality of the BeagleY-AI development board.

## 01 Led Blink

Based on [this tutorial](https://docs.beagleboard.org/boards/beagley/ai/demos/beagley-ai-using-gpio.html).

In this repository, the python code used an outdated library of `gpiod`.
The included python code runs on the BeagleY-AI with a current python venv from within the directory:

```python
python -m venv .venv
source .venv/bin/activate
```

### PWM

Based on [this tutorial](https://docs.beagleboard.org/boards/beagley/ai/demos/beagley-ai-using-pwm.html).

> NOTE: If you use any GPIO command on the same port the PWM will no longer work.

You must run `sudo beagle-pwm-export --pin hat-08` and then run the `fade.sh` script.
If you use a regular GPIO command you must then reboot the board to reactivate the PWM functionality.

## 02 Algorithm Benchmark

```bash
gcc -o benchmark-csv benchmark-csv.c algorithms.c
./benchmark-csv > benchmark-beagle.csv
```

## 03 Object Detection

Based on [this guide](https://docs.beagleboard.org/boards/beagley/ai/demos/beagley-ai-object-detection-tutorial.html).
Follow the directions in the guide to configure the python virtual environment and machine learning code.

The python script in this repository contains small modification to function with CSI cameras:

1. Modifying the `fourcc` value for the `V4L2` capture backend to `RGGB` to match the CSI camera
2. Logging of capture backend information and outputting the camera frames to file

By default, the CSI camera registers under `/dev/video3` but if this is not the case,
you will need to change the `video_driver_id` in the script.

## 04 Web App

This is an object detection webapp on port 40000.
Inspiration from [this guide](https://medium.com/better-programming/build-a-computer-vision-webapp-flask-opencv-and-mongodb-62a52d38738a)
and [this guide](https://medium.com/@draj0718/opencv-face-detection-deployment-in-flask-web-framework-1a9b9772d9fd)

From the `04-web-app` directory
```bash
conda activate myenv
pip install -r requirements.txt
python app.py --modeldir=TFLite_model
```

# Using an IMX219 CSI Camera

Based on [this tutorial](https://docs.beagleboard.org/boards/beagley/ai/demos/beagley-ai-using-imx219-csi-cameras.html).
The code in this section has been tested specifically with the [Raspberry Pi Camera V2 Module](https://www.raspberrypi.com/products/camera-module-v2/).

If you are used to using webcams this camera is much less "plug and play" and requires more in-depth knowledge of camera capture.
These code snippets are designed to get you up and running without much understanding of what the camera is doing.

### Bootstrap the Camera

You **MUST** run this code **EVERY** time you wish to use the CSI camera after booting or rebooting!
If you get really excited about your new code idea, boot the machine, and forget to initialize the camera
you may waste precious time wondering why your code doesn't work when in fact your camera isn't configured.

> NOTE: You must have enabled the firmware overlay for the CSI camera as described in the above guide
> and reboot once before running the code below.

These commands are necessary to load the appropriate camera drivers and set the output format for use
in OpenCV or other consuming formats.

```bash
sudo beagle-camera-setup
media-ctl -V '"imx219 5-0010":0[fmt:SRGGB8_1X8/640x480 field:none]'
```

You can also change the resolution or output format for more advanced use cases.
To query the available output formats you can run the following:

```bash
v4l2-ctl -d /dev/video3 --list-formats
```

### [**IMPORTANT**] Camera Settings

These settings will set the camera gain and exposure for the camera to a sensible default.
If you find that your image is washed out, too dark or even blank, you may need to tweak these parameters
for your own lighting environment.
If you are not directly observing your output, a hint that these settings are wrong is that your
pipeline (ex. object detection) is running but nothing is being detected or recognized.

Indoor Light
```bash
v4l2-ctl -d /dev/v4l-subdev2 --set-ctrl=digital_gain=2048
v4l2-ctl -d /dev/v4l-subdev2 --set-ctrl=analogue_gain=230
v4l2-ctl -d /dev/v4l-subdev2 --set-ctrl=exposure=1750
```

Natural Light

```bash
v4l2-ctl -d /dev/v4l-subdev2 --set-ctrl=digital_gain=1000
v4l2-ctl -d /dev/v4l-subdev2 --set-ctrl=analogue_gain=100
v4l2-ctl -d /dev/v4l-subdev2 --set-ctrl=exposure=1000
```

## Capturing Test Frames

Run the following command to capture some test frames in `.jpg` format

```bash
gst-launch-1.0 -v v4l2src num-buffers=5 device=/dev/video3 io-mode=dmabuf ! \
    video/x-bayer, width=1920, height=1080, framerate=30/1, format=rggb ! \
    bayer2rgb ! videoconvert ! jpegenc ! \
    multifilesink location="imx219-image-%d.jpg"
```

## Capturing a Test Movie

Run the following command to capture a test movie (100 frames) in `.mp4` format

```bash
gst-launch-1.0 v4l2src device=/dev/video3 num-buffers=100 io-mode=dmabuf ! \
    video/x-bayer, width=640, height=480, format=rggb,depth=8 ! \
    queue ! bayer2rgb ! queue ! videoconvert ! video/x-raw,format=NV12 ! \
    queue ! v4l2h264enc ! queue !  h264parse ! mp4mux  ! filesink location=imx219.mp4
```

## Creating a Virtual Camera

The following can be used to create a virtual camera that outputs to standard formats
that may be expected in downstream applications (ex. Chromium, OBS, VLC, etc.).

In order to run this command, you must install `v4l2loopback` which enables a kernel
module that can create virtual cameras. This requires:

1. Installing the Linux Headers for your current kernel. See [this article](https://docs.beagleboard.org/books/beaglebone-cookbook/07kernel/kernel.html)
   for more information about modifying the kernel.

```bash
sudo apt install linux-headers-`uname -r`
```

2. Install `v4l2loopback-dkms` (Dynamic Kernel Module Support). This allows you to add kernel modules
   without modifying the entire kernel.

```bash
sudo apt-get install v4l2loopback-dkms
```

3. You may need to reload kernel module dependencies with

```bash
sudo depmod -a
```

4. Load the newly installed kernel module

```bash
sudo modprobe v4l2loopback
```

5. Now you can start the virtual camera! This process must be running for the virtual camera to work.
   You can move the process to the background with your preferred method (ex. `screen`, `ctrl+z`, `&`).

```bash
gst-launch-1.0   v4l2src device=/dev/video3 io-mode=dmabuf ! \
    video/x-bayer, width=640, height=480, framerate=30/1, format=rggb,depth=8 ! \
    bayer2rgb ! videoconvert ! video/x-raw, format=NV12 ! \
    v4l2sink device=/dev/video9
```

This will create a virtual camera on `/dev/video9` or index `9` that can be recognized
by downstream applications.

# References

- [CSI IMX219 camera to work with BeagleY-AI](https://forum.beagleboard.org/t/csi-imx219-camera-to-work-with-beagley-ai/41235)
- [Interfacing the RPi camera module 2 with Python on BY-AI](https://forum.beagleboard.org/t/interfacing-the-rpi-camera-module-2-with-python-on-by-ai/41323)

