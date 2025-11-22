# Attack Detail Pages - Feature Documentation

## Overview
Added detailed attack information pages that display comprehensive information when you click on any attack type card from the dashboard.

## Features Added

### 1. Dynamic Attack Detail Pages
- **Route**: `/attacks/[type]` (e.g., `/attacks/dos_ddos`, `/attacks/port_scan`)
- **File**: `frontend/app/attacks/[type]/page.tsx`

### 2. What Each Attack Page Shows

#### Top Section
- **Attack icon and title** with color-coded branding
- **Back button** to return to main dashboard
- **Description** of the attack type

#### Statistics Cards (4 cards)
1. **Total Detections** - Overall count for this attack type
2. **High Severity** - Critical threats (red)
3. **Medium Severity** - Moderate threats (yellow)
4. **Low Severity** - Minor threats (blue)

#### Information Panels (3 panels)
1. **Attack Characteristics**
   - How to identify this attack
   - Behavioral patterns
   - Network signatures

2. **Common Targets**
   - What services/systems are typically attacked
   - Vulnerable infrastructure

3. **Prevention & Mitigation**
   - Security best practices
   - Tools and techniques to defend
   - Configuration recommendations

#### Recent Detections Table
- **Live data table** showing up to 50 recent detections
- **Columns**:
  - Timestamp (formatted: Nov 22, 11:20:45)
  - Source IP
  - Destination IP
  - Protocol (with badge)
  - Anomaly Score (visual progress bar + number)
  - Severity (color-coded badge)
- **Auto-refresh** every 5 seconds

### 3. Interactive Features

#### Clickable Attack Cards
- Click any attack type card on the main dashboard
- Instantly navigate to detailed attack page
- Hover effect shows it's clickable (scale up + shadow)

#### Visual Feedback
- Cards scale up on hover (105%)
- Enhanced shadow on interaction
- Cursor changes to pointer

### 4. Attack Types Covered

All 8 attack types have dedicated detail pages:

1. **DoS/DDoS Attacks** (`/attacks/dos_ddos`) - Red theme
2. **Port Scanning** (`/attacks/port_scan`) - Orange theme  
3. **Brute Force** (`/attacks/brute_force`) - Yellow theme
4. **SQL Injection & XSS** (`/attacks/sql_xss`) - Pink theme
5. **Backdoor & Botnet** (`/attacks/backdoor_botnet`) - Purple theme
6. **Data Exfiltration** (`/attacks/data_exfiltration`) - Blue theme
7. **Man-in-the-Middle** (`/attacks/mitm`) - Green theme
8. **Zero-Day Attacks** (`/attacks/zero_day`) - Cyan theme

## How to Use

### From the Dashboard
1. Open dashboard at `http://localhost:3000`
2. Scroll to "Attack Classification" section
3. Click on any attack type card
4. View detailed information and recent detections
5. Click back arrow to return to dashboard

### Direct URL Access
You can also directly navigate to attack pages:
```
http://localhost:3000/attacks/dos_ddos
http://localhost:3000/attacks/port_scan
http://localhost:3000/attacks/brute_force
http://localhost:3000/attacks/sql_xss
http://localhost:3000/attacks/backdoor_botnet
http://localhost:3000/attacks/data_exfiltration
http://localhost:3000/attacks/mitm
http://localhost:3000/attacks/zero_day
```

## Technical Details

### Components Modified
1. **AttackTypeGrid.tsx**
   - Added `useRouter` from Next.js
   - Added `onClick` handler to navigate to detail pages
   - Enhanced hover effects for better UX

2. **New Page**: `/attacks/[type]/page.tsx`
   - Dynamic route parameter `[type]`
   - Real-time data fetching from API
   - Comprehensive attack information
   - Auto-refresh every 5 seconds

### API Endpoints Used
- `GET /api/detections/by-type` - Fetches all detections grouped by attack type
- Returns both counts and full detection arrays

### Styling
- Consistent with dashboard theme (dark mode)
- Color-coded by attack severity
- Responsive design (mobile-friendly)
- Smooth transitions and animations

## Example Data Structure

```typescript
// What the API returns
{
  "counts": {
    "dos_ddos": 178,
    "port_scan": 0,
    "brute_force": 0,
    ...
  },
  "detections": {
    "dos_ddos": [
      {
        "id": 1234,
        "timestamp": "2025-11-22T11:20:45Z",
        "source_ip": "192.168.0.101",
        "dest_ip": "192.168.1.50",
        "protocol": "TCP",
        "anomaly_score": 0.9823,
        "severity": "high"
      },
      ...
    ]
  }
}
```

## Future Enhancements (Optional)

- Export detection data to CSV/JSON
- Filter by date range
- Search by IP address
- Real-time chart showing detection timeline
- Detailed packet inspection modal
- Threat intelligence integration
- Automatic remediation suggestions

## Testing

To see the feature in action:

1. Make sure detection is running:
   ```bash
   ./start_detection_demo.sh
   ```

2. Open browser: `http://localhost:3000`

3. Click on any attack type with detections (showing a number badge)

4. Verify:
   - Page loads correctly
   - Statistics are displayed
   - Attack information panels show content
   - Detection table populates with data
   - Data refreshes automatically
   - Back button returns to dashboard

## Troubleshooting

**Issue**: Clicking card does nothing
- **Solution**: Make sure frontend is running (`npm run dev` in `frontend/` directory)

**Issue**: Page shows "No detections found"
- **Solution**: Start the detection script to generate data

**Issue**: Stats show 0 for all attack types
- **Solution**: Check if API server is running on port 5000

**Issue**: Page crashes or shows error
- **Solution**: Check browser console for errors, verify API endpoint is accessible
