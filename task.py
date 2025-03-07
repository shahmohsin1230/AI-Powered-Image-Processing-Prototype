import cv2
import mediapipe as mp
import numpy as np

def apply_mosaic(image, x, y, w, h, mosaic_size=10):
    """Apply mosaic effect to a specific region of the image"""
    roi = image[y:y+h, x:x+w]

    small = cv2.resize(roi, (mosaic_size, mosaic_size), interpolation=cv2.INTER_NEAREST)
    mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    image[y:y+h, x:x+w] = mosaic
    return image

def process_image(image_path):
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not load image")
        return

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = face_mesh.process(image_rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w = image.shape[:2]

            left_eye_indices = [33, 160, 158, 133, 153, 144]
            left_eye_points = []

            right_eye_indices = [362, 385, 387, 263, 373, 380]
            right_eye_points = []

            for idx in left_eye_indices:
                lm = face_landmarks.landmark[idx]
                x = int(lm.x * w)
                y = int(lm.y * h)
                left_eye_points.append([x, y])

            for idx in right_eye_indices:
                lm = face_landmarks.landmark[idx]
                x = int(lm.x * w)
                y = int(lm.y * h)
                right_eye_points.append([x, y])

            left_eye_points = np.array(left_eye_points)
            right_eye_points = np.array(right_eye_points)

            left_x_min = np.min(left_eye_points[:, 0])
            left_x_max = np.max(left_eye_points[:, 0])
            left_y_min = np.min(left_eye_points[:, 1])
            left_y_max = np.max(left_eye_points[:, 1])

            right_x_min = np.min(right_eye_points[:, 0])
            right_x_max = np.max(right_eye_points[:, 0])
            right_y_min = np.min(right_eye_points[:, 1])
            right_y_max = np.max(right_eye_points[:, 1])

            padding = 10
            left_x = max(0, left_x_min - padding)
            left_y = max(0, left_y_min - padding)
            left_w = min(w - left_x, (left_x_max - left_x_min) + 2*padding)
            left_h = min(h - left_y, (left_y_max - left_y_min) + 2*padding)

            right_x = max(0, right_x_min - padding)
            right_y = max(0, right_y_min - padding)
            right_w = min(w - right_x, (right_x_max - right_x_min) + 2*padding)
            right_h = min(h - right_y, (right_y_max - right_y_min) + 2*padding)

            image = apply_mosaic(image, left_x, left_y, left_w, left_h)
            image = apply_mosaic(image, right_x, right_y, right_w, right_h)

    cv2.imwrite('processed_image2.jpg', image)
    print("Processed image saved as 'processed_image.jpg'")

    face_mesh.close()

if __name__ == "__main__":
    image_path = '/content/input_image2.jpg'
    process_image(image_path)
