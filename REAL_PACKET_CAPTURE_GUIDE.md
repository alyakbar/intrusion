# 🚀 Real Packet Capture - Quick Fix Guide

## ✅ Problem Fixed!

The issue was that the `threat_score` column was missing from your database, causing the API to return 500 errors. This has been fixed.

## 📋 How to Run Real Packet Capture

### Step 1: Start the Services (API + Frontend)

In **Terminal 1**, run:
```bash
./start_advanced.sh
```

This will start:
- API Server on http://localhost:5000
- Frontend on http://localhost:3000

**Leave this terminal running!**

---

### Step 2: Run Real-Time Detection

In **Terminal 2** (new terminal), run:
```bash
./start_realtime_detection.sh
```

This will:
- Capture **REAL** packets from your WiFi interface (`wlo1`)
- Use PyShark backend (tshark)
- **NO synthetic data** (inject-rate = 0)
- Run indefinitely until you press Ctrl+C

**Leave this terminal running!**

---

### Step 3: View Live Detections

Open your browser to:
- **Main Dashboard**: http://localhost:3000
- **Advanced Features**: http://localhost:3000/advanced

You should now see **real network traffic** being analyzed!

---

## 🔧 If Packet Capture Fails

If you see permission errors like `dumpcap: Couldn't run /usr/bin/dumpcap`, run these commands **once**:

```bash
sudo groupadd -f wireshark
sudo usermod -aG wireshark $USER
sudo chgrp wireshark /usr/bin/dumpcap
sudo chmod 750 /usr/bin/dumpcap
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap
newgrp wireshark
```

Then restart your terminal and try again.

---

## 🎯 Verify It's Working

### Check the Terminal Output
You should see logs like:
```
[INFO] Processing packet: TCP 192.168.1.x -> 172.217.x.x
[INFO] Anomaly detected! Score: 0.89
[INFO] Saved to database (ID: 123)
```

### Check the Dashboard
- **Total Packets** should be increasing
- **Recent Activity** should show real IPs from your network
- **Top Sources** should show actual devices on your network

### Check the Database
```bash
sqlite3 data/detections.db "SELECT COUNT(*) FROM detections;"
```
This number should be increasing as packets are captured.

---

## 🆚 Difference from Before

| Before | Now |
|--------|-----|
| Synthetic packet injection | **Real WiFi capture** |
| Fake IP addresses (10.x.x.x) | **Your actual network IPs** |
| Scapy backend (broken) | **PyShark backend (working)** |
| inject_rate > 0 | **inject_rate = 0** |
| Dashboard showed fake data | **Dashboard shows real traffic** |

---

## 📊 What You Should See

### Real Traffic Examples:
- **Your router IP**: 192.168.100.x
- **Google DNS**: 8.8.8.8
- **Cloudflare**: 1.1.1.1
- **ISP DNS**: Your ISP's DNS servers
- **HTTPS traffic**: Port 443 connections
- **DNS queries**: Port 53 UDP packets

### Synthetic Traffic (OLD - should NOT see):
- 10.0.x.x IP addresses
- Perfectly random patterns
- Unrealistic packet rates

---

## 🎨 Advanced Features Available

Once real detection is running, try these features at http://localhost:3000/advanced:

1. **📁 PCAP Analysis** - Upload and analyze packet capture files
2. **🔍 Packet Filtering** - Filter by protocol, port, IP, etc.
3. **🌐 Threat Intelligence** - IP reputation from AbuseIPDB & VirusTotal
4. **📧 Email Alerts** - Get notified of high-severity threats
5. **📡 Multi-Interface** - Monitor multiple network interfaces
6. **📄 Report Export** - Generate PDF/CSV reports

Configure these in `configs/config.yaml`.

---

## 🐛 Troubleshooting

### "No packets captured"
- Check WiFi is connected: `ip link show wlo1`
- Try: `tshark -i wlo1 -c 5` to test directly

### "API errors (500)"
- Already fixed! Database now has threat_score column
- Restart services: `./start_advanced.sh`

### "Permission denied"
- Run the dumpcap permission commands above
- Or temporarily: `sudo ./start_realtime_detection.sh`

### "Frontend shows no data"
- Wait 10-20 seconds for first packets
- Check Terminal 2 for detection logs
- Verify database: `sqlite3 data/detections.db "SELECT * FROM detections LIMIT 5;"`

---

## 📞 Support

If you still see issues:
1. Check Terminal 1 logs (API/Frontend)
2. Check Terminal 2 logs (Detection)
3. Run: `tshark -i wlo1 -c 10` to verify packet capture works
4. Check `logs/` directory for detailed error logs

---

## ✅ Success Checklist

- [ ] `./start_advanced.sh` running in Terminal 1
- [ ] `./start_realtime_detection.sh` running in Terminal 2
- [ ] Frontend accessible at http://localhost:3000
- [ ] Detection logs showing real packets in Terminal 2
- [ ] Dashboard showing increasing packet counts
- [ ] IP addresses match your real network (192.168.x.x, not 10.x.x.x)

**Now you're monitoring REAL network traffic! 🎉**
