# Network Anomaly Detection - Next.js Frontend

Modern, real-time dashboard for visualizing network intrusion detection data.

## Features

- 🎯 **Real-time Attack Classification** - 8 attack types with live detection counts
- 📊 **Interactive Charts** - Timeline graphs showing packet flow and anomalies
- 🚨 **Alert Monitoring** - Recent detections with severity indicators
- 🌍 **Top Threat Sources** - IP addresses with highest anomaly counts
- ⚡ **Auto-refresh** - Updates every 5 seconds without page reload
- 🎨 **Modern UI** - Dark theme with gradient effects and animations

## Attack Types Detected

1. **DoS/DDoS Attacks** - Server flooding attacks
2. **Port Scanning** - Network vulnerability probing
3. **Brute Force** - Login attempt attacks
4. **SQL Injection & XSS** - Database and script injection
5. **Backdoor & Botnet** - C2 communications
6. **Data Exfiltration** - Unusual data transfers
7. **Man-in-the-Middle** - ARP/DNS hijacking
8. **Zero-Day** - Unknown attack patterns

## Prerequisites

- Node.js 18+ and npm
- Python backend API running on port 5000
- Detection system with populated SQLite database

## Installation

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Python API Server

In the project root (one directory up from frontend):

```bash
# Install Flask dependencies
pip install -r api_requirements.txt

# Start API server
python api_server.py
```

The API will run on `http://localhost:5000`

### 3. Start Next.js Development Server

```bash
npm run dev
```

Access the dashboard at: **http://localhost:3000**

## Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Main dashboard page
│   └── globals.css         # Global styles
├── components/
│   ├── AttackTypeGrid.tsx  # 8 attack type cards
│   ├── StatsCards.tsx      # Overview statistics
│   ├── TimelineChart.tsx   # Detection timeline graph
│   ├── TopSources.tsx      # Top threat IPs
│   └── RecentDetections.tsx # Detection table
├── public/                 # Static assets
├── package.json
├── next.config.js          # API proxy configuration
├── tailwind.config.js      # Styling configuration
└── tsconfig.json           # TypeScript config
```

## API Endpoints Used

| Endpoint | Purpose | Refresh Rate |
|----------|---------|--------------|
| `/api/detections/stats` | Overall statistics | 5s |
| `/api/detections/by-type` | Attack classification | 5s |
| `/api/detections/timeline` | Historical chart data | 10s |
| `/api/detections/recent` | Latest detections | 5s |
| `/api/detections/top-sources` | Top threat IPs | 10s |

## Configuration

### Change API URL

Edit `frontend/components/*.tsx` files and replace:

```typescript
fetch('http://localhost:5000/api/...')
```

With your production API URL.

### Adjust Refresh Intervals

In each component's `useEffect`:

```typescript
const interval = setInterval(fetchData, 5000) // Change 5000ms
```

## Customization

### Colors & Theme

Edit `frontend/app/globals.css`:

```css
:root {
  --background: 222 47% 11%;  /* Dark background */
  --foreground: 213 31% 91%;  /* Text color */
  --border: 216 34% 17%;      /* Border color */
}
```

### Attack Type Icons

Modify `frontend/components/AttackTypeGrid.tsx`:

```typescript
import { YourIcon } from 'lucide-react'

const attackTypes = [
  {
    id: 'dos_ddos',
    icon: YourIcon,  // Change icon
    color: 'red',    // Change color
    // ...
  }
]
```

## Troubleshooting

### "Cannot connect to API"

**Problem**: Frontend can't reach backend

**Solutions**:
1. Ensure API server is running: `python api_server.py`
2. Check API is accessible: `curl http://localhost:5000/health`
3. Verify CORS is enabled in `api_server.py`

### "No data showing"

**Problem**: Database is empty

**Solutions**:
1. Run detection to populate data:
   ```bash
   python anomaly_detection/main.py --mode detect --packet-count 50 --inject-rate 0.2
   ```
2. Verify database has records:
   ```bash
   sqlite3 data/detections.db "SELECT COUNT(*) FROM detections;"
   ```

### "Module not found" errors

**Problem**: Dependencies not installed

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Development Tips

### Hot Reload

Next.js automatically reloads on file changes. Edit components and see updates instantly.

### Debug API Calls

Open browser DevTools → Network tab to see all API requests and responses.

### Add New Attack Type

1. Update `api_server.py` classification logic
2. Add new type to `AttackTypeGrid.tsx`
3. Choose icon from [Lucide Icons](https://lucide.dev)

## Performance

- **Initial Load**: ~2s
- **Auto-refresh**: 5-10s intervals
- **Memory Usage**: ~50-100MB
- **Network**: ~5-10 KB/refresh

## Security Notes

⚠️ **Production Deployment**:

1. **Environment Variables**: Move API URL to `.env.local`
   ```bash
   NEXT_PUBLIC_API_URL=https://your-api.com
   ```

2. **Authentication**: Add JWT/API key authentication to API endpoints

3. **HTTPS**: Use SSL certificates for production

4. **Rate Limiting**: Implement API rate limiting to prevent abuse

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

Part of Network Anomaly Detection System - MIT License

## Support

For issues or questions:
1. Check `logs/anomaly_detection.log`
2. Verify API server is running
3. Test with `curl http://localhost:5000/api/detections/stats`
