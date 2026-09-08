$ErrorActionPreference = "Stop"

$url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$zipPath = "$PWD\ffmpeg.zip"
$extractPath = "$PWD\ffmpeg_temp"

Write-Host "Descargando FFmpeg..."
Invoke-WebRequest -Uri $url -OutFile $zipPath

Write-Host "Extrayendo FFmpeg..."
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

Write-Host "Moviendo binarios a la carpeta del proyecto..."
$binDir = Get-ChildItem -Path $extractPath -Directory | Select-Object -First 1
$binDir = Join-Path -Path $binDir.FullName -ChildPath "bin"

Copy-Item -Path (Join-Path -Path $binDir -ChildPath "ffmpeg.exe") -Destination $PWD -Force
Copy-Item -Path (Join-Path -Path $binDir -ChildPath "ffprobe.exe") -Destination $PWD -Force

Write-Host "Limpiando archivos temporales..."
Remove-Item -Path $zipPath -Force
Remove-Item -Path $extractPath -Recurse -Force

Write-Host "FFmpeg configurado correctamente."
