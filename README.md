# CamScan

## Description
This project is a Python script designed to scan networks for IP cameras. It attempts to discover cameras by sending requests to various paths and checking for common camera signatures in the responses. The script can also capture images from the discovered cameras and save them for further analysis.

## Features
- Scans specified IP ranges for cameras.
- Supports authentication with common default credentials.
- Captures images from detected cameras and saves them.
- Handles both HTTP and RTSP streams.
- Uses threading to perform scans concurrently.
- Implements structured logging for better debugging and tracking.

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd cam
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the script with the desired IP ranges and number of threads:
```bash
python camscan.py --ranges "192.168.1.0/24" --threads 50
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.
