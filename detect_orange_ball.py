from flask import Flask, Response
import cv2
import numpy as np

# Initialize the Flask app
app = Flask(__name__)

# Initialize the camera
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Set width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Set height

def generate_frames():
    """
    Generator function that yields video frames with orange ball detection applied.
    """
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Convert frame to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define range of orange color in HSV
        lower_orange = np.array([5, 100, 100])
        upper_orange = np.array([15, 255, 255])

        # Apply Gaussian Blur to reduce noise
        blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

        # Create a mask for the orange color
        mask = cv2.inRange(hsv, lower_orange, upper_orange)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw contours around detected orange objects
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1690:  # Adjust this threshold for your ball size
                # Approximate contour to check if it's round
                approx = cv2.approxPolyDP(contour, 0.015 * cv2.arcLength(contour, True), True)
                if len(approx) > 8:  # Check for circular shape
                    # Draw the contour on the original frame
                    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 3)

        # JPEG image
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            break

        # Convert to bytes and yield
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """
    Flask route to serve the video stream.
    """
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """
    Default route to display a simple webpage with the video stream.
    """
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Orange Ball Detection</title>
    </head>
    <body>
        <h1>Live Video Stream: Orange Ball Detection</h1>
        <img src="/video_feed" width="640" height="480">
    </body>
    </html>
    '''

# used only if running detect_orange_ball.py by itself
def run_flask_app():
    app.run(host="0.0.0.0", port=5000, debug=False)

