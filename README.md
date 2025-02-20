# CamScan - Made for Blackpill

Ultra-fast network camera scanner with automatic screenshot capture. Scans entire networks to find IP cameras, DVRs, and NVRs.

## Features

- Multi-threaded scanning (1000+ concurrent threads)
- Automatic screenshot capture of discovered cameras
- Support for HTTP and RTSP streams
- Broad network range coverage
- Brand detection for 100+ manufacturers
- Default credential testing
- Fast port scanning
- Multiple detection methods

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Maximum Coverage Scan (Recommended)
For the broadest possible scan, just run:
```bash
python camscan.py
```
This automatically scans:
- All private networks (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- Link-local networks (169.254.0.0/16)
- Common camera subnets
- IoT networks
- Enterprise networks
- Special use ranges
- Common public IP ranges

### Custom Network Scan
Scan specific networks:
```bash
python camscan.py --ranges 192.168.1.0/24 10.0.0.0/8
```

### Maximum Performance
For fastest possible scanning:
```bash
# Increase thread count (adjust based on your CPU)
python camscan.py --threads 2000

# Scan multiple large networks
python camscan.py --ranges 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16 8.0.0.0/8 66.0.0.0/8 71.0.0.0/8
```

## Coverage Details

### Default Networks (Auto-Scanned)
- `10.0.0.0/8` - All private Class A (16.7 million IPs)
- `172.16.0.0/12` - All private Class B (1 million IPs)
- `192.168.0.0/16` - All private Class C (65,536 IPs)
- `169.254.0.0/16` - Link-local addresses
- `100.64.0.0/10` - Carrier NAT space
- `192.0.0.0/24` - IANA special use
- `192.0.2.0/24` - TEST-NET-1
- `198.18.0.0/15` - Network testing
- `203.0.113.0/24` - TEST-NET-3

### Common Camera Networks (Auto-Scanned)
- `192.168.1.0/24` - Default home network
- `192.168.0.0/24` - Default router network
- `10.0.0.0/24` - Common business
- `10.0.1.0/24` - Common business
- `172.16.0.0/24` - Common business
- `172.16.1.0/24` - Common business
- `192.168.2.0/24` - Common IoT
- `192.168.10.0/24` - Common cameras
- `192.168.20.0/24` - Common cameras
- `10.10.0.0/16` - Enterprise cameras
- `172.20.0.0/16` - Enterprise cameras

### Public IP Ranges (Auto-Scanned)
- `8.0.0.0/8` - Level 3
- `66.0.0.0/8` - Various ISPs
- `71.0.0.0/8` - Various ISPs
- `98.0.0.0/8` - Various ISPs
- `108.0.0.0/8` - Various ISPs
- `184.0.0.0/8` - Various ISPs
- `216.0.0.0/8` - Various ISPs

## Output

- Found cameras are logged to `found_cameras.txt`
- Screenshots are saved to `camera_screenshots/` directory
- Live console output shows discoveries

## Security Notice

⚠️ **IMPORTANT**: Only scan networks you have permission to scan. Unauthorized scanning may be illegal.

## Tips for Maximum Results

1. Run during off-peak hours for better network performance
2. Use a machine with good network connectivity
3. Consider splitting large ranges into smaller chunks
4. Let the scan run for several hours to cover all ranges
5. Check `found_cameras.txt` periodically for new discoveries
6. Monitor `camera_screenshots/` for visual confirmation
7. Use a wired connection for stability
