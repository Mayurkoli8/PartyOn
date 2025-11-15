# Sexy Audio Streamer

**Stream your system audio over LAN to any device via browser. Cross-platform support for Windows, macOS, and Linux.**

## Features

* **Real-time PC audio streaming** to your phone, tablet, or another PC.
* **Browser-based:** Works instantly inside any modern browser (WebAudio + WebSocket).
* **Zero-installation on Client:** Just a web page!
* **Cross-Platform Audio Capture:** 
  - **Windows:** WASAPI Loopback captures system audio directly (Stereo Mix fallback supported)
  - **macOS:** Uses BlackHole virtual audio driver for system audio capture
  - **Linux:** Supports standard audio input devices
* **Multi-Client Streaming:** Stream to multiple devices simultaneously.
* **Beautiful UI:** Clean, responsive player interface.
* **Robust Connection:** Features auto-reconnect and queue buffering.

---

## Installation

### Prerequisites

* Python 3.x
* Operating System: Windows, macOS, or Linux

### Setup Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Mayurkoli8/PartyOn.git
    cd PartyOn
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    # or on macOS/Linux:
    pip3 install -r requirements.txt
    ```

3.  **Platform-Specific Audio Setup:**

    **Windows:**
    * Open your **Windows Sound Panel** (Recording tab).
    * Ensure **"Show Disabled Devices"** is checked.
    * Enable **"Stereo Mix,"** or verify that the main playback device's loopback functionality is accessible by the application.

    **macOS:**
    * Install **BlackHole** virtual audio driver:
      1. Download from: https://github.com/ExistentialAudio/BlackHole/releases
      2. Install BlackHole (2ch or 16ch version)
      3. Open **System Preferences** (or **System Settings** on newer macOS) > **Sound**
      4. Set **Output** to BlackHole
      5. Set **Input** to BlackHole (for the application to capture)
      6. Use **Audio MIDI Setup** to create a Multi-Output Device if you want to hear audio while streaming
    * Restart the application after installing BlackHole

    **Linux:**
    * Ensure you have audio input devices configured
    * The application will attempt to use available input devices

---

##  Usage

### Starting the Server

Use the standard command or the auto-restart script:

1.  **Standard Python Command:**
    ```bash
    python server.py
    # or on macOS/Linux:
    python3 server.py
    ```
2.  **Auto-Restart Scripts:**
    * **Windows:**
      ```bash
      sexy-audio.bat
      ```
    * **macOS/Linux:**
      ```bash
      ./sexy-audio.sh
      ```

### Connecting from a Client Device

1.  Find your PC's **local IP Address**.
2.  Open a browser (on any device) and navigate to:
    ```
    http://YOUR-PC-IP:5000
    ```
3.  Click the **"Play Stream"** button on the page.

---

## Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend** | Python (Flask, WebSockets, sounddevice) | Audio capture, web hosting, and stream management. |
| **Frontend** | WebAudio API, HTML/CSS/JS | Audio decoding and playback in the client browser. |

---

## File Structure
```bash
    client.html        # Player UI
    server.py          # Audio capture + stream server (cross-platform)
    sexy-audio.bat     # Auto restart script (Windows)
    sexy-audio.sh      # Auto restart script (macOS/Linux)
    requirements.txt
    README.md
    LICENSE
```

---

## Platform-Specific Setup Tips

### Windows
* **No Sound:** Confirm that a loopback device (like Stereo Mix) is **Enabled** in the Windows Sound Recording panel.
* **Connection Errors:** Check your **Windows Firewall** settings to ensure port **5000** is open for `server.py`.

### macOS
* **No Sound:** 
  * Ensure BlackHole is installed and selected as both Output and Input in System Preferences/Settings
  * If you want to hear audio while streaming, create a Multi-Output Device in Audio MIDI Setup that includes both your speakers and BlackHole
* **Connection Errors:** Check your **macOS Firewall** settings to ensure port **5000** is open for `server.py`.
* **Permission Issues:** macOS may require microphone permissions - grant them in System Preferences > Security & Privacy > Privacy > Microphone

### Linux
* **No Sound:** Ensure audio input devices are properly configured and accessible
* **Connection Errors:** Check your firewall settings (ufw, firewalld, etc.) to ensure port **5000** is open

## License

MIT — Free to use and modify.

---

##  Connect With Me

I'm actively building AI, automation & networking tools.  
Reach out if you’d like to collaborate or contribute.

<div align="left">

<a href="https://github.com/mayurkoli8" target="_blank">
<img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" />
</a>

<a href="https://www.linkedin.com/in/mayur-koli-484603215/" target="_blank">
<img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" />
</a>


<a href="https://instagram.com/mentesa.live" target="_blank">
<img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white" />
</a>

<a href="mailto:kolimohit9595@gmail.com">
<img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" />
</a>

</div>

---

### 💬 Want to improve this project?
Open an issue or start a discussion — PRs welcome ⚡
