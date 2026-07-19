# IP Logger with Tracking Pixel, GeoIP & Real Image Overlay

A lightweight, self-hosted **IP logger** using tracking pixels or real images. Includes GeoIP lookup with caching, optional watermark overlay, and a clean dashboard.

**⚠️ Legal & Ethical Warning**  
This tool logs IP addresses, location data, and browser info when an image is loaded.  
**Use ONLY for legitimate purposes** (your own marketing, personal projects, with proper disclosure in your privacy policy).  
Comply with GDPR, CCPA, and all applicable laws. Misuse is your sole responsibility.

## Features
- Invisible 1x1 tracking pixel (`/track.png`)
- Named campaigns (`/track/summer-sale.png`)
- Serve real images with optional "Tracked" watermark overlay (`/photo/image.jpg?overlay=1`)
- Automatic GeoIP (country, city, lat/lon) with smart caching
- Beautiful web dashboard to view all logs
- Docker support for easy deployment
- GitHub Actions CI included

## Quick Start (Linux / macOS / Windows)

### 1. Clone the repo
```bash
git clone https://github.com/Lromero79/ip-logger.git
cd ip-logger
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the server
```bash
python -m app.main
```

Open http://127.0.0.1:5000/logs in your browser.

### 4. Make it public (for emails)
Install [ngrok](https://ngrok.com) and run:
```bash
ngrok http 5000
```
Use the `https://xxxx.ngrok-free.app` URL in your emails/images.

## Usage Examples

**Invisible pixel in email:**
```html
<img src="https://your-ngrok-url/track.png" width="1" height="1" style="display:none;">
```

**Named campaign:**
```html
<img src="https://your-ngrok-url/track/summer-sale.png" width="1" height="1" style="display:none;">
```

**Track views of a real photo (with overlay):**
1. Put your image in the `images/` folder (e.g. `vacation.jpg`)
2. Embed:
```html
<img src="https://your-ngrok-url/photo/vacation.jpg?overlay=1" width="600">
```

## Docker (Recommended)

```bash
docker-compose up --build
```

The app will be available on port 5000.

## Project Structure
```
ip-logger/
├── app/
│   ├── __init__.py
│   └── main.py              # Main Flask application
├── images/                  # Put images you want to track here
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── LICENSE
```

## Running on Linux (Step-by-Step)

1. Update system:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. Install Python & pip (if not installed):
   ```bash
   sudo apt install python3 python3-pip python3-venv -y
   ```

3. Clone and setup:
   ```bash
   git clone https://github.com/YOURUSERNAME/ip-logger.git
   cd ip-logger
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Run:
   ```bash
   python -m app.main
   ```

5. In another terminal (for public access):
   ```bash
   # Install ngrok if needed
   curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
   echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
   sudo apt update && sudo apt install ngrok
   ngrok config add-authtoken YOUR_TOKEN
   ngrok http 5000
   ```

## Mobile Companion (Android + iOS)

A basic **Flutter** companion app is included in the `mobile/` folder (create it if needed). It allows generating tracking links and viewing logs from your phone.

See the `mobile/` directory for the Flutter project.

## License
MIT License — see [LICENSE](LICENSE) file.

**Use responsibly and ethically.**
```

---

**Note**: The mobile folder can be added later if needed. For now, the web project is complete.
