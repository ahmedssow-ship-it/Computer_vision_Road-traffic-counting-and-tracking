
import numpy as np
from collections import defaultdict

class ByteTracker:
    """
    Implémentation simplifiée de ByteTrack.
    Pour la version complète : pip install bytetracker
    """

    def __init__(self, max_age: int = 30, min_hits: int = 3, iou_thresh: float = 0.3):
        self.max_age    = max_age
        self.min_hits   = min_hits
        self.iou_thresh = iou_thresh
        self.tracks     = []
        self.next_id    = 1
        self.frame_count = 0

    def update(self, detections: list, class_ids: list) -> list:
        """
        Met à jour les tracks avec les nouvelles détections.

        Args:
            detections: [[x1,y1,x2,y2,conf,class_id], ...]
            class_ids: liste des class_ids correspondants

        Returns:
            tracked: [{"track_id", "bbox", "class_id", "conf"}, ...]
        """
        self.frame_count += 1

        if len(detections) == 0:
            # Vieillir les tracks existants
            for t in self.tracks:
                t["age"] += 1
            self.tracks = [t for t in self.tracks if t["age"] <= self.max_age]
            return []

        det_boxes = np.array([[d[0], d[1], d[2], d[3]] for d in detections])
        det_confs  = np.array([d[4] for d in detections])
        det_classes = np.array([d[5] for d in detections])

        # Séparer haute et basse confiance (ByteTrack)
        high_mask = det_confs >= 0.5
        low_mask  = ~high_mask

        high_dets = det_boxes[high_mask]
        low_dets  = det_boxes[low_mask]

        # Associer avec les tracks existants
        matched, unmatched_dets, unmatched_tracks = self._associate(
            high_dets, self.tracks
        )

        # Mettre à jour les tracks matchés
        active_tracks = []
        for det_idx, trk_idx in matched:
            self.tracks[trk_idx]["bbox"]    = high_dets[det_idx].tolist()
            self.tracks[trk_idx]["conf"]    = float(det_confs[high_mask][det_idx])
            self.tracks[trk_idx]["class_id"] = int(det_classes[high_mask][det_idx])
            self.tracks[trk_idx]["hits"]   += 1
            self.tracks[trk_idx]["age"]     = 0
            active_tracks.append(self.tracks[trk_idx])

        # Créer nouveaux tracks pour détections non matchées
        for det_idx in unmatched_dets:
            new_track = {
                "track_id": self.next_id,
                "bbox":     high_dets[det_idx].tolist(),
                "conf":     float(det_confs[high_mask][det_idx]),
                "class_id": int(det_classes[high_mask][det_idx]),
                "hits":     1,
                "age":      0,
            }
            self.tracks.append(new_track)
            self.next_id += 1

        # Vieillir les tracks non matchés
        for trk_idx in unmatched_tracks:
            self.tracks[trk_idx]["age"] += 1

        # Supprimer tracks trop vieux
        self.tracks = [t for t in self.tracks if t["age"] <= self.max_age]

        # Retourner seulement les tracks confirmés
        return [t for t in active_tracks if t["hits"] >= self.min_hits]

    def _iou(self, box1, box2):
        """Calcule l'IoU entre deux boîtes."""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        inter = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2]-box1[0]) * (box1[3]-box1[1])
        area2 = (box2[2]-box2[0]) * (box2[3]-box2[1])
        union = area1 + area2 - inter

        return inter / union if union > 0 else 0

    def _associate(self, detections, tracks):
        """Associe détections et tracks par IoU."""
        if len(tracks) == 0:
            return [], list(range(len(detections))), []
        if len(detections) == 0:
            return [], [], list(range(len(tracks)))

        iou_matrix = np.zeros((len(detections), len(tracks)))
        for d, det in enumerate(detections):
            for t, trk in enumerate(tracks):
                iou_matrix[d, t] = self._iou(det, trk["bbox"])

        matched, unmatched_dets, unmatched_trks = [], [], []

        # Greedy matching
        while iou_matrix.max() > self.iou_thresh:
            d, t = np.unravel_index(iou_matrix.argmax(), iou_matrix.shape)
            matched.append((d, t))
            iou_matrix[d, :] = -1
            iou_matrix[:, t] = -1

        matched_d = {m[0] for m in matched}
        matched_t = {m[1] for m in matched}
        unmatched_dets = [d for d in range(len(detections)) if d not in matched_d]
        unmatched_trks = [t for t in range(len(tracks))    if t not in matched_t]

        return matched, unmatched_dets, unmatched_trks
            
        