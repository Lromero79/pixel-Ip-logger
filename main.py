from flask import Flask, request, send_file, render_template_string, abort, make_response
import os
import csv
import datetime
import requests
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# CONFIG
PIXEL_FILE = "pixel.png"
LOGS_FILE = "access_logs.csv"
GEO_CACHE_FILE = "geo_cache.json"
IMAGES_FOLDER = "images"

os.makedirs(IMAGES_FOLDER, exist_ok=True)

# Global cache
geo_cache = {}

def load_geo_cache():
    global geo_cache
    if os.path.exists(GEO_CACHE_FILE):
        try:
            with open(GEO_CACHE_FILE, "r", encoding="utf-8") as f:
                geo_cache = json.load(f)
        except Exception:
            pass

def save_geo_cache():
    try:
        with open(GEO_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(geo_cache, f, indent=2)
    except Exception:
        pass

def create_pixel():
    if not os.path.exists(PIXEL_FILE):
        img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        img.save(PIXEL_FILE, "PNG")

create_pixel()
load_geo_cache()

def init_logs():
    if not os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "ip", "country", "city", "lat", "lon", "user_agent", "referer", "path", "tracking_id"])

init_logs()

def get_geoip(ip):
    if not ip or ip.startswith(("127.", "192.168.", "10.")):
        return "Local", "N/A", "0", "0"
    if ip in geo_cache:
        return geo_cache[ip]
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,city,lat,lon", timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                result = (
                    data.get("country", "Unknown"),
                    data.get("city", "Unknown"),
                    str(data.get("lat", "N/A")),
                    str(data.get("lon", "N/A"))
                )
                geo_cache[ip] = result
                save_geo_cache()
                return result
    except Exception:
        pass
    result = ("Unknown", "Unknown", "N/A", "N/A")
    geo_cache[ip] = result
    return result

def log_access(tracking_id="default"):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()
    country, city, lat, lon = get_geoip(ip)
    ua = request.headers.get("User-Agent", "Unknown")
    referer = request.headers.get("Referer", "Direct")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path = request.path
    with open(LOGS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, ip, country, city, lat, lon, ua, referer, path, tracking_id])
    print(f"[LOG] {timestamp} | {ip} | {country}/{city} | {tracking_id}")

def add_watermark(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        width, height = img.size
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        except:
            font = ImageFont.load_default()
        text = "Tracked"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = width - text_width - 20
        y = height - text_height - 20
        draw.rectangle([x-12, y-8, x+text_width+12, y+text_height+8], fill=(0, 0, 0, 160))
        draw.text((x, y), text, fill=(255, 255, 255, 230), font=font)
        output = BytesIO()
        img.save(output, format='JPEG', quality=88, optimize=True)
        output.seek(0)
        return output
    except Exception:
        return open(image_path, "rb")

# ====================== ROUTES ======================

@app.route("/track.png")
@app.route("/track/<name>.png")
def track_pixel(name="default"):
    log_access(name)
    return send_file(PIXEL_FILE, mimetype="image/png")

@app.route("/photo/<filename>")
def serve_tracked_image(filename):
    filepath = os.path.join(IMAGES_FOLDER, filename)
    if not os.path.exists(filepath):
        abort(404)
    log_access(f"photo:{filename}")
    if request.args.get("overlay") == "1":
        img_data = add_watermark(filepath)
        response = make_response(send_file(img_data, mimetype="image/jpeg"))
        response.headers["Content-Disposition"] = f"inline; filename={filename}"
        return response
    return send_file(filepath)

@app.route("/logs")
def view_logs():
    logs = []
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            logs = list(reader)
            logs.reverse()

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>IP Logger Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #f8f9fa; }
            .table { font-size: 0.9rem; }
            .log-table td { vertical-align: middle; }
        </style>
    </head>
    <body>
        <div class="container py-4">
            <h1 class="mb-4">📊 IP Logger Dashboard</h1>
            <div class="alert alert-success">
                <strong>GeoIP Caching Active</strong> • {{ geo_count }} entries cached
            </div>
            
            <div class="card mb-4">
                <div class="card-header d-flex justify-content-between">
                    <strong>Latest Logs (showing most recent)</strong>
                    <a href="/logs" class="btn btn-sm btn-outline-primary">Refresh</a>
                </div>
                <div class="card-body p-0">
                    {% if logs %}
                    <div class="table-responsive">
                        <table class="table table-striped table-hover log-table mb-0">
                            <thead class="table-dark">
                                <tr>
                                    <th>Time</th>
                                    <th>IP</th>
                                    <th>Country</th>
                                    <th>City</th>
                                    <th>Lat / Lon</th>
                                    <th>Tracking ID</th>
                                    <th>Path</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for log in logs[:200] %}
                                <tr>
                                    <td>{{ log.timestamp }}</td>
                                    <td><code>{{ log.ip }}</code></td>
                                    <td>{{ log.country }}</td>
                                    <td>{{ log.city }}</td>
                                    <td>{{ log.lat }} / {{ log.lon }}</td>
                                    <td><span class="badge bg-primary">{{ log.tracking_id }}</span></td>
                                    <td><code>{{ log.path }}</code></td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="p-5 text-center text-muted">No logs yet. Load a tracking image to start recording.</div>
                    {% endif %}
                </div>
            </div>

            <div class="card">
                <div class="card-header"><strong>Quick Embed Examples</strong></div>
                <div class="card-body">
                    <p><strong>Invisible Tracking Pixel:</strong></p>
                    <pre class="bg-light p-3"><code>&lt;img src="https://YOUR-URL/track.png" width="1" height="1" style="display:none;"&gt;</code></pre>
                    <p><strong>Named Campaign:</strong></p>
                    <pre class="bg-light p-3"><code>&lt;img src="https://YOUR-URL/track/summer-sale.png" width="1" height="1" style="display:none;"&gt;</code></pre>
                    <p><strong>Real Photo with Overlay:</strong></p>
                    <pre class="bg-light p-3"><code>&lt;img src="https://YOUR-URL/photo/yourphoto.jpg?overlay=1" width="600"&gt;</code></pre>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, logs=logs, geo_count=len(geo_cache))

@app.route("/")
def index():
    return """
    <h1 class="text-center mt-5">IP Logger is Running</h1>
    <p class="text-center"><a href="/logs" class="btn btn-primary">Open Dashboard →</a></p>
    """

if __name__ == "__main__":
    print("\n🚀 IP Logger with GeoIP Caching + Docker Support Started!")
    print("   Dashboard: http://127.0.0.1:5000/logs")
    print("   Run with Docker: docker-compose up --build")
    app.run(host="0.0.0.0", port=5000, debug=False)
