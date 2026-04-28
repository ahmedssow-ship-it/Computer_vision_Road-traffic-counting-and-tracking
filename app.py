from flask import (Flask, render_template, request,
                   Response, jsonify)
from werkzeug.utils import secure_filename
from huggingface_hub import hf_hub_download
import cv2, os, json, time
from src.detector import TrafficDetector
from src.tracker  import ByteTracker
from src.counter  import ObjectCounter
from src.logger   import TrafficLogger

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("models", exist_ok=True)

ALLOWED_EXT = {"mp4", "avi", "mov", "mkv"}

# ── Chargement du modèle ──────────────────────────────────────────────────────
def load_model():
    model_path = "models/traffic_yolo11_best.pt"

    if not os.path.exists(model_path):
        print("⬇️  Downloading model from HuggingFace Hub...")
        model_path = hf_hub_download(
            repo_id   = "AhmedSouley01/traffic-yolo11",
            filename  = "traffic_yolo11_best.pt",
            local_dir = "models",
            token     = os.getenv("HF_TOKEN")
        )
        print("✅ Model downloaded successfully!")
    else:
        print("✅ Model loaded from local cache!")

    return model_path

MODEL_PATH = load_model()

# ── État global ───────────────────────────────────────────────────────────────
session_state = {
    "running":          False,
    "video_source":     None,
    "selected_classes": [],
    "stats":            {},
    "active":           {},
    "frame_count":      0,
    "no_object":        False,
}

detector = TrafficDetector(MODEL_PATH)
tracker  = ByteTracker()
counter  = ObjectCounter()
logger   = None

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", classes=list(detector.CLASSES.values()))

@app.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "Aucun fichier fourni"}), 400
    file = request.files["video"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Format non supporté"}), 400
    filename = secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    return jsonify({"success": True, "path": path, "filename": filename})

@app.route("/start", methods=["POST"])
def start_detection():
    global tracker, counter, logger, session_state
    data             = request.get_json()
    video_source     = data.get("video_source")
    selected_classes = data.get("classes", list(detector.CLASSES.values()))
    scene_id         = data.get("scene_id", "scene_01")
    tracker  = ByteTracker()
    counter  = ObjectCounter()
    logger   = TrafficLogger(scene_id=scene_id)
    session_state.update({
        "running":          True,
        "video_source":     video_source,
        "selected_classes": selected_classes,
        "stats":            {},
        "active":           {},
        "frame_count":      0,
        "no_object":        False,
    })
    return jsonify({"success": True})

@app.route("/stop", methods=["POST"])
def stop_detection():
    session_state["running"] = False
    if logger:
        logger.save_json()
    return jsonify({"success": True, "stats": session_state["stats"]})

@app.route("/stats")
def get_stats():
    return jsonify({
        "totals":      session_state["stats"],
        "active":      session_state["active"],
        "frame_count": session_state["frame_count"],
        "no_object":   session_state["no_object"],
    })

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/live")
def live():
    return render_template("live.html")

@app.route("/dashboard")
def dashboard():
    log_files = []
    if os.path.exists("logs"):
        log_files = [f for f in os.listdir("logs") if f.endswith(".json")]
    return render_template("dashboard.html", log_files=log_files)

@app.route("/logs/<filename>")
def get_log(filename):
    path = os.path.join("logs", filename)
    if os.path.exists(path):
        with open(path) as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Fichier introuvable"}), 404

# ── Stream vidéo ──────────────────────────────────────────────────────────────
def generate_frames():
    source = session_state["video_source"]
    if not source:
        return

    cap = cv2.VideoCapture(source)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frame_idx = 0

    while cap.isOpened() and session_state["running"]:
        ret, frame = cap.read()
        if not ret:
            break

        seconds   = frame_idx / fps
        timestamp = f"{int(seconds//60):02d}:{seconds%60:05.2f}"

        detections     = detector.detect(frame, session_state["selected_classes"])
        class_ids_list = [d[5] for d in detections]
        tracked        = tracker.update(detections, class_ids_list)

        counter.update(tracked, detector.CLASSES)

        if logger:
            logger.log_frame(frame_idx, timestamp, tracked, detector.CLASSES)

        session_state["stats"]       = counter.get_totals()
        session_state["active"]      = counter.get_active()
        session_state["frame_count"] = frame_idx
        session_state["no_object"]   = len(tracked) == 0

        tracked_for_draw = [
            {
                "bbox":     t["bbox"],
                "track_id": t["track_id"],
                "class":    detector.CLASSES.get(t["class_id"], "unknown"),
                "conf":     t["conf"],
            }
            for t in tracked
        ]
        annotated = detector.draw_detections(frame.copy(), tracked_for_draw)
        annotated = _draw_counters(annotated, counter.get_active(),
                                   session_state["no_object"])

        _, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

        frame_idx += 1
        time.sleep(1 / fps)

    cap.release()
    session_state["running"] = False

def _draw_counters(frame, active_counts, no_object):
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (250, 30 + 25*max(len(active_counts),1)), (0,0,0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

    y = 35
    cv2.putText(frame, "ACTIVE OBJECTS", (15, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    y += 25

    if no_object:
        cv2.putText(frame, "No object detected", (15, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,100,255), 2)
    else:
        for cls, count in active_counts.items():
            color = detector.COLORS.get(cls, (255,255,255))
            cv2.putText(frame, f"{cls}: {count}", (15, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
            y += 25

    return frame

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=7860)