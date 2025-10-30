# video_analyzer.py
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import math

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    """Calculate angle (in degrees) formed by three points a-b-c."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle

def analyze_video(video_path):
    """
    Main analysis function. Takes a video file path and returns a 
    dictionary with graph data and text suggestions.
    """
    
    angles_data = []
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    # We initialize pose inside the function
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        
        frame_no = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_no += 1
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(img_rgb)
            
            if not result.pose_landmarks:
                continue

            lm = result.pose_landmarks.landmark
            
            # Landmark indices
            R_SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
            R_ELBOW = mp_pose.PoseLandmark.RIGHT_ELBOW.value
            R_WRIST = mp_pose.PoseLandmark.RIGHT_WRIST.value
            L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
            L_ELBOW = mp_pose.PoseLandmark.LEFT_ELBOW.value
            L_WRIST = mp_pose.PoseLandmark.LEFT_WRIST.value
            R_HIP = mp_pose.PoseLandmark.RIGHT_HIP.value
            R_KNEE = mp_pose.PoseLandmark.RIGHT_KNEE.value
            R_ANKLE = mp_pose.PoseLandmark.RIGHT_ANKLE.value
            L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
            L_KNEE = mp_pose.PoseLandmark.LEFT_KNEE.value
            L_ANKLE = mp_pose.PoseLandmark.LEFT_ANKLE.value

            def pt(i): return (lm[i].x, lm[i].y)

            # Calculate angles
            right_elbow = calculate_angle(pt(R_SHOULDER), pt(R_ELBOW), pt(R_WRIST))
            left_elbow  = calculate_angle(pt(L_SHOULDER), pt(L_ELBOW), pt(L_WRIST))
            right_knee  = calculate_angle(pt(R_HIP), pt(R_KNEE), pt(R_ANKLE))
            left_knee   = calculate_angle(pt(L_HIP), pt(L_KNEE), pt(L_ANKLE))

            angles_data.append({
                "frame": frame_no,
                "time_sec": frame_no / fps,
                "right_elbow": right_elbow,
                "left_elbow": left_elbow,
                "right_knee": right_knee,
                "left_knee": left_knee
            })

    cap.release()
    
    # --- IMPORTANT: Check if any data was collected ---
    if not angles_data:
        return {"error": "No pose detected in the video. Please try again."}

    df = pd.DataFrame(angles_data)

    # --- 1. Prepare Data for Graphs (to send to JavaScript) ---
    graph_data = {
        "time_sec": df['time_sec'].round(2).tolist(),
        "left_elbow": df['left_elbow'].round(2).tolist(),
        "right_elbow": df['right_elbow'].round(2).tolist(),
        "left_knee": df['left_knee'].round(2).tolist(),
        "right_knee": df['right_knee'].round(2).tolist()
    }

    # --- 2. Prepare Elbow Report ---
    left_elbow_angles = df['left_elbow'].to_numpy()
    right_elbow_angles = df['right_elbow'].to_numpy()
    avg_left_angle = np.mean(left_elbow_angles)
    avg_right_angle = np.mean(right_elbow_angles)
    symmetry_score = 100 - abs(avg_left_angle - avg_right_angle)
    range_of_motion = np.max(left_elbow_angles) - np.min(left_elbow_angles)

    elbow_report = []
    elbow_report.append(f"Average left elbow angle: {avg_left_angle:.2f}°")
    elbow_report.append(f"Average right elbow angle: {avg_right_angle:.2f}°")
    elbow_report.append(f"Symmetry score: {symmetry_score:.2f}%")
    elbow_report.append(f"Range of motion: {range_of_motion:.2f}°")

    if symmetry_score > 90:
        elbow_report.append("✅ The movement is well balanced between left and right sides.")
    elif symmetry_score > 70:
        elbow_report.append("⚠️ Minor asymmetry observed — continue targeted exercises.")
    else:
        elbow_report.append("❌ Significant imbalance detected — consult therapist guidance.")

    # --- 3. Prepare Knee Report ---
    left_knee_angles = df['left_knee'].to_numpy()
    right_knee_angles = df['right_knee'].to_numpy()
    avg_left_knee = np.mean(left_knee_angles)
    avg_right_knee = np.mean(right_knee_angles)
    symmetry_knee = 100 - abs(avg_left_knee - avg_right_knee)
    range_knee = np.max(left_knee_angles) - np.min(left_knee_angles)

    knee_report = []
    knee_report.append(f"Average left knee angle: {avg_left_knee:.2f}°")
    knee_report.append(f"Average right knee angle: {avg_right_knee:.2f}°")
    knee_report.append(f"Symmetry score: {symmetry_knee:.2f}%")
    knee_report.append(f"Range of motion: {range_knee:.2f}°")
    
    if symmetry_knee > 90:
        knee_report.append("✅ Knees are moving symmetrically — great control observed.")
    else:
        knee_report.append("❌ Significant difference between knees — requires physiotherapy attention.")

    # --- 4. Assemble Final Results Dictionary ---
    final_results = {
        "graph_data": graph_data,
        "suggestions": {
            "elbow_report": elbow_report,
            "knee_report": knee_report
        }
    }
    
    return final_results