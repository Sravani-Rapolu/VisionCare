from flask import Flask, render_template_string, request, Response, redirect, url_for
from modules.camera import initialize_camera, read_frame
from modules.preprocessing import preprocess_frame
from modules.multi_person_posture import detect_multiple_postures
from modules.fall_detection import detect_fall
from modules.database import log_event, init_db
import sqlite3
import cv2
import uuid
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
init_db()

def gen_frames():
    cap = initialize_camera()
    while True:
        ret, frame = read_frame(cap)
        if not ret:
            break
        frame = preprocess_frame(frame)
        frame = detect_multiple_postures(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    cap.release()

@app.route("/")
def home():
    conn = sqlite3.connect("logs/events.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY id DESC")
    events = cursor.fetchall()
    conn.close()

    html = """
    <style>
      body{font-family:'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:20px}
      .page{max-width:1100px;margin:auto}
      .card{background:#172a49;border:1px solid #294069;border-radius:12px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.35);}
      h1,h2{margin:0 0 12px}
      a{color:#60a5fa;text-decoration:none;font-weight:600}
      a:hover{text-decoration:underline}
      .toolbar{display:flex;align-items:center;gap:12px;margin-bottom:14px;flex-wrap:wrap}
      input{border:1px solid #334155;border-radius:8px;padding:8px 10px;background:#0f172a;color:#f8fafc}
      button{cursor:pointer;border:none;border-radius:8px;padding:10px 14px;background:#2563eb;color:#fff;font-weight:600}
      table{width:100%;border-collapse:collapse;margin-top:10px}
      th,td{text-align:left;padding:10px;border-bottom:1px solid #334155}
      th{background:#1e3a60;color:#bfdbfe}
      tr:nth-child(even){background:#142b4a}
      @media (max-width:768px){.toolbar{flex-direction:column;align-items:flex-start}}
    </style>
    <script>
      function filterEvents(){
        const input = document.getElementById('eventFilter').value.toLowerCase();
        const rows = document.querySelectorAll('#eventsTable tbody tr');
        rows.forEach(row => {
          const text = row.innerText.toLowerCase();
          row.style.display = text.includes(input) ? '' : 'none';
        });
      }
      function clearFilter(){
        document.getElementById('eventFilter').value = '';
        filterEvents();
      }
    </script>
    <div class="page">
      <div class="card">
        <h1>VisionCare Monitoring Dashboard</h1>
        <div class="toolbar">
          <a href='/live'>Live Monitoring</a>
          <a href='/upload'>Upload Video</a>
          <button onclick='location.reload()'>Refresh</button>
          <input id='eventFilter' type='text' placeholder='Filter events by text...' oninput='filterEvents()'>
          <button onclick='clearFilter()'>Clear</button>
        </div>
        <h2>Event Log</h2>
        <table id='eventsTable'>
          <thead>
            <tr><th>ID</th><th>Event</th><th>Time</th></tr>
          </thead>
          <tbody>
          {% for event in events %}
            <tr>
              <td>{{event[0]}}</td>
              <td>{{event[1]}}</td>
              <td>{{event[2]}}</td>
            </tr>
          {% endfor %}
          </tbody>
        </table>
      </div>
    </div>
    """
    return render_template_string(html, events=events)

@app.route('/live')
def live_view():
    html = """
    <style>
      body{font-family:'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:20px}
      .page{max-width:920px;margin:auto}
      .card{background:#1c2e4f;border:1px solid #2f4d77;border-radius:12px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.35);}
      .toolbar{display:flex;gap:10px;align-items:center;margin-bottom:12px}
      button{cursor:pointer;border:none;border-radius:8px;padding:8px 12px;background:#2563eb;color:#fff;font-weight:600}
      a{color:#60a5fa;text-decoration:none}
    </style>
    <div class='page'>
      <div class='card'>
        <div class='toolbar'>
          <a href='/'>← Back</a>
          <button onclick='document.location.reload(true)'>Refresh Stream</button>
        </div>
        <h2>Live Monitoring</h2>
        <p>Real-time patient monitoring with fall and movement detection:</p>
        <img src='/video_feed' style='max-width:100%;border-radius:10px;border:2px solid #2f5294;' />
      </div>
    </div>
    """
    return render_template_string(html)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        if 'video' not in request.files:
            return "No file part"
        file = request.files['video']
        if file.filename == '':
            return "No selected file"

        filename = f"{uuid.uuid4().hex}_{file.filename}"
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(upload_path)

        cap = cv2.VideoCapture(upload_path)
        if not cap.isOpened():
            return "Failed to open uploaded video"

        out_filename = f"processed_{uuid.uuid4().hex}.mp4"
        output_path = os.path.join(OUTPUT_FOLDER, out_filename)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        summary = {"falls": 0, "rapid_movements": 0, "frames": 0}
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = preprocess_frame(frame)
            processed_frame, stats = detect_multiple_postures(frame, return_stats=True)
            summary["falls"] += stats.get("falls", 0)
            summary["rapid_movements"] += stats.get("rapid_movements", 0)
            summary["frames"] += 1
            writer.write(processed_frame)
        
        # Log events if detected
        if summary["falls"] > 0:
            log_event(f"🚨 CRITICAL: Fall detected - {summary['falls']} instances in uploaded video")
        if summary["rapid_movements"] > 0:
            log_event(f"⚠️ WARNING: Rapid bed movements detected - {summary['rapid_movements']} instances")
        log_event(f"✓ Video processed: {summary['frames']} frames analyzed")

        cap.release()
        writer.release()

        return redirect(url_for('show_processed', filename=out_filename,
                                falls=summary["falls"],
                                bed_motion=summary["rapid_movements"],
                                full=summary.get("full_visible", 0),
                                partial=summary.get("partial", 0),
                                frames=summary["frames"]))

    html = """
    <style>
      body{font-family:'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:20px}
      .page{max-width:900px;margin:auto}
      .card{background:#1c2f50;border:1px solid #2f4d77;border-radius:12px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.35);}
      h2{margin-top:0}
      a{color:#60a5fa;text-decoration:none}
      .input-group{display:flex;gap:10px;align-items:center;margin-bottom:16px;flex-wrap:wrap}
      input[type=file]{color:#f8fafc}
      button{cursor:pointer;border:none;border-radius:8px;padding:10px 14px;background:#2563eb;color:#fff;font-weight:600}
      .status{margin-top:10px;padding:10px;border:1px solid #2563eb;border-radius:8px;background:#1a3b6d}
    </style>
    <script>
      function showFilename(){
        const fileInput = document.getElementById('videoInput');
        const label = document.getElementById('filenameLabel');
        label.textContent = fileInput.files.length ? 'Selected: ' + fileInput.files[0].name : 'No file selected';
      }
      function startUpload(event){
        event.preventDefault();
        const input = document.getElementById('videoInput');
        const status = document.getElementById('statusBox');
        if(!input.files.length){
          status.textContent = 'Please choose a video file first.';
          return;
        }
        status.textContent = 'Uploading and processing video... this may take a moment.';
        document.getElementById('uploadForm').submit();
      }
    </script>
    <div class='page'>
      <div class='card'>
        <a href='/'>← Back</a>
        <h2>Upload Video for Detection</h2>
        <form id='uploadForm' method='post' enctype='multipart/form-data' onsubmit='startUpload(event)'>
          <div class='input-group'>
            <input id='videoInput' type='file' name='video' accept='video/*' required onchange='showFilename()'>
            <button type='submit'>Start Processing</button>
          </div>
          <p id='filenameLabel'>No file selected</p>
          <div id='statusBox' class='status'>Choose a file and click Start Processing.</div>
        </form>
      </div>
    </div>
    """
    return render_template_string(html)

@app.route('/processed/<filename>')
def show_processed(filename):
    if not os.path.exists(os.path.join(OUTPUT_FOLDER, filename)):
        return "File not found"

    falls = int(request.args.get('falls', 0))
    bed_motion = int(request.args.get('bed_motion', 0))
    full = int(request.args.get('full', 0))
    partial = int(request.args.get('partial', 0))
    frames = int(request.args.get('frames', 0))

    alert_html = ""
    if falls > 0:
        alert_html += "<p style='color:red; font-weight:bold;'>🚨 CRITICAL ALERT: Fall detected in uploaded video!</p>"
    if bed_motion > 0:
        alert_html += "<p style='color:orange; font-weight:bold;'>⚠️ WARNING: Rapid bed movements detected - Patient may be in distress!</p>"

    html = f"""
    <style>
      body{{font-family:'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:20px}}
      .page{{max-width:900px;margin:auto}}
      .card{{background:#1c2f50;border:1px solid #2f4d77;border-radius:12px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.35);}}
      a{{color:#60a5fa;text-decoration:none}}
      ul{{line-height:1.8}}
      video{{margin-top:20px;max-width:100%;border-radius:10px;border:2px solid #2f5294;}}
    </style>
    <div class='page'>
      <div class='card'>
        <a href='/'>← Back</a>
        <h2>Processed Video Analysis</h2>
        {alert_html}
        <p><strong>Analysis Summary:</strong></p>
        <ul>
          <li>Frames processed: {frames}</li>
          <li>Falls detected: {falls}</li>
          <li>Rapid bed movements: {bed_motion}</li>
        </ul>
        <video width='640' controls><source src='/download/{filename}' type='video/mp4'></video><br><br>
        <a href='/download/{filename}' download style='background:#2563eb;color:#fff;padding:10px 14px;border-radius:8px;display:inline-block;'>Download Processed Video</a>
      </div>
    </div>
    """
    return render_template_string(html)

@app.route('/download/<filename>')
def download_video(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    return open(file_path, 'rb'), 200, {'Content-Disposition': f'attachment; filename={filename}'}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
