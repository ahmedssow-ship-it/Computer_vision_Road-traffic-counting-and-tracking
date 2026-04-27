
from collections import defaultdict

class ObjectCounter:
    """Comptage d'objets uniques par classe."""

    def __init__(self):
        self.seen_ids    = defaultdict(set)   # class → set of track_ids
        self.active      = defaultdict(int)   # class → count actif dans la frame

    def update(self, tracked_objects: list, class_names: dict):
        """
        Met à jour les compteurs.

        Args:
            tracked_objects: sortie du tracker
            class_names: {class_id: class_name}
        """
        self.active = defaultdict(int)

        for obj in tracked_objects:
            class_name = class_names.get(obj["class_id"], "unknown")
            track_id   = obj["track_id"]

            self.seen_ids[class_name].add(track_id)
            self.active[class_name] += 1

    def get_totals(self) -> dict:
        """Retourne le total d'objets uniques par classe."""
        return {cls: len(ids) for cls, ids in self.seen_ids.items()}

    def get_active(self) -> dict:
        """Retourne le nombre d'objets actifs dans la frame courante."""
        return dict(self.active)

    def reset(self):
        self.seen_ids.clear()
        self.active.clear()
        
    