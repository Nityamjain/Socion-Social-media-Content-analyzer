from flask import Flask, request, render_template, Response, jsonify
from backend.flow import main_pipeline
import uuid
import os
import json
import time


app = Flask(__name__, template_folder="templates", static_folder="static")


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Store uploaded file locations
TASKS = {}



def convert_non_json(obj):
    """Ensure generator / custom objects become JSON-serializable."""
    if hasattr(obj, "__iter__") and not isinstance(obj, (str, dict, list)):
        return list(obj)
    return str(obj)



@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# app.py (add this route)
@app.route("/dashboard")
def dashboard():
    # Optional: pass result via session or localStorage (we use localStorage)
    return render_template("dashboard.html")



# ----------------------------------------------------
# 1️⃣ UPLOAD FILE
# ----------------------------------------------------
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")


    if not file:
        return jsonify({"error": "No file uploaded"}), 400


    if file.filename == "":
        return jsonify({"error": "Invalid file name"}), 400


    task_id = str(uuid.uuid4())
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)


    try:
        file.save(filepath)
        TASKS[task_id] = filepath
        print(f"[INFO] File saved: {filepath}")
    except Exception as e:
        print("[ERROR] Couldn't save file:", e)
        return jsonify({"error": "Failed to save file"}), 500


    return jsonify({"task_id": task_id})



# ----------------------------------------------------
# 2️⃣ SSE STREAM — SEND JSON EVENTS
# ----------------------------------------------------
@app.route("/analyze_stream/<task_id>", methods=["GET"])
def analyze_stream(task_id):
    if task_id not in TASKS:
        return Response(
            "event: error\ndata: Invalid Task ID\n\n",
            mimetype="text/event-stream"
        )


    filepath = TASKS[task_id]


    def send_progress(step_text, progress_value):
        data = json.dumps({"step": step_text, "progress": progress_value})
        return f"event: progress\ndata: {data}\n\n"


    def generate():
        try:
            # Stream from main_pipeline generator
            for event in main_pipeline(filepath):
                try:
                    data = json.loads(event)
                    if isinstance(data, dict) and "result" in data:
                        result_json = json.dumps(data["result"], default=convert_non_json)
                        yield f"event: result\ndata: {result_json}\n\n"
                        yield "event: done\ndata: complete\n\n"
                        break
                    else:
                        # Progress step
                        step = data.get("step", "Processing...")
                        progress = data.get("progress", 0)
                        yield send_progress(step, progress)
                except json.JSONDecodeError:
                    # Fallback for non-JSON yields (if any)
                    yield send_progress(str(event), 0)
                except Exception as e:
                    yield f"event: error\ndata: {str(e)}\n\n"
                    break


            # Cleanup
            if os.path.exists(filepath):
                os.remove(filepath)
            if task_id in TASKS:
                del TASKS[task_id]


        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"


    return Response(generate(), mimetype="text/event-stream")



if __name__ == "__main__":
    app.run(debug=True)
