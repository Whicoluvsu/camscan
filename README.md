# **CamScan - IP Camera Network Scanner**  

---

## **What It Does**  

- **Finds cameras fast** - Checks for 60+ camera brands and protocols  
- **Gets visual proof** - Captures screenshots from live feeds  
- **Breaks weak logins** - Tests 50+ default username/password combos  
- **Works with all camera types** - Supports HTTP, RTSP, and MJPEG streams  
- **Plays nice with networks** - Smart throttling prevents congestion  

---

## **Getting Started**  

### **1. Install Requirements**  
```bash
pip install requests opencv-python pillow numpy urllib3
```

### **2. Run a Scan**  
```bash
# Scan a single subnet (auto-adjusts speed)
python camscan.py --ranges 192.168.1.0/24

# Full audit mode (multiple networks, max threads)
python camscan.py --threads 30 --ranges 10.0.0.0/16 192.168.0.0/24
```

### **3. Check Results**  
- **`found_cameras.txt`** - Lists all discovered devices  
- **`camera_screenshots/`** - Contains captured images  

---

## **Why Use This?**  

I built CamScan after wasting hours manually checking IP ranges for forgotten cameras during security audits. Existing tools either missed devices or flooded networks. This version:  

✔ **Actually finds cameras** - Not just web servers pretending to be cameras  
✔ **Gets visual confirmation** - No more guessing if an IP is really a camera  
✔ **Respects network limits** - Won't crash your router like some scripts  

---

## **Real-World Uses**  

- **Security teams** - Find unauthorized cameras in offices  
- **Home users** - Map all smart cameras on their network  
- **IT departments** - Inventory surveillance systems before upgrades  

---

## **Warning**  

*Use responsibly. Unauthorized scanning violates laws in most countries.*  


# ⚠️ ILLEGAL EXAMPLES (DO NOT USE) ⚠️
```python
python camscan.py --ranges 0.0.0.0/0      # Scans the entire internet (illegal)
```

---

## **About the Code**  

- No bloated dependencies - Runs anywhere Python works  
- Clear logging - Know exactly what's happening  
- Adjustable speed - From cautious scans to full network sweeps  

```python
# Example of the smart threading logic
MAX_WORKERS = min(32, (os.cpu_count() or 1) * 4)  # Auto-scaling
SCAN_LOCK = Semaphore(MAX_WORKERS)  # Traffic control
```
