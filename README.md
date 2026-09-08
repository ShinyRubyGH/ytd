# YouTube Downloader Web App

Una aplicación web local construida con Python, Flask y `yt-dlp` para descargar videos y audios de YouTube fácilmente.

## Características
- Descarga videos de YouTube en múltiples resoluciones: 480p, 720p, 1080p y 1440p (MP4).
- Descarga audios en formato MP3.
- Combina audio y video automáticamente usando `ffmpeg` para mantener la mejor calidad posible en altas resoluciones, asegurando compatibilidad nativa (audio AAC) en reproductores de Windows.

## Instalación y Configuración

1. Clona este repositorio o descarga el código.
2. Abre una terminal (PowerShell) en la carpeta del proyecto.
3. Ejecuta el script de configuración para descargar automáticamente `ffmpeg` (necesario para el procesamiento de medios):
   ```powershell
   .\setup_ffmpeg.ps1
   ```
4. Instala las dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. Inicia el servidor de Flask:
   ```bash
   python app.py
   ```
2. Abre tu navegador web y ve a `http://localhost:5000`.
3. Pega el enlace de YouTube, selecciona el formato/calidad deseado y haz clic en "Descargar".
