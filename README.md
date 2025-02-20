# CamScan

A fast and efficient network camera scanner that detects IP cameras and web-enabled surveillance devices on your local network.

## Features

- Multi-threaded scanning for high performance
- Detects common IP camera brands and models
- Scans multiple ports and paths simultaneously
- Identifies video streams and camera interfaces
- Progress tracking during scan
- Supports multiple camera manufacturers including:
  - Hikvision
  - Dahua
  - Axis
  - Foscam
  - Amcrest
  - Reolink
  - Wyze
  - And more...

## Requirements

```
python 3.x
requests
```

## Installation

1. Install the required package:
```bash
pip install requests
```

2. Download `camscan.py` to your local machine.

## Usage

Simply run the script:
```bash
python camscan.py
```

The scanner will:
- Check all IP addresses in the 192.168.1.x range
- Scan common camera ports (80, 81, 554, 8080, etc.)
- Test multiple endpoints on each open port
- Display progress as it runs
- Show discovered cameras with their details

## Output

When a camera is found, you'll see output like:
```
Found camera stream at http://192.168.1.x:port/path (Content-Type: video/mjpeg)
Server type: Camera-Model-XYZ
```

## Security Note

This tool is intended for use only on networks you own or have permission to scan. Unauthorized scanning of networks may be illegal in your jurisdiction.

## How It Works

1. Performs quick port scan using sockets
2. Tests open ports for common camera paths
3. Checks responses for camera-specific signatures
4. Identifies video streams and camera interfaces
5. Reports findings with server information

## Advanced Features

- Parallel path checking for faster scanning
- Multiple signature detection methods
- Server header analysis
- Content-type verification
- SSL/TLS handling
- Automatic redirect handling

## Supported Ports

The scanner checks common ports used by IP cameras:
- Standard HTTP (80-88)
- RTSP (554)
- Common alternate ports (8000-8086)
- Manufacturer-specific ports (34567, 37777)
- And more...

## Supported Paths

Checks multiple camera-specific paths including:
- /video
- /live
- /mjpg/video.mjpg
- /axis-cgi/mjpg/video.cgi
- /streaming/channels/1
- /onvif/device_service
- And many others...
