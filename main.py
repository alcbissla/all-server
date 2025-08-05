from flask import Flask, request, render_template_string, send_file
import yt_dlp
import requests
import os
import re
from uuid import uuid4

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>All-in-One Video Downloader</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
  <style>
    :root {
      --bg-light: #f4f4f9;
      --text-light: #1a1a1a;
      --bg-dark: #181818;
      --text-dark: #f5f5f5;
      --card-light: #ffffff;
      --card-dark: #2b2b2b;
      --accent: #3b82f6;
    }

    [data-theme="light"] {
      --bg: var(--bg-light);
      --text: var(--text-light);
      --card: var(--card-light);
    }

    [data-theme="dark"] {
      --bg: var(--bg-dark);
      --text: var(--text-dark);
      --card: var(--card-dark);
    }

    body {
      margin: 0;
      padding: 0;
      font-family: 'Inter', sans-serif;
      background-color: var(--bg);
      color: var(--text);
      display: flex;
      flex-direction: column;
      align-items: center;
      min-height: 100vh;
      transition: background-color 0.3s, color 0.3s;
    }

    header {
      text-align: center;
      margin-top: 2rem;
    }

    header h1 {
      font-size: 2.5rem;
      margin-bottom: 0.5rem;
    }

    header p {
      color: var(--accent);
      font-weight: 500;
    }

    .video-preview {
      margin: 2rem auto;
      width: 90%;
      max-width: 720px;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 10px 25px rgba(0,0,0,0.1);
      text-align: center;
    }

    video {
      width: 100%;
      border-radius: 16px;
      max-height: 400px;
    }

    .form-box {
      margin-top: 1rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 90%;
      max-width: 500px;
      gap: 10px;
    }

    input[type="text"] {
      width: 100%;
      padding: 14px 18px;
      font-size: 1rem;
      border-radius: 12px;
      border: 2px solid var(--accent);
      background-color: var(--card);
      color: var(--text);
    }

    button {
      background-color: var(--accent);
      color: white;
      font-weight: bold;
      padding: 14px 22px;
      font-size: 1rem;
      border-radius: 12px;
      border: none;
      cursor: pointer;
      transition: background-color 0.3s;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    button:hover {
      background-color: #2563eb;
    }

    .ads-container {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 20px;
      padding: 2rem 1rem;
      width: 100%;
      box-sizing: border-box;
    }

    .ad-box {
      background-color: var(--card);
      color: var(--text);
      padding: 20px;
      border-radius: 16px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      width: 280px;
      text-align: center;
      transition: transform 0.2s ease;
    }

    .ad-box:hover {
      transform: translateY(-5px);
    }

    footer {
      margin-top: auto;
      padding: 1.5rem;
      text-align: center;
    }

    .social-icons a {
      margin: 0 10px;
      display: inline-block;
    }

    .social-icons img {
      width: 32px;
      height: 32px;
      transition: transform 0.3s ease;
    }

    .social-icons img:hover {
      transform: scale(1.1);
    }

    .error-msg {
      margin-top: 1rem;
      color: #e53e3e;
      font-weight: 700;
      text-align: center;
    }

    .video-title {
      margin-top: 1rem;
      font-weight: 700;
      font-size: 1.25rem;
      color: var(--text);
    }

    .hashtags {
      margin-top: 0.25rem;
      color: var(--accent);
      font-weight: 600;
    }

    @media (min-width: 768px) {
      .form-box {
        flex-direction: row;
      }

      input[type="text"] {
        flex: 1;
      }

      button {
        flex-shrink: 0;
      }
    }
  </style>
</head>
<body>

  <header>
    <h1><i class="bi bi-download"></i> All-in-One Video Downloader</h1>
    <p>#TikTok #YouTube #Facebook #MP4 #M3U8 #HD</p>
  </header>

  <form class="form-box" action="/" method="post">
    <input type="text" name="url" placeholder="Paste your video link here..." required autocomplete="off" />
    <button type="submit"><i class="bi bi-cloud-arrow-down-fill"></i> Download</button>
  </form>

  {% if error %}
    <p class="error-msg">{{ error }}</p>
  {% endif %}

  {% if filename %}
  <div class="video-preview">
    <video autoplay muted controls playsinline>
      <source src="/video/{{ filename }}" type="video/mp4" />
      Your browser does not support the video tag.
    </video>
    <div class="video-title">{{ title }}</div>
    <div class="hashtags">{{ hashtags or "No hashtags found" }}</div>
    
    <div style="display: flex; justify-content: center; margin-top: 1rem;">
      <a href="/video/{{ filename }}" download>
        <button>
          <i class="bi bi-cloud-arrow-down-fill"></i> Download Video
        </button>
      </a>
    </div>
  {% endif %}

  <div class="ads-container">
    <div class="ad-box">
      <h3><i class="bi bi-megaphone-fill"></i> Ad Spot 1</h3>
      <p>Promote your service or product here.</p>
    </div>
    <div class="ad-box">
      <h3><i class="bi bi-rocket-takeoff-fill"></i> Ad Spot 2</h3>
      <p>Boost visibility and drive more clicks.</p>
    </div>
  </div>

  <footer>
  &copy; 2025 Smart Downloader.
    <div class="social-icons">
      <a href="https://t.me/Alcboss112" target="_blank" title="Telegram">
        <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Telegram" />
      </a>
      <a href="https://www.facebook.com/Alcboss112" target="_blank" title="Facebook">
        <img src="https://upload.wikimedia.org/wikipedia/commons/1/1b/Facebook_icon.svg" alt="Facebook" />
      </a>
    </div>
  </footer>

  <script>
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (prefersDark) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  </script>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    title = None
    hashtags = None
    filename = None
    error = None

    if request.method == "POST":
        url = request.form["url"].strip()

        if not re.match(r"^https?://", url):
            error = "❌ Invalid URL. Please enter a proper video link."
            return render_template_string(HTML_TEMPLATE, error=error)

        try:
            # TikTok via tikwm API
            if "tiktok.com" in url:
                api = f"https://www.tikwm.com/api/?url={url}"
                resp = requests.get(api).json()
                if resp["code"] == 0:
                    video_url = resp["data"]["play"]
                    title = resp["data"]["title"]
                    hashtags = " ".join(f"#{tag}" for tag in resp["data"].get("tags", []))
                else:
                    raise Exception("TikTok API error or video not found.")
            else:
                ydl_opts = {
                    "format": "mp4",
                    "outtmpl": "downloads/%(id)s.%(ext)s",
                    "quiet": True,
                    "noplaylist": True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get("title", "No Title")
                    hashtags = " ".join(f"#{tag}" for tag in info.get("tags", [])[:5])
                    video_url = info.get("url")
                    filename = str(uuid4()) + ".mp4"
                    ydl.download([url])
                    original_file = ydl.prepare_filename(info)
                    os.rename(original_file, f"downloads/{filename}")

            if not filename:
                filename = str(uuid4()) + ".mp4"
                video_data = requests.get(video_url)
                with open(f"downloads/{filename}", "wb") as f:
                    f.write(video_data.content)

        except Exception as e:
            error = f"❌ Error: {str(e)}"

    return render_template_string(HTML_TEMPLATE, title=title, hashtags=hashtags, filename=filename, error=error)

@app.route("/video/<filename>")
def serve_video(filename):
    return send_file(f"downloads/{filename}", as_attachment=False)

if __name__ == "__main__":
    os.makedirs("downloads", exist_ok=True)
    app.run(host="0.0.0.0", port=10000)
