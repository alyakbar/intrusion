"""
Threat intelligence feed integration.
Enriches detections with threat data from external sources.
"""

import requests
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import time
from ..utils.logger import LoggerFactory


class ThreatIntelProvider(ABC):
    """Base class for threat intelligence providers."""
    
    def __init__(self, api_key: str, config: Dict[str, Any]):
        """
        Initialize provider.
        
        Args:
            api_key: API key for the service
            config: Provider-specific configuration
        """
        self.api_key = api_key
        self.config = config
        self.logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.cache = {}
        self.cache_ttl = config.get('cache_ttl', 3600)  # 1 hour default
    
    @abstractmethod
    def lookup_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Lookup IP reputation.
        
        Args:
            ip_address: IP address to lookup
            
        Returns:
            Threat intelligence data
        """
        pass
    
    def _check_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Check if cached data is available and valid."""
        if key in self.cache:
            cached_data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        return None
    
    def _update_cache(self, key: str, data: Dict[str, Any]):
        """Update cache with new data."""
        self.cache[key] = (data, time.time())


class AbuseIPDBProvider(ThreatIntelProvider):
    """AbuseIPDB threat intelligence provider."""
    
    BASE_URL = "https://api.abuseipdb.com/api/v2"
    
    def lookup_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Lookup IP on AbuseIPDB.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            Reputation data including abuse confidence score
        """
        # Check cache
        cached = self._check_cache(ip_address)
        if cached:
            self.logger.debug(f"Using cached AbuseIPDB data for {ip_address}")
            return cached
        
        try:
            headers = {
                'Key': self.api_key,
                'Accept': 'application/json'
            }
            
            params = {
                'ipAddress': ip_address,
                'maxAgeInDays': self.config.get('max_age_days', 90),
                'verbose': ''
            }
            
            response = requests.get(
                f"{self.BASE_URL}/check",
                headers=headers,
                params=params,
                timeout=self.config.get('timeout', 10)
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    'provider': 'abuseipdb',
                    'ip': ip_address,
                    'abuse_confidence_score': data.get('data', {}).get('abuseConfidenceScore', 0),
                    'country_code': data.get('data', {}).get('countryCode', 'Unknown'),
                    'usage_type': data.get('data', {}).get('usageType', 'Unknown'),
                    'isp': data.get('data', {}).get('isp', 'Unknown'),
                    'domain': data.get('data', {}).get('domain', 'Unknown'),
                    'total_reports': data.get('data', {}).get('totalReports', 0),
                    'is_public': data.get('data', {}).get('isPublic', True),
                    'is_whitelisted': data.get('data', {}).get('isWhitelisted', False)
                }
                
                self._update_cache(ip_address, result)
                return result
            else:
                self.logger.error(f"AbuseIPDB API error: {response.status_code}")
                return {'provider': 'abuseipdb', 'ip': ip_address, 'error': f"HTTP {response.status_code}"}
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"AbuseIPDB request failed: {e}")
            return {'provider': 'abuseipdb', 'ip': ip_address, 'error': str(e)}


class VirusTotalProvider(ThreatIntelProvider):
    """VirusTotal threat intelligence provider."""
    
    BASE_URL = "https://www.virustotal.com/api/v3"
    
    def lookup_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Lookup IP on VirusTotal.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            Reputation data including malicious detections
        """
        # Check cache
        cached = self._check_cache(ip_address)
        if cached:
            self.logger.debug(f"Using cached VirusTotal data for {ip_address}")
            return cached
        
        try:
            headers = {
                'x-apikey': self.api_key
            }
            
            response = requests.get(
                f"{self.BASE_URL}/ip_addresses/{ip_address}",
                headers=headers,
                timeout=self.config.get('timeout', 10)
            )
            
            if response.status_code == 200:
                data = response.json()
                attributes = data.get('data', {}).get('attributes', {})
                stats = attributes.get('last_analysis_stats', {})
                
                result = {
                    'provider': 'virustotal',
                    'ip': ip_address,
                    'malicious': stats.get('malicious', 0),
                    'suspicious': stats.get('suspicious', 0),
                    'harmless': stats.get('harmless', 0),
                    'undetected': stats.get('undetected', 0),
                    'reputation': attributes.get('reputation', 0),
                    'country': attributes.get('country', 'Unknown'),
                    'asn': attributes.get('asn', 'Unknown'),
                    'as_owner': attributes.get('as_owner', 'Unknown'),
                    'network': attributes.get('network', 'Unknown')
                }
                
                self._update_cache(ip_address, result)
                return result
            else:
                self.logger.error(f"VirusTotal API error: {response.status_code}")
                return {'provider': 'virustotal', 'ip': ip_address, 'error': f"HTTP {response.status_code}"}
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"VirusTotal request failed: {e}")
            return {'provider': 'virustotal', 'ip': ip_address, 'error': str(e)}


