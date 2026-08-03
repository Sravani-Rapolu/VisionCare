import cv2
from modules.camera import initialize_camera, read_frame
from modules.preprocessing import preprocess_frame
from modules.multi_person_posture import detect_multiple_postures

def main():
    cap = initialize_camera()

    while True:
        ret, frame = read_frame(cap)
        if not ret:
            break

        frame = preprocess_frame(frame)

        frame = detect_multiple_postures(frame)

        cv2.imshow("VisionCare Multi-Person Monitoring", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
