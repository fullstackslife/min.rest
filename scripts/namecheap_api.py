import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

# Define the Namecheap API namespace
NAMECHEAP_NS = {'nc': 'http://api.namecheap.com/xml.response'}

class NamecheapAPI:
    def __init__(self, api_user: str, api_key: str, username: str, client_ip: str, sandbox: bool = False):
        self.api_user = api_user
        self.api_key = api_key
        self.username = username
        self.client_ip = client_ip
        self.base_url = "https://api.sandbox.namecheap.com/xml.response" if sandbox else "https://api.namecheap.com/xml.response"
        logger.info(f"Initialized NamecheapAPI with {'sandbox' if sandbox else 'production'} mode")
        
    def _make_request(self, command: str, params: Dict) -> Dict:
        """Make a request to the Namecheap API."""
        start_time = time.time()
        try:
            # Add required parameters
            params.update({
                'ApiUser': self.api_user,
                'ApiKey': self.api_key,
                'UserName': self.username,
                'ClientIp': self.client_ip,
                'Command': command
            })
            
            # Log request details (excluding sensitive data)
            safe_params = params.copy()
            safe_params['ApiKey'] = '***'  # Mask API key in logs
            logger.debug(f"Making request to {self.base_url}")
            logger.debug(f"Command: {command}")
            logger.debug(f"Params: {safe_params}")
            
            # Make the request
            response = requests.get(self.base_url, params=params)
            response_time = time.time() - start_time
            logger.debug(f"Request completed in {response_time:.2f} seconds")
            
            # Log response status
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Check HTTP status
            response.raise_for_status()
            
            # Log raw response content
            logger.debug(f"Raw response content: {response.content}")
            
            # Parse XML response
            try:
                root = ET.fromstring(response.content)
            except ET.ParseError as e:
                logger.error(f"Failed to parse XML response: {str(e)}")
                logger.error(f"Raw response: {response.content}")
                raise Exception(f"Invalid XML response: {str(e)}")
            
            # Check for errors in the response
            if root.attrib.get('Status') == 'ERROR':
                error = root.find('.//nc:Error', NAMECHEAP_NS)
                if error is not None:
                    error_msg = error.text
                    error_number = error.attrib.get('Number', 'Unknown')
                    logger.error(f"Namecheap API Error #{error_number}: {error_msg}")
                    if error_number == '1011102':
                        raise Exception("API Key is invalid or API access has not been enabled. Please check your API credentials and ensure API access is enabled in your Namecheap account.")
                    raise Exception(f"Namecheap API Error #{error_number}: {error_msg}")
                else:
                    error_msg = "Unknown error - no error message found in response"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            
            # Parse and return response
            result = self._parse_response(root)
            logger.debug(f"Successfully parsed response for command: {command}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response content: {e.response.content}")
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise Exception(f"Unexpected error: {str(e)}")
    
    def _parse_response(self, root: ET.Element) -> Dict:
        """Parse the XML response from Namecheap API."""
        result = {}
        command_response = root.find('.//nc:CommandResponse', NAMECHEAP_NS)
        if command_response is not None:
            result = self._parse_command_response(command_response)
        return result
    
    def _parse_command_response(self, element: ET.Element) -> Dict:
        """Parse the CommandResponse section of the API response."""
        result = {}
        hosts_result = element.find('.//nc:DomainDNSGetHostsResult', NAMECHEAP_NS)
        if hosts_result is not None:
            result['hosts'] = self._parse_hosts(hosts_result)
        domains_result = element.find('.//nc:DomainDNSGetListResult', NAMECHEAP_NS)
        if domains_result is not None:
            result['domains'] = self._parse_domains(domains_result)
        return result
    
    def _parse_hosts(self, element: ET.Element) -> List[Dict]:
        """Parse the hosts section of the API response."""
        hosts = []
        for host in element.findall('.//nc:host', NAMECHEAP_NS):
            hosts.append({
                'host_id': host.attrib.get('HostId'),
                'name': host.attrib.get('Name'),
                'type': host.attrib.get('Type'),
                'address': host.attrib.get('Address'),
                'mx_pref': host.attrib.get('MXPref'),
                'ttl': host.attrib.get('TTL')
            })
        return hosts
    
    def _parse_domains(self, element: ET.Element) -> List[Dict]:
        """Parse the domains section of the API response."""
        domains = []
        for domain in element.findall('.//nc:Domain', NAMECHEAP_NS):
            domains.append({
                'name': domain.attrib.get('Name'),
                'is_locked': domain.attrib.get('IsLocked') == 'true',
                'expires': datetime.strptime(domain.attrib.get('Expires'), '%m/%d/%Y').isoformat()
            })
        return domains
    
    def get_dns_records(self, domain: str) -> List[Dict]:
        """Get all DNS records for a domain."""
        params = {
            'SLD': domain.split('.')[0],
            'TLD': domain.split('.')[1]
        }
        response = self._make_request('namecheap.domains.dns.getHosts', params)
        return response.get('hosts', [])
    
    def add_dns_record(self, domain: str, record_type: str, name: str, address: str, 
                      mx_pref: Optional[int] = None, ttl: int = 1800) -> bool:
        """Add a new DNS record."""
        params = {
            'SLD': domain.split('.')[0],
            'TLD': domain.split('.')[1],
            'RecordType': record_type,
            'HostName': name,
            'Address': address,
            'TTL': ttl
        }
        
        if record_type == 'MX' and mx_pref is not None:
            params['MXPref'] = mx_pref
        
        try:
            self._make_request('namecheap.domains.dns.setHosts', params)
            return True
        except Exception as e:
            logger.error(f"Error adding DNS record: {str(e)}")
            return False
    
    def update_dns_record(self, domain: str, host_id: str, record_type: str, name: str, 
                         address: str, mx_pref: Optional[int] = None, ttl: int = 1800) -> bool:
        """Update an existing DNS record."""
        params = {
            'SLD': domain.split('.')[0],
            'TLD': domain.split('.')[1],
            'HostId': host_id,
            'RecordType': record_type,
            'HostName': name,
            'Address': address,
            'TTL': ttl
        }
        
        if record_type == 'MX' and mx_pref is not None:
            params['MXPref'] = mx_pref
        
        try:
            self._make_request('namecheap.domains.dns.setHosts', params)
            return True
        except Exception as e:
            logger.error(f"Error updating DNS record: {str(e)}")
            return False
    
    def delete_dns_record(self, domain: str, host_id: str) -> bool:
        """Delete a DNS record."""
        params = {
            'SLD': domain.split('.')[0],
            'TLD': domain.split('.')[1],
            'HostId': host_id
        }
        
        try:
            self._make_request('namecheap.domains.dns.delHost', params)
            return True
        except Exception as e:
            logger.error(f"Error deleting DNS record: {str(e)}")
            return False
    
    def get_domains(self) -> List[Dict]:
        """Get list of domains."""
        response = self._make_request('namecheap.domains.getList', {})
        return response.get('domains', []) 