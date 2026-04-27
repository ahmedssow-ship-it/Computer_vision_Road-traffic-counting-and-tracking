
import csv
import json
import os
from datetime import datetime

class TrafficLogger:
    """Génère les logs CSV et JSON des détections."""

    def __init__(self, output_dir: str = "logs", scene_id: str = "scene_01"):
        self.output_dir = output_dir
        self.scene_id   = scene_id
        os.makedirs(output_dir, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_path  = os.path.join(output_dir, f"detections_{ts}.csv")
        self.json_path = os.path.join(output_dir, f"tracking_{ts}.json")

        self.json_log = []
        self._init_csv()

    def _init_csv(self):
        with open(self.csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "scene_id", "frame", "timestamp",
                "track_id", "class", "confidence",
                "x1", "y1", "x2", "y2"
            ])

    def log_frame(self, frame_idx: int, timestamp: str,
                  tracked_objects: list, class_names: dict):
        """Enregistre les détections d'une frame."""

        # CSV
        with open(self.csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            for obj in tracked_objects:
                x1, y1, x2, y2 = obj["bbox"]
                class_name = class_names.get(obj["class_id"], "unknown")
                writer.writerow([
                    self.scene_id, frame_idx, timestamp,
                    obj["track_id"], class_name,
                    round(obj["conf"], 3),
                    x1, y1, x2, y2
                ])

        # JSON
        entry = {
            "scene_id":   self.scene_id,
            "frame":      frame_idx,
            "timestamp":  timestamp,
            "detections": [
                {
                    "track_id":  obj["track_id"],
                    "class":     class_names.get(obj["class_id"], "unknown"),
                    "confidence": round(obj["conf"], 3),
                    "bbox":      obj["bbox"]
                }
                for obj in tracked_objects
            ]
        }
        self.json_log.append(entry)

    def save_json(self):
        """Sauvegarde le fichier JSON complet."""
        with open(self.json_path, "w") as f:
            json.dump(self.json_log, f, indent=2)
        print(f"Logs sauvegardés : {self.csv_path} | {self.json_path}")
