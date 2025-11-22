#!/usr/bin/env python3
"""
Command-line port scanner utility
"""

import argparse
import json
import sys
from anomaly_detection.scanning.port_scanner import PortScanner


def main():
    parser = argparse.ArgumentParser(
        description='Network Port Scanner - Discover open ports on hosts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick scan of common ports
  python scan_ports.py --host 192.168.1.1 --quick
  
  # Scan specific ports
  python scan_ports.py --host example.com --ports 80,443,8080
  
  # Scan port range
  python scan_ports.py --host 192.168.1.1 --range 1-1000
  
  # Scan network range
  python scan_ports.py --network 192.168.1.0/24 --quick
  
  # Full port scan (slow!)
  python scan_ports.py --host 192.168.1.1 --full
        """
    )
    
    parser.add_argument('--host', help='Target host IP or hostname')
    parser.add_argument('--network', help='Network range in CIDR notation (e.g., 192.168.1.0/24)')
    parser.add_argument('--ports', help='Comma-separated list of ports (e.g., 80,443,8080)')
    parser.add_argument('--range', help='Port range (e.g., 1-1000)')
    parser.add_argument('--quick', action='store_true', help='Quick scan of common ports')
    parser.add_argument('--full', action='store_true', help='Full scan of all 65535 ports (very slow!)')
    parser.add_argument('--timeout', type=float, default=1.0, help='Connection timeout in seconds (default: 1.0)')
    parser.add_argument('--workers', type=int, default=100, help='Max concurrent threads (default: 100)')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.host and not args.network:
        parser.error('Either --host or --network is required')
    
    if args.network and args.full:
        parser.error('Full scan not supported for network ranges (too slow)')
    
    # Initialize scanner
    scanner = PortScanner(timeout=args.timeout, max_workers=args.workers)
    
    try:
        if args.network:
            # Scan network range
            ports = None
            if args.ports:
                ports = [int(p.strip()) for p in args.ports.split(',')]
            elif args.quick:
                ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 8080]
            
            print(f"Scanning network {args.network}...")
            results = scanner.scan_range(args.network, ports)
            
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(f"\n{'='*60}")
                print(f"Network Scan Results: {args.network}")
                print(f"{'='*60}\n")
                
                for result in results:
                    print(f"Host: {result['host']}")
                    print(f"  Open Ports: {result['open_count']}")
                    for port in result['open_ports']:
                        print(f"    {port['port']}/tcp - {port['service']}")
                    print()
        
        else:
            # Scan single host
            if args.full:
                print(f"⚠️  WARNING: Full port scan of {args.host} - This will take a LONG time!")
                result = scanner.full_scan(args.host)
            elif args.quick:
                result = scanner.quick_scan(args.host)
            elif args.range:
                start, end = map(int, args.range.split('-'))
                result = scanner.scan_port_range(args.host, start, end)
            elif args.ports:
                ports = [int(p.strip()) for p in args.ports.split(',')]
                result = scanner.scan_host(args.host, ports)
            else:
                # Default: scan common ports
                result = scanner.scan_host(args.host)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"\n{'='*60}")
                print(f"Port Scan Results: {result['host']}")
                print(f"{'='*60}")
                print(f"Scan Duration: {result['duration']:.2f} seconds")
                print(f"Ports Scanned: {result['ports_scanned']}")
                print(f"Open Ports: {result['open_count']}\n")
                
                if result['open_ports']:
                    print("PORT     STATE    SERVICE")
                    print("-" * 40)
                    for port in result['open_ports']:
                        print(f"{port['port']:<8} {port['state']:<8} {port['service']}")
                else:
                    print("No open ports found.")
                
                print()
    
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
