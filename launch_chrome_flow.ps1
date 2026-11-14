$CdpPort = 9333
$UserDataDir = "$env:LOCALAPPDATA\Google\FlowAutomationChrome"
$ChromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$FlowUrl = "https://flow.google.com/project/d7cecce7-8682-454a-bb94-13576243c599"

$proc = Start-Process -FilePath $ChromePath -ArgumentList `
    "--remote-debugging-port=$CdpPort", `
    "--user-data-dir=$UserDataDir", `
    "--remote-allow-origins=*", `
    "--no-first-run", `
    "--no-default-browser-check", `
    "--window-size=1920,1080", `
    $FlowUrl -PassThru

Start-Sleep -Seconds 2
Write-Output "PID: $($proc.Id), HasExited: $($proc.HasExited)"
