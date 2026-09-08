import os
import uuid
from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp

app = Flask(__name__)

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video')
            return jsonify({'title': title})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/download', methods=['GET', 'POST'])
def download():
    if request.method == 'POST':
        data = request.json or {}
        url = data.get('url')
        format_type = data.get('format', '1080') # 480, 720, 1080, 1440, mp3
    else:
        url = request.args.get('url')
        format_type = request.args.get('format', '1080')
        
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    unique_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_DIR, f'%(title)s_{unique_id}.%(ext)s')
    
    ydl_opts = {
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'ffmpeg_location': os.path.dirname(os.path.abspath(__file__)), # Use local ffmpeg
    }

    if format_type == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        # Dynamic logic based on URL domain
        if 'tiktok.com' in url or 'instagram.com' in url:
            # TikTok and Instagram: try to force h264 codec to avoid HEVC/AV1 issues, ignore height limits
            ydl_opts.update({
                'format': 'bestvideo[vcodec*=h264]+bestaudio/best[vcodec*=h264]/bestvideo[vcodec^=avc]+bestaudio/best[vcodec^=avc]/best',
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'postprocessor_args': [
                    '-c:v', 'libx264',
                    '-c:a', 'aac'
                ]
            })
        else:
            # YouTube: Use user-selected height and prefer mp4/m4a
            height = format_type
            ydl_opts.update({
                'format': f'bestvideo[ext=mp4][vcodec^=avc][height<={height}]+bestaudio[ext=m4a]/bestvideo[ext=mp4][height<={height}]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio[ext=m4a]/best[height<={height}]',
                'merge_output_format': 'mp4',
            })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Find the downloaded file
            # the extension might be different initially but yt-dlp ensures it becomes mp4 or mp3
            ext = 'mp3' if format_type == 'mp3' else 'mp4'
            title = info.get('title', 'Video').replace('/', '_').replace('\\', '_')
            
            # The exact filepath might be slightly different because yt-dlp cleans up titles
            # But ydl.prepare_filename gives the final name mostly, except for postprocessors
            filename = ydl.prepare_filename(info)
            if format_type == 'mp3':
                # Because of postprocessor, the extension changes to .mp3
                filename = os.path.splitext(filename)[0] + '.mp3'
            elif format_type != 'mp3':
                filename = os.path.splitext(filename)[0] + '.mp4'
                
            # If for some reason it didn't change (fallback)
            if not os.path.exists(filename):
                # fallback, just search for the file with the unique id
                for f in os.listdir(DOWNLOAD_DIR):
                    if unique_id in f:
                        filename = os.path.join(DOWNLOAD_DIR, f)
                        break

            return send_file(filename, as_attachment=True)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    import threading
    import webbrowser
    
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000/')
        
    # Open the browser after 1.5 seconds to give the server time to start
    threading.Timer(1.5, open_browser).start()
    app.run(debug=False, host='0.0.0.0', port=5000)
