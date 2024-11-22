import cv2 as cv
import numpy as np
import sys

def people_counter(input_path, output_path):
    """
    Process a video file to count people entering and exiting using OpenCV.

    Args:
        input_path (str): Path to the input video.
        output_path (str): Path to save the processed video.
    """
    cap = cv.VideoCapture(input_path)
    if not cap.isOpened():
        raise Exception("Cannot open the video source.")

    # Read the first frame to get dimensions
    ret, frame = cap.read()
    if not ret:
        raise Exception("Cannot read the first frame of the video.")

    h, w = frame.shape[:2]
    print(f"Video dimensions: {w}x{h}")

    # Initialize video writer
    out = cv.VideoWriter(output_path, cv.VideoWriter_fourcc(*"mp4v"), 30.0, (w, h))

    # Line positions
    line_up = int(2 * h / 5)
    line_down = int(3 * h / 5)
    up_limit = int(h / 5)
    down_limit = int(4 * h / 5)

    # Background subtractor and morphological operations
    fgbg = cv.createBackgroundSubtractorMOG2(detectShadows=True)
    kernel_op = np.ones((3, 3), np.uint8)
    kernel_cl = np.ones((11, 11), np.uint8)

    # Tracking variables
    cnt_up, cnt_down = 0, 0
    persons = []
    pid = 1

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Preprocessing
        fgmask = fgbg.apply(frame)
        _, binarized = cv.threshold(fgmask, 200, 255, cv.THRESH_BINARY)
        mask = cv.morphologyEx(binarized, cv.MORPH_OPEN, kernel_op)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel_cl)

        # Find contours
        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if cv.contourArea(cnt) > (h * w / 250):  # Area threshold
                M = cv.moments(cnt)
                if M["m00"] != 0:
                    cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])

                    # Tracking logic
                    new = True
                    for person in persons:
                        if abs(cx - person["x"]) <= 15 and abs(cy - person["y"]) <= 15:
                            new = False
                            person["x"], person["y"] = cx, cy
                            person["age"] = 0
                            if person["state"] == 0 and cy <= line_up:
                                person["state"] = 1
                                cnt_up += 1
                                print(f"Person {person['id']} crossed going up.")
                            elif person["state"] == 0 and cy >= line_down:
                                person["state"] = 1
                                cnt_down += 1
                                print(f"Person {person['id']} crossed going down.")
                            break

                    if new:
                        persons.append({"id": pid, "x": cx, "y": cy, "age": 0, "state": 0})
                        pid += 1

        # Age and cleanup
        for person in persons:
            person["age"] += 1
        persons = [p for p in persons if p["age"] <= 5]

        # Draw lines and display counts
        cv.line(frame, (0, line_up), (w, line_up), (0, 255, 0), 2)
        cv.line(frame, (0, line_down), (w, line_down), (0, 0, 255), 2)
        cv.putText(frame, f"UP: {cnt_up}", (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv.putText(frame, f"DOWN: {cnt_down}", (10, 80), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Save processed frame
        out.write(frame)

    # Cleanup
    cap.release()
    out.release()
    print(f"Processed video saved to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python PeopleCounter.py <input_video_path> <output_video_path>")
        sys.exit(1)

    input_video = sys.argv[1]
    output_video = sys.argv[2]
    people_counter(input_video, output_video)
