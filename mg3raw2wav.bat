@echo off & setlocal
for /R %%a in (*.raw) do ffmpeg -f s16le -ar 48.0k -ac 1 -i "%%~dpna.raw" "%%~dpna.wav"