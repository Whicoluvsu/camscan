# CamScan

## Project Overview
Designed to scan networks for IP cameras. It automates the discovery of IP cameras by sending HTTP requests to various common paths and checking for known camera signatures in the responses. The script can also capture images from the discovered cameras and save them for further analysis, making it a useful tool for "network administrators and security professionals." 

## Features
- **Network Scanning**: Efficiently scans specified IP ranges for connected cameras using multithreading.
- **Authentication Support**: Attempts to authenticate with common default credentials for various camera brands.
- **Image Capture**: Captures images from detected cameras and saves them locally for review.
- **RTSP Stream Handling**: Supports capturing images from RTSP streams, enabling access to live video feeds.
- **Threading**: Utilizes Python's threading capabilities to perform scans concurrently, improving performance.
- **Structured Logging**: Implements logging to track the script's activity and facilitate debugging.
- **Customizable**: Allows users to specify IP ranges and the number of concurrent threads for scanning.

## Installation
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd cam
   ```
2. **Install the required dependencies**:
   Make sure you have Python and pip installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the script with the desired IP ranges and number of threads:
```bash
python camscan.py --ranges "192.168.1.0/24" --threads 50
```

### Example Commands
- To scan a specific subnet:
```bash
python camscan.py --ranges "192.168.1.0/24" --threads 10
```
- To scan multiple ranges:
```bash
python camscan.py --ranges "192.168.1.0/24,192.168.2.0/24" --threads 20
```

## Troubleshooting
- **Common Issues**:
  - If the script fails to find cameras, ensure that the specified IP range is correct and that the cameras are powered on and connected to the network.
  - If you encounter permission errors, try running the script with elevated privileges.
  - Check the network settings to ensure that your machine can communicate with the target IP addresses.

If you have any questions or need further assistance, feel free to open an issue in the repository.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.
