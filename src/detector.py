
from ultralytics import YOLO
import cv2
import numpy as np

class TrafficDetector:
    """Détecteur d'objets de trafic basé sur YOLOv11."""

    CLASSES = {
        0: "person",
        1: "bicycle",
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck"
    }

    COLORS = {
        "person":    (0,   255, 127),
        "bicycle":        (255, 140,   0),
        "car":        (0,   120, 255),
        "motorcycle": (255,   0, 180),
        "bus":     (0,   255, 255),
        "truck":      (180,   0, 255),
    }

    def __init__(self, model_path: str, conf: float = 0.3, iou: float = 0.45):
        self.model = YOLO(model_path)
        self.conf  = conf
        self.iou   = iou

    def detect(self, frame: np.ndarray, selected_classes: list = None):
        """
        Détecte les objets dans une frame.

        Args:
            frame: Image OpenCV (BGR)
            selected_classes: Liste des classes à détecter (None = toutes)

        Returns:
            detections: list de [x1, y1, x2, y2, conf, class_id]
        """
        class_ids = None
        if selected_classes:
            class_ids = [k for k, v in self.CLASSES.items()
                         if v in selected_classes]

        results = self.model.predict(
            source=frame,
            conf=self.conf,
            iou=self.iou,
            classes=class_ids,
            verbose=False
        )[0]

        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf     = float(box.conf[0])
            class_id = int(box.cls[0])
            detections.append([x1, y1, x2, y2, conf, class_id])

        return detections

    def draw_detections(self, frame, tracked_objects):
        """Dessine les bounding boxes et IDs sur la frame."""
        for obj in tracked_objects:
            x1, y1, x2, y2 = obj["bbox"]
            track_id        = obj["track_id"]
            class_name      = obj["class"]
            conf            = obj["conf"]

            color = self.COLORS.get(class_name, (255, 255, 255))

            # Bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Label
            label = f"#{track_id} {class_name} {conf:.2f}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        return frame
            
            