class ThreatIntelligence:
    """Threat intelligence aggregator."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize threat intelligence.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config.get('threat_intel', {})
        self.logger = LoggerFactory.get_logger('ThreatIntelligence')
        self.providers = []
        
        # Initialize providers
        if self.config.get('enabled', False):
            self._init_providers()
    
    def _init_providers(self):
        """Initialize configured providers."""
        # AbuseIPDB
        abuseipdb_config = self.config.get('abuseipdb', {})
        if abuseipdb_config.get('enabled', False):
            api_key = abuseipdb_config.get('api_key')
            if api_key:
                provider = AbuseIPDBProvider(api_key, abuseipdb_config)
                self.providers.append(provider)
                self.logger.info("AbuseIPDB provider initialized")
        
        # VirusTotal
        virustotal_config = self.config.get('virustotal', {})
        if virustotal_config.get('enabled', False):
            api_key = virustotal_config.get('api_key')
            if api_key:
                provider = VirusTotalProvider(api_key, virustotal_config)
                self.providers.append(provider)
                self.logger.info("VirusTotal provider initialized")
    
    def enrich_detection(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich detection with threat intelligence.
        
        Args:
            detection: Detection dictionary
            
        Returns:
            Enriched detection with threat data
        """
        if not self.providers:
            return detection
        
        src_ip = detection.get('src_ip')
        dst_ip = detection.get('dst_ip')
        
        threat_data = {}
        
        # Lookup source IP
        if src_ip:
            threat_data['src_threat_intel'] = self._lookup_ip_all_providers(src_ip)
        
        # Lookup destination IP
        if dst_ip:
            threat_data['dst_threat_intel'] = self._lookup_ip_all_providers(dst_ip)
        
        # Add threat data to detection
        detection['threat_intel'] = threat_data
        
        # Calculate threat score
        detection['threat_score'] = self._calculate_threat_score(threat_data)
        
        return detection
    
    def _lookup_ip_all_providers(self, ip_address: str) -> Dict[str, Any]:
        """Lookup IP across all providers."""
        results = {}
        
        for provider in self.providers:
            try:
                result = provider.lookup_ip(ip_address)
                provider_name = provider.__class__.__name__.replace('Provider', '').lower()
                results[provider_name] = result
            except Exception as e:
                self.logger.error(f"Provider {provider.__class__.__name__} lookup failed: {e}")
        
        return results
    
    def _calculate_threat_score(self, threat_data: Dict[str, Any]) -> float:
        """
        Calculate aggregate threat score.
        
        Args:
            threat_data: Threat intelligence data
            
        Returns:
            Threat score between 0-100
        """
        scores = []
        
        # Source IP threats
        src_intel = threat_data.get('src_threat_intel', {})
        
        if 'abuseipdb' in src_intel:
            abuse_score = src_intel['abuseipdb'].get('abuse_confidence_score', 0)
            scores.append(abuse_score)
        
        if 'virustotal' in src_intel:
            vt_malicious = src_intel['virustotal'].get('malicious', 0)
            vt_suspicious = src_intel['virustotal'].get('suspicious', 0)
            if vt_malicious + vt_suspicious > 0:
                # Normalize to 0-100 scale
                vt_score = min(100, (vt_malicious * 10 + vt_suspicious * 5))
                scores.append(vt_score)
        
        # Destination IP threats (weighted lower)
        dst_intel = threat_data.get('dst_threat_intel', {})
        
        if 'abuseipdb' in dst_intel:
            abuse_score = dst_intel['abuseipdb'].get('abuse_confidence_score', 0)
            scores.append(abuse_score * 0.5)
        
        if 'virustotal' in dst_intel:
            vt_malicious = dst_intel['virustotal'].get('malicious', 0)
            if vt_malicious > 0:
                vt_score = min(100, vt_malicious * 5)
                scores.append(vt_score * 0.5)
        
        # Return average score
        return sum(scores) / len(scores) if scores else 0.0
