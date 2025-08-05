from flask import Flask, request, render_template_string
import requests
import yt_dlp
import os
import re

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Universal Video Downloader</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 20px; }
        input, button { padding: 10px; width: 80%%; margin: 10px auto; }
        video { margin-top: 20px; max-width: 100%%; }
        .info { margin-top: 20px; }
    </style>
</head>
<body>
    <h2>🌐 Universal Video Downloader</h2>
    <form method="POST">
        <input type="text" name="url" placeholder="Paste video link here..." required>
        <br>
        <button type="submit">Download</button>
    </form>

    %s
</body>
</html>
'''

def extract_hashtags(text):
    return ' '.join(re.findall(r"#\w+", text))

def download_info_with_ytdlp(url):
    ydl_opts = {
        'quiet': True,
        'forcejson': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    result_html = ''
    if request.method == 'POST':
        url = request.form['url'].strip()

        try:
            if "tiktok.com" in url:
                api = f"https://www.tikwm.com/api/?url={url}"
                res = requests.get(api).json()
                if res["code"] != 0:
                    raise Exception("TikTok API failed.")
                data = res['data']
                title = data.get("title", "No title")
                hashtags = extract_hashtags(title)
                video_url = data['play']
            else:
                info = download_info_with_ytdlp(url)
                title = info.get('title', 'No title')
                video_url = info.get('url', '')
                hashtags = extract_hashtags(info.get('description', '') or '')

            result_html = f'''
            <div class="info">
                <h3>Title: {title}</h3>
                <p>Hashtags: {hashtags or "None found"}</p>
                <input type="text" value="{title}" readonly onclick="this.select();document.execCommand('copy');">
                <br><br>
                <video controls autoplay>
                    <source src="{video_url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <br><br>
                <a href="{video_url}" download>
                    <button>⬇️ Download Video</button>
                </a>
            </div>
            '''
        except Exception as e:
            result_html = f"<p style='color:red;'>Error: {str(e)}</p>"

    return render_template_string(HTML_TEMPLATE % result_html)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
