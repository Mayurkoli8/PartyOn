@echo off
:loop
echo Starting LAN Audio Server...
python server.py
echo Server crashed. Restarting in 3 seconds...
timeout /t 3 >nul
goto loop
