# file: PeopleCounter.py
import numpy as np
import cv2 as cv
import logging
import time
from Person import MyPerson

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename="log.txt", format="%(asctime)s - %(levelname)s - %(message)s")

# Constants and Configuration
VIDEO_SOURCE = "/Users/apple/Desktop/Python-Project/TestVideo.mp4"  # Update with your video file path
AREA_DIVISOR = 250  # Threshold divisor for object size
MAX_PERSON_AGE = 5  # Max age for tracking objects
EXIT_KEY = 'q'      # Key to exit the video

def initialize_video(video_source):
    """Initialize and verify video source."""
    cap = cv.VideoCapture(video_source)
    if not cap.isOpened():
        raise FileNotFoundError(f"Error: Cannot open video source {video_source}.")
    logging.info(f"Video {video_source} loaded successfully.")
    return cap

def get_video_dimensions(cap):
    """Retrieve video dimensions and the first frame."""
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("Error: Cannot read the first frame of the video.")
    h, w = frame.shape[:2]
    logging.info(f"Video dimensions: {w}x{h}")
    return h, w, frame

def calculate_lines(h, w):
    """Dynamically calculate entry/exit lines based on height."""
    line_up = int(2 * h / 5)
    line_down = int(3 * h / 5)
    up_limit = int(h / 5)
    down_limit = int(4 * h / 5)
    logging.debug(f"Lines calculated: Up ({line_up}), Down ({line_down}), Limits ({up_limit}, {down_limit})")
    return line_up, line_down, up_limit, down_limit

def preprocess_frame(frame, fgbg, kernel_op, kernel_cl):
    """Preprocess frame with background subtraction and morphological filters."""
    fgmask = fgbg.apply(frame)
    _, binarized = cv.threshold(fgmask, 200, 255, cv.THRESH_BINARY)
    mask = cv.morphologyEx(binarized, cv.MORPH_OPEN, kernel_op)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel_cl)
    return mask

def draw_lines(frame, line_positions, colors):
    """Draw lines on the frame for visualization."""
    for line, color in zip(line_positions, colors):
        cv.polylines(frame, [line], isClosed=False, color=color, thickness=2)
    return frame

def main():
    try:
        # Initialize video
        cap = initialize_video(VIDEO_SOURCE)
        h, w, first_frame = get_video_dimensions(cap)
        area_threshold = (h * w) / AREA_DIVISOR
        logging.info(f"Area Threshold: {area_threshold}")

        # Calculate lines
        line_up, line_down, up_limit, down_limit = calculate_lines(h, w)

        # Background subtractor and kernels
        fgbg = cv.createBackgroundSubtractorMOG2(detectShadows=True)
        kernel_op = np.ones((3, 3), np.uint8)
        kernel_cl = np.ones((11, 11), np.uint8)

        # Line coordinates
        line_positions = [
            np.array([[0, line_down], [w, line_down]], np.int32),
            np.array([[0, line_up], [w, line_up]], np.int32),
        ]
        line_colors = [(255, 0, 0), (0, 0, 255)]  # Colors for lines (down, up)

        # Variables
        persons = []
        pid = 1
        cnt_up, cnt_down = 0, 0
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                logging.info(f"End of video or cannot read the frame at frame {frame_count}")
                break

            logging.debug(f"Processing frame {frame_count}")
            frame_count += 1

            # Preprocess frame
            try:
                mask = preprocess_frame(frame, fgbg, kernel_op, kernel_cl)
            except Exception as e:
                logging.error(f"Error during frame preprocessing: {e}")
                break

            # Find contours
            contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                if cv.contourArea(cnt) > area_threshold:
                    M = cv.moments(cnt)
                    if M["m00"] != 0:
                        cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                        x, y, w, h = cv.boundingRect(cnt)

                        new = True
                        for person in persons:
                            if abs(x - person.get_x()) <= w and abs(y - person.get_y()) <= h:
                                new = False
                                person.update_position(cx, cy)

                                if person.moving_up(line_down, line_up):
                                    cnt_up += 1
                                    logging.info(f"Person {person.get_id()} crossed going up.")
                                elif person.moving_down(line_down, line_up):
                                    cnt_down += 1
                                    logging.info(f"Person {person.get_id()} crossed going down.")
                                break

                            if person.is_timed_out():
                                persons.remove(person)

                        if new:
                            p = MyPerson(pid, cx, cy, MAX_PERSON_AGE)
                            persons.append(p)
                            pid += 1

            # Draw lines and trajectories
            frame = draw_lines(frame, line_positions, line_colors)
            for person in persons:
                cv.putText(frame, f"ID: {person.get_id()}", (person.get_x(), person.get_y()), cv.FONT_HERSHEY_SIMPLEX, 0.5, person.get_color(), 1)

            # Display counts
            cv.putText(frame, f"UP: {cnt_up}", (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv.putText(frame, f"DOWN: {cnt_down}", (10, 90), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Show frame
            cv.imshow("Frame", frame)

            # Break on EXIT_KEY
            if cv.waitKey(30) & 0xFF == ord(EXIT_KEY):
                break

        cap.release()
        cv.destroyAllWindows()

    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        raise

if __name__ == "__main__":
    main()
