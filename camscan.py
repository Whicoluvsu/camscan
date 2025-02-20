import requests, socket, logging, json, argparse, ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from itertools import product
from datetime import datetime
import os

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

RESULTS_FILE = "found_cameras.txt"
discovered = []

CAMERA_PATHS = ['/','/..','/video','/live','/mjpg/video.mjpg','/axis-cgi/mjpg/video.cgi','/videostream.cgi','/video.mjpg','/video.cgi','/video.h264','/cam','/camera','/live.html','/view.html','/viewer/live/index.html','/streaming/channels/1','/onvif/device_service','/onvif/media','/img/video.mjpeg','/cgi-bin/video.cgi','/web/auto.htm','/live/index.html','/live/ch0','/live/ch00','/live/ch01','/live_stream.html','/live/stream','/snap.jpg','/snapshot.cgi','/control/control.cgi','/config/system.cgi','/api/v1/device','/anony/mjpg','/h264/ch1/sub/av_stream','/h264/ch1/main/av_stream','/live/main','/live/sub','/live/ch01_0','/live/ch01_1','/live/0','/live/1','/live_sub','/live_main','/av0_0','/av0_1','/cam0_0','/cam0_1','/cam1_0','/cam/realmonitor','/cam/realmonitor?channel=1&subtype=0','/cam/realmonitor?channel=1&subtype=1','/cgi-bin/snapshot.cgi','/cgi-bin/viewer/video.jpg','/udpstream/1','/live/0/MAIN','/live/0/SUB','/live/1/MAIN','/live/1/SUB','/live_stream/0','/live_stream/1']

CAMERA_SIGS = ['ipcam','webcam','camera','hikvision','dahua','axis','foscam','webcamxp','yawcam','netcam','avigilon','amcrest','ubiquiti','unifi','reolink','wyze','vivotek','geovision','mobotix','panasonic','samsung','bosch','trendnet','dlink','tplink','lorex','swann','nest','arlo','ring','eufy','annke','rtsp','mjpeg','h.264','h264','onvif','ipcamera','network camera','ip camera','cctv','dvr','nvr']

ports = [80,81,82,83,84,85,86,87,88,443,554,888,1024,2000,3000,4000,5000,6000,7000,8000,8001,8002,8003,8004,8005,8006,8007,8008,8009,8010,8080,8081,8082,8083,8084,8085,8086,8090,8091,8092,8093,8094,8095,8096,8097,8098,8099,9000,9001,34567,37777]

headers = {'User-Agent': 'Mozilla/5.0'}

def save_camera(url, info):
    with open(RESULTS_FILE, 'a') as f:
        f.write(f"{url} | {info}\n")
    discovered.append(url)

def check_url(ip, port, path):
    url = f"http://{ip}:{port}{path}"
    try:
        r = requests.get(url, timeout=2, headers=headers, verify=False, allow_redirects=True)
        if r.status_code == 200:
            ct = r.headers.get('Content-Type', '').lower()
            sv = r.headers.get('Server', '').lower()
            txt = r.text.lower()[:500]
            
            if any(x in ct for x in ['video','stream','mjpeg','multipart']):
                save_camera(url, f"Stream detected ({ct})")
                return True
                
            if any(sig in txt for sig in CAMERA_SIGS) or any(sig in sv for sig in CAMERA_SIGS):
                save_camera(url, f"Camera signature found ({sv})")
                return True
    except:
        pass
    return False

def check_port(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        if s.connect_ex((ip, port)) == 0:
            with ThreadPoolExecutor(max_workers=20) as ex:
                futs = [ex.submit(check_url, ip, port, path) for path in CAMERA_PATHS]
                for f in as_completed(futs):
                    if f.result():
                        break
        s.close()
    except:
        pass

def scan_range(ip_range):
    try:
        net = ipaddress.ip_network(ip_range, strict=False)
        ips = [str(ip) for ip in net.hosts()]
        with ThreadPoolExecutor(max_workers=100) as ex:
            futs = [ex.submit(check_port, ip, port) for ip, port in product(ips, ports)]
            done = 0
            for f in as_completed(futs):
                done += 1
                if done % 1000 == 0:
                    print(f"Scanned: {done}/{len(futs)} IPs")
    except Exception as e:
        print(f"Error scanning {ip_range}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ranges', nargs='+', default=['192.168.1.0/24'], help='IP ranges to scan')
    args = parser.parse_args()
    
    if os.path.exists(RESULTS_FILE):
        os.remove(RESULTS_FILE)
        
    for ip_range in args.ranges:
        scan_range(ip_range)
        
    print(f"\nFound {len(discovered)} cameras")
    print(f"Results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    main()
