
# import cv2
# import os
# import numpy as np
# from predict_image import predict_image_model
# import tempfile

# def analyze_video(video_path):
#     cap = cv2.VideoCapture(video_path)
#     frame_count = 0
#     real_votes = 0
#     fake_votes = 0

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         if frame_count % 10 == 0:
#             # Convert frame to RGB and save to temporary file
#             temp_frame_path = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name
#             cv2.imwrite(temp_frame_path, frame)

#             verdict, real_score, fake_score = predict_image_model(temp_frame_path)
#             os.remove(temp_frame_path)  # cleanup temp file

#             if verdict == "REAL":
#                 real_votes += 1
#             else:
#                 fake_votes += 1

#         frame_count += 1

#     cap.release()
#     total_votes = real_votes + fake_votes
#     if total_votes == 0:
#         return {"verdict": "Unknown", "real_percent": 0, "fake_percent": 0}

#     real_percent = round((real_votes / total_votes) * 100, 2)
#     fake_percent = round((fake_votes / total_votes) * 100, 2)
#     final_verdict = "REAL" if real_votes > fake_votes else "FAKE"

#     return {"verdict": final_verdict, "real_percent": real_percent, "fake_percent": fake_percent}


# import cv2
# import tempfile
# import numpy as np
# from predict_image import predict_image_model

# def analyze_video(video_bytes):
#     # Write video bytes to a temp file for OpenCV
#     with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp:
#         tmp.write(video_bytes)
#         tmp.flush()
#         cap = cv2.VideoCapture(tmp.name)

#         frame_count = 0
#         real_votes = 0
#         fake_votes = 0

#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             # Process every 10th frame (speed up)
#             if frame_count % 10 == 0:
#                 _, buffer = cv2.imencode('.jpg', frame)
#                 frame_bytes = buffer.tobytes()

#                 # Predict single frame
#                 verdict, real_score, fake_score = predict_image_model(frame_bytes)

#                 if verdict == "REAL":
#                     real_votes += 1
#                 else:
#                     fake_votes += 1

#             frame_count += 1

#         cap.release()

#     total_votes = real_votes + fake_votes
#     if total_votes == 0:
#         return {"verdict": "Unknown", "real_percent": 0, "fake_percent": 0}

#     real_percent = round((real_votes / total_votes) * 100, 2)
#     fake_percent = round((fake_votes / total_votes) * 100, 2)
#     final_verdict = "REAL" if real_votes > fake_votes else "FAKE"

#     return {"verdict": final_verdict, "real_percent": real_percent, "fake_percent": fake_percent}




import cv2
import os
import tempfile
from predict_image import predict_image_model  # your existing image prediction function

def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    real_votes = 0
    fake_votes = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % 10 == 0:
            # Save frame to temp file
            temp_frame_path = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False).name
            cv2.imwrite(temp_frame_path, frame)

            verdict, real_score, fake_score = predict_image_model(temp_frame_path)
            os.remove(temp_frame_path)

            if verdict == "REAL":
                real_votes += 1
            else:
                fake_votes += 1

        frame_count += 1

    cap.release()

    total_votes = real_votes + fake_votes
    if total_votes == 0:
        return {"verdict": "Unknown", "real_percent": 0, "fake_percent": 0}

    real_percent = round((real_votes / total_votes) * 100, 2)
    fake_percent = round((fake_votes / total_votes) * 100, 2)
    final_verdict = "REAL" if real_votes > fake_votes else "FAKE"

    return {"verdict": final_verdict, "real_percent": real_percent, "fake_percent": fake_percent}
