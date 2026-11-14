@echo off
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9333 --remote-allow-origins=* --user-data-dir="C:\Users\CHAU\AppData\Local\Google\FlowAutomationChrome" "https://flow.google.com/project/d7cecce7-8682-454a-bb94-13576243c599"
exit /b 0
