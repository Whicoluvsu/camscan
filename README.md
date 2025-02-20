# CamScan

Network camera scanner that detects IP cameras on networks.

## Usage

```bash
python camscan.py --ranges 192.168.1.0/24 10.0.0.0/24
```

## Features

- Fast multi-threaded scanning
- Detects common IP camera brands
- Scans multiple ports and paths
- Simple text output format
- No extra dependencies

## Output

Results saved to `found_cameras.txt`:
```
http://192.168.1.100:80/live | Stream detected (video/mjpeg)
http://192.168.1.120:8080/video | Camera signature found (hikvision)
```

## Supported Cameras

- Hikvision
- Dahua  
- Axis
- Amcrest
- Reolink
- Wyze
- Foscam
- And many more...

## Ports Scanned

- HTTP/HTTPS (80-88, 443)
- RTSP (554)
- Common alternates (8000-8099)
- Special ports (34567, 37777)

## Requirements

```
python 3.x
requests
```

## Warning

Only scan networks you own or have permission to scan.
