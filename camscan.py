import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import socket
from itertools import product

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

CAMERA_SIGNATURES = [
    'ipcam', 'webcam', 'camera', 'hikvision', 'dahua', 'axis', 'foscam', 'webcamxp',
    'yawcam', 'netcam', 'avigilon', 'amcrest', 'ubiquiti', 'unifi', 'reolink', 'wyze'
]

CAMERA_PATHS = [
    '/', '/video', '/live', '/mjpg/video.mjpg', '/axis-cgi/mjpg/video.cgi',
    '/videostream.cgi', '/video.mjpg', '/video.cgi', '/video.h264',
    '/cam', '/camera', '/live.html', '/view.html', '/viewer/live/index.html',
    '/streaming/channels/1', '/onvif/device_service', '/onvif/media',
    '/img/video.mjpeg', '/cgi-bin/video.cgi', '/web/auto.htm'
]

ports = [
    80, 81, 82, 83, 84, 85, 88,
    554, 1935, 5000, 5001, 5002, 5004, 5005,
    7001, 7002,
    8000, 8001, 8002, 8080, 8081, 8082, 8083, 8084, 8085, 8086,
    8554, 9000, 9001, 9002,
    37777, 37778,
    34567, 34568
]

ip_ranges = [f"192.168.1.{i}" for i in range(1, 255)]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def is_camera_response(response, url):
    try:
        server = response.headers.get('Server', '').lower()
        content_type = response.headers.get('Content-Type', '').lower()
        
        if any(x in content_type for x in ['video', 'stream', 'mjpeg', 'multipart']):
            print(f"Found camera stream at {url} (Content-Type: {content_type})")
            return True
            
        text = response.text.lower()[:1000]
        if any(sig in text for sig in CAMERA_SIGNATURES):
            print(f"Found camera signature at {url}")
            return True
            
        if any(sig in server for sig in CAMERA_SIGNATURES):
            print(f"Found camera server at {url} (Server: {server})")
            return True
            
        return False
    except:
        return False

def check_url(ip, port, path):
    url = f"http://{ip}:{port}{path}"
    try:
        response = requests.get(
            url,
            timeout=2,
            headers=headers,
            verify=False,
            allow_redirects=True
        )
        
        if response.status_code == 200:
            if is_camera_response(response, url):
                server = response.headers.get('Server', '')
                if server:
                    print(f"Server type: {server}")
    except requests.RequestException:
        pass

def check_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            with ThreadPoolExecutor(max_workers=10) as path_executor:
                path_futures = [
                    path_executor.submit(check_url, ip, port, path)
                    for path in CAMERA_PATHS
                ]
                for future in as_completed(path_futures):
                    future.result()
    except:
        pass

with ThreadPoolExecutor(max_workers=50) as executor:
    futures = [
        executor.submit(check_port, ip, port)
        for ip, port in product(ip_ranges, ports)
    ]
    
    completed = 0
    total = len(futures)
    
    for future in as_completed(futures):
        completed += 1
        if completed % 100 == 0:
            print(f"Progress: {completed}/{total} ({(completed/total)*100:.1f}%)")
