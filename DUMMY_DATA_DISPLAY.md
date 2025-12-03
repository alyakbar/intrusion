# Dummy Data Display Feature

## Overview
The system now shows synthetic/dummy data in the live capture feed when running in demo mode with anomaly injection.

## Changes Made

### 1. Backend - realtime_detector.py
**Location:** `anomaly_detection/inference/realtime_detector.py` (lines 460-477)

**What Changed:**
- Modified synthetic packet processing to log ALL packets (both anomalies and normal traffic) to the database
- Previously, only anomalous synthetic packets were logged
- Now normal synthetic packets are also logged with `is_anomaly=False` when `inject_rate > 0`

**Why:**
- The live feed displays data from the database
- Without logging normal synthetic packets, the feed appeared empty or showed only anomalies
- Now you see the full flow of synthetic traffic in demo mode

**Code Change:**
```python
else:
    # Process and log normal synthetic packets so they appear in live feed
    result = self.process_packet(packet_data)
    # Also log non-anomalous synthetic packets to database for live feed
    if inject_rate > 0:  # We're in synthetic mode
        self._log_detection({
            'timestamp': datetime.now(),
            'is_anomaly': False,
            'anomaly_score': 0.0,
            'severity': None,
            'packet_data': packet_data
        })
```

### 2. Frontend - LivePacketCapture.tsx
**Location:** `frontend/components/LivePacketCapture.tsx`

**What Changed:**

#### A) Header displays demo mode status
- Shows "Demo mode (X% synthetic anomalies)" instead of "Real-time network monitoring"
- Checks `systemStatus.process_info.inject_rate` to detect demo mode

#### B) "Dummy Data" badge
- Added amber-colored badge when `inject_rate > 0`
- Appears next to the Active/Idle status
- Clear visual indicator that synthetic data is being generated

**Visual Changes:**
```
Before:
  [WiFi Icon] Live Packet Capture        [Active]
              Real-time network monitoring

After (Demo Mode):
  [WiFi Icon] Live Packet Capture        [Dummy Data] [Active]
              Demo mode (20% synthetic anomalies)
```

## How It Works

### Demo Mode Flow:
1. Start capture with `--inject-rate 0.2` (20% anomalies)
2. Synthetic packets are generated with realistic patterns:
   - Port scanning (30% of traffic)
   - Normal traffic (70% of traffic)
   - Mix of TCP, UDP, ICMP protocols
3. **ALL packets are logged to database** (not just anomalies)
4. Frontend fetches from database and displays in live feed
5. Visual indicators show it's demo mode

### Real Mode Flow:
1. Start capture with `--inject-rate 0` (real packets only)
2. Real network packets are captured via PyShark
3. Only processed packets are logged to database
4. Frontend shows "Real-time network monitoring"
5. No "Dummy Data" badge appears

## Testing

### Start Demo Mode:
```bash
./capture_example_anomalies.sh
```

### What You Should See:
1. **Dashboard header:** "Demo mode (20% synthetic anomalies)"
2. **Badge:** Amber "Dummy Data" badge appears
3. **Live feed:** Shows both anomalies and normal traffic
4. **Activity:** Continuous packet flow with realistic patterns
5. **Mix of traffic:**
   - Green checkmarks = normal packets
   - Red X marks = anomalous packets (port scans, etc.)

### Start Real Mode:
```bash
./start_realtime_detection.sh
```

### What You Should See:
1. **Dashboard header:** "Real-time network monitoring"
2. **No dummy badge:** Only Active/Idle status
3. **Live feed:** Shows actual network packets from WiFi
4. **Real activity:** Based on your actual network usage

## Benefits

### Before This Change:
- ❌ Synthetic mode generated packets but they weren't visible in live feed
- ❌ Users couldn't see the demo working
- ❌ No indication of synthetic vs real mode
- ❌ Database only had anomalies, not full traffic picture

### After This Change:
- ✅ All synthetic packets appear in live feed
- ✅ Clear visual indicator of demo mode
- ✅ Percentage of anomaly injection displayed
- ✅ Full traffic picture (anomalies + normal) in database
- ✅ Users can see the demo working in real-time
- ✅ Easy to distinguish demo from real capture

## Technical Details

### Database Impact:
- **Demo mode:** Higher insert rate (all synthetic packets logged)
- **Real mode:** Only processed packets logged
- Storage considerations: Demo mode generates ~1 packet per 0.5s (configurable)

### API Response:
The `/api/system/status` endpoint includes:
```json
{
  "process_info": {
    "inject_rate": 0.2,  // 0.2 = 20% synthetic anomalies
    "interface": "wlo1",
    "backend": "pyshark"
  },
  "is_capturing_packets": true,
  "status": "active"
}
```

Frontend checks `process_info.inject_rate` to show/hide the "Dummy Data" badge.

## Files Modified:
1. `anomaly_detection/inference/realtime_detector.py` - Log all synthetic packets
2. `frontend/components/LivePacketCapture.tsx` - Display demo mode indicators

## No Restart Needed:
- Backend changes apply to NEW detection sessions
- Frontend changes: Next.js dev server auto-reloads (Fast Refresh)
- Just reload browser to see changes

## Usage:

### To see dummy data in action:
```bash
# Stop any existing detection
pkill -f "anomaly_detection.main"

# Start demo mode
./capture_example_anomalies.sh

# Open dashboard
# http://localhost:3000
```

Look for:
- 🟡 Amber "Dummy Data" badge
- 📊 Packet flow in live feed
- 🔢 Growing packet counts
- ⚠️ Anomalies marked in red
