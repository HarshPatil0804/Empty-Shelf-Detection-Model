import streamlit as st
import cv2
import tempfile
import numpy as np
from ultralytics import YOLO

# -------------------------------
# Load YOLO Model
# -------------------------------
model = YOLO("best.pt")   # keep best.pt in same folder


# -------------------------------
# Function: YOLO + Empty Detection
# -------------------------------
def detect_empty_inside_shelves(frame):
    results = model(frame, verbose=False)
    boxes = results[0].boxes

    annotated_frame = frame.copy()
    empty_count = 0

    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        roi = frame[y1:y2, x1:x2]

        if roi.size == 0:
            continue

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        density = np.sum(edges) / (roi.shape[0] * roi.shape[1])

        #  Empty detection logic
        if density < 6:
            status = "Empty"
            color = (0, 0, 255)
            empty_count += 1
        else:
            status = "Occupied"
            color = (0, 255, 0)

        # Draw bounding box
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 3)

        # Add label
        cv2.putText(
            annotated_frame,
            status,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

    return annotated_frame, empty_count


# -------------------------------
# Streamlit UI
# -------------------------------
st.title("🛒 Empty Shelf Detection (YOLO + Smart Analysis)")

uploaded_file = st.file_uploader("Upload CCTV Video", type=["mp4"])

if uploaded_file:
    st.video(uploaded_file)

    if st.button("Analyze Video"):
        st.write("⏳ Processing...")

        # Save uploaded file
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())

        cap = cv2.VideoCapture(tfile.name)

        count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process every 30th frame (fast demo)
            if count % 30 == 0:
                processed_frame, empty_count = detect_empty_inside_shelves(frame)

                st.image(
                    processed_frame,
                    caption=f"Empty Shelves Detected: {empty_count}",
                    channels="BGR"
                )

            count += 1

        cap.release()

        st.success("✅ Analysis Complete!")
        #  SUMMARY (CORRECT INDENT)
        from collections import Counter
        final_summary = Counter(all_results)

        st.subheader("📊 Summary")
        st.write(dict(final_summary))
