import os
import shutil
from pathlib import Path
import json
from typing import Dict, List, Optional
import sys
from datetime import datetime
from namecheap_api import NamecheapAPI

class DomainManager:
    def __init__(self, workspace_root: str = ".", namecheap_config: Optional[Dict] = None):
        self.workspace_root = Path(workspace_root)
        self.namecheap_api = None
        if namecheap_config:
            self.namecheap_api = NamecheapAPI(
                api_user=namecheap_config.get('api_user'),
                api_key=namecheap_config.get('api_key'),
                username=namecheap_config.get('username'),
                client_ip=namecheap_config.get('client_ip'),
                sandbox=namecheap_config.get('sandbox', False)
            )
        self.domain_structure = {
            "content": {
                "context.md": None,
                "pages": {},
                "blog": {},
                "records": {
                    "data.json": None,  # Store structured records
                    "schema.json": None,  # Store record schemas
                    "dns.json": None  # Store DNS records
                }
            },
            "assets": {
                "images": {
                    "logos": {},
                    "hero": {},
                    "gallery": {},
                },
                "media": {},
            },
            "config": {
                "settings.json": None,
                "seo.json": None,
            }
        }

    def create_domain(self, domain_name: str) -> bool:
        """Create a new domain with proper directory structure."""
        try:
            domain_path = self.workspace_root / domain_name
            if domain_path.exists():
                print(f"Domain {domain_name} already exists!")
                return False

            # Create base domain directory
            domain_path.mkdir(parents=True)

            # Create directory structure
            self._create_directory_structure(domain_path, self.domain_structure)

            # Initialize default files
            self._initialize_default_files(domain_path, domain_name)

            print(f"Successfully created domain: {domain_name}")
            return True
        except Exception as e:
            print(f"Error creating domain {domain_name}: {str(e)}")
            return False

    def _create_directory_structure(self, base_path: Path, structure: Dict):
        """Recursively create directory structure."""
        for name, content in structure.items():
            path = base_path / name
            if content is None:  # It's a file
                path.touch(exist_ok=True)
            else:  # It's a directory
                path.mkdir(exist_ok=True)
                self._create_directory_structure(path, content)

    def _initialize_default_files(self, domain_path: Path, domain_name: str):
        """Initialize default files for a new domain."""
        # Create default context.md
        context_path = domain_path / "content" / "context.md"
        with open(context_path, "w", encoding="utf-8") as f:
            f.write(f"# {domain_name}\n\n## Domain Information\n\n")

        # Create default settings.json
        settings_path = domain_path / "config" / "settings.json"
        default_settings = {
            "domain": domain_name,
            "theme": "default",
            "features": [],
            "integrations": {
                "brevo": {
                    "enabled": False,
                    "form_id": ""
                }
            }
        }
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(default_settings, f, indent=2)

        # Create default seo.json
        seo_path = domain_path / "config" / "seo.json"
        default_seo = {
            "title": domain_name,
            "description": f"Welcome to {domain_name}",
            "keywords": [],
            "social": {
                "og_image": "",
                "twitter_card": ""
            }
        }
        with open(seo_path, "w", encoding="utf-8") as f:
            json.dump(default_seo, f, indent=2)

        # Create default dns.json
        dns_path = domain_path / "content" / "records" / "dns.json"
        default_dns = {
            "records": {
                "A": [],
                "CNAME": [],
                "MX": [],
                "TXT": [],
                "NS": []
            },
            "last_updated": datetime.now().isoformat()
        }
        with open(dns_path, "w", encoding="utf-8") as f:
            json.dump(default_dns, f, indent=2)

    def delete_domain(self, domain_name: str) -> bool:
        """Delete a domain and all its contents."""
        try:
            domain_path = self.workspace_root / domain_name
            if not domain_path.exists():
                print(f"Domain {domain_name} does not exist!")
                return False

            shutil.rmtree(domain_path)
            print(f"Successfully deleted domain: {domain_name}")
            return True
        except Exception as e:
            print(f"Error deleting domain {domain_name}: {str(e)}")
            return False

    def list_domains(self) -> List[str]:
        """List all domains in the workspace."""
        return [d.name for d in self.workspace_root.iterdir() if d.is_dir()]

    def update_context(self, domain_name: str, content: str) -> bool:
        """Update the context.md file for a domain."""
        try:
            context_path = self.workspace_root / domain_name / "content" / "context.md"
            if not context_path.exists():
                print(f"Context file for {domain_name} does not exist!")
                return False

            with open(context_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Successfully updated context for {domain_name}")
            return True
        except Exception as e:
            print(f"Error updating context for {domain_name}: {str(e)}")
            return False

    def add_asset(self, domain_name: str, asset_type: str, source_path: str, asset_name: Optional[str] = None) -> bool:
        """Add an asset to a domain's asset directory."""
        try:
            if asset_type not in ["logo", "hero", "gallery", "media"]:
                print(f"Invalid asset type: {asset_type}")
                return False

            source = Path(source_path)
            if not source.exists():
                print(f"Source file {source_path} does not exist!")
                return False

            # Determine target directory based on asset type
            if asset_type in ["logo", "hero", "gallery"]:
                target_dir = self.workspace_root / domain_name / "assets" / "images" / asset_type
            else:
                target_dir = self.workspace_root / domain_name / "assets" / "media"

            target_dir.mkdir(parents=True, exist_ok=True)

            # Use provided name or original filename
            target_name = asset_name if asset_name else source.name
            target_path = target_dir / target_name

            shutil.copy2(source, target_path)
            print(f"Successfully added asset {target_name} to {domain_name}")
            return True
        except Exception as e:
            print(f"Error adding asset to {domain_name}: {str(e)}")
            return False

    def create_domain_template(self, domain_name):
        """Create a template structure for a new domain with consistent context management."""
        try:
            # Create main domain directory
            domain_path = os.path.join(os.getcwd(), domain_name)
            os.makedirs(domain_path, exist_ok=True)
            
            # Create .context directory and its subdirectories
            context_path = os.path.join(domain_path, '.context')
            os.makedirs(context_path, exist_ok=True)
            os.makedirs(os.path.join(context_path, 'assets'), exist_ok=True)
            os.makedirs(os.path.join(context_path, 'templates'), exist_ok=True)
            
            # Create assets directory
            os.makedirs(os.path.join(domain_path, 'assets'), exist_ok=True)
            
            # Create default context.md template
            context_template = """# Domain Context for {domain_name}

## Site Information
- Domain: {domain_name}
- Created: {date}
- Status: Active

## Content Structure
- Home Page
- About Page
- Services Page
- Contact Page

## Customization Notes
Add your domain-specific content and customization instructions here.

## Assets
- Logo: assets/logo.png
- Favicon: assets/favicon.ico

## Page Templates
Custom page templates can be added in the .context/templates directory.

## SEO Configuration
- Meta Title: 
- Meta Description: 
- Keywords: 

## Custom Scripts
Add any custom JavaScript or CSS requirements here.

## Contact Information
- Email: 
- Phone: 
- Address: 

## Social Media
- Facebook: 
- Twitter: 
- LinkedIn: 
- Instagram: 

## Analytics
- Google Analytics ID: 
- Other Tracking Codes: 
""".format(domain_name=domain_name, date=datetime.now().strftime('%Y-%m-%d'))
            
            with open(os.path.join(context_path, 'context.md'), 'w') as f:
                f.write(context_template)
            
            # Create .gitignore
            gitignore_content = """# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE files
.idea/
.vscode/
*.swp
*.swo

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Dependencies
node_modules/
vendor/

# Build files
dist/
build/
out/

# Environment files
.env
.env.local
.env.*.local

# Context files
.context/
"""
            with open(os.path.join(domain_path, '.gitignore'), 'w') as f:
                f.write(gitignore_content)
            
            # Create CNAME file
            with open(os.path.join(domain_path, 'CNAME'), 'w') as f:
                f.write(domain_name)
            
            print(f"Template structure created for {domain_name}")
            return True
        except Exception as e:
            print(f"Error creating template for {domain_name}: {str(e)}")
            return False

    def add_record(self, domain_name: str, record_type: str, data: Dict) -> bool:
        """Add a new record to the domain's records collection."""
        try:
            domain_path = self.workspace_root / domain_name
            records_path = domain_path / "content" / "records" / "data.json"
            
            # Load existing records
            records = {}
            if records_path.exists():
                with open(records_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            
            # Initialize record type if it doesn't exist
            if record_type not in records:
                records[record_type] = []
            
            # Add metadata to record
            record_data = {
                **data,
                'id': str(len(records[record_type]) + 1),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            records[record_type].append(record_data)
            
            # Save updated records
            with open(records_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding record: {str(e)}")
            return False

    def get_records(self, domain_name: str, record_type: Optional[str] = None) -> Dict:
        """Get records for a domain, optionally filtered by type."""
        try:
            domain_path = self.workspace_root / domain_name
            records_path = domain_path / "content" / "records" / "data.json"
            
            if not records_path.exists():
                return {}
            
            with open(records_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            if record_type:
                return records.get(record_type, [])
            
            return records
        except Exception as e:
            print(f"Error getting records: {str(e)}")
            return {}

    def update_record(self, domain_name: str, record_type: str, record_id: str, data: Dict) -> bool:
        """Update an existing record."""
        try:
            domain_path = self.workspace_root / domain_name
            records_path = domain_path / "content" / "records" / "data.json"
            
            if not records_path.exists():
                return False
            
            with open(records_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            if record_type not in records:
                return False
            
            # Find and update record
            for record in records[record_type]:
                if record['id'] == record_id:
                    record.update(data)
                    record['updated_at'] = datetime.now().isoformat()
                    break
            
            # Save updated records
            with open(records_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating record: {str(e)}")
            return False

    def delete_record(self, domain_name: str, record_type: str, record_id: str) -> bool:
        """Delete a record from the domain's records."""
        try:
            domain_path = self.workspace_root / domain_name
            records_path = domain_path / "content" / "records" / "data.json"
            
            if not records_path.exists():
                return False
            
            with open(records_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            if record_type not in records:
                return False
            
            # Remove record
            records[record_type] = [r for r in records[record_type] if r['id'] != record_id]
            
            # Save updated records
            with open(records_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error deleting record: {str(e)}")
            return False

    def get_dns_records(self, domain_name: str, record_type: Optional[str] = None) -> Dict:
        """Get DNS records for a domain, optionally filtered by type."""
        try:
            domain_path = self.workspace_root / domain_name
            dns_path = domain_path / "content" / "records" / "dns.json"
            
            if not dns_path.exists():
                return {"records": {}}
            
            with open(dns_path, 'r', encoding='utf-8') as f:
                dns_data = json.load(f)
            
            if record_type:
                return {"records": {record_type: dns_data["records"].get(record_type, [])}}
            
            return dns_data
        except Exception as e:
            print(f"Error getting DNS records: {str(e)}")
            return {"records": {}}

    def add_dns_record(self, domain_name: str, record_type: str, record_data: Dict) -> bool:
        """Add a new DNS record."""
        try:
            domain_path = self.workspace_root / domain_name
            dns_path = domain_path / "content" / "records" / "dns.json"
            
            if not dns_path.exists():
                return False
            
            with open(dns_path, 'r', encoding='utf-8') as f:
                dns_data = json.load(f)
            
            if record_type not in dns_data["records"]:
                return False
            
            # Add metadata to record
            record = {
                **record_data,
                'id': str(len(dns_data["records"][record_type]) + 1),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            dns_data["records"][record_type].append(record)
            dns_data["last_updated"] = datetime.now().isoformat()
            
            with open(dns_path, 'w', encoding='utf-8') as f:
                json.dump(dns_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding DNS record: {str(e)}")
            return False

    def update_dns_record(self, domain_name: str, record_type: str, record_id: str, record_data: Dict) -> bool:
        """Update an existing DNS record."""
        try:
            domain_path = self.workspace_root / domain_name
            dns_path = domain_path / "content" / "records" / "dns.json"
            
            if not dns_path.exists():
                return False
            
            with open(dns_path, 'r', encoding='utf-8') as f:
                dns_data = json.load(f)
            
            if record_type not in dns_data["records"]:
                return False
            
            # Find and update record
            for record in dns_data["records"][record_type]:
                if record['id'] == record_id:
                    record.update(record_data)
                    record['updated_at'] = datetime.now().isoformat()
                    break
            
            dns_data["last_updated"] = datetime.now().isoformat()
            
            with open(dns_path, 'w', encoding='utf-8') as f:
                json.dump(dns_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating DNS record: {str(e)}")
            return False

    def delete_dns_record(self, domain_name: str, record_type: str, record_id: str) -> bool:
        """Delete a DNS record."""
        try:
            domain_path = self.workspace_root / domain_name
            dns_path = domain_path / "content" / "records" / "dns.json"
            
            if not dns_path.exists():
                return False
            
            with open(dns_path, 'r', encoding='utf-8') as f:
                dns_data = json.load(f)
            
            if record_type not in dns_data["records"]:
                return False
            
            # Remove record
            dns_data["records"][record_type] = [
                r for r in dns_data["records"][record_type] 
                if r['id'] != record_id
            ]
            
            dns_data["last_updated"] = datetime.now().isoformat()
            
            with open(dns_path, 'w', encoding='utf-8') as f:
                json.dump(dns_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error deleting DNS record: {str(e)}")
            return False

    def sync_dns_records(self, domain_name: str) -> bool:
        """Sync DNS records between Namecheap and local storage."""
        try:
            if not self.namecheap_api:
                raise Exception("Namecheap API not configured")
            
            # Get records from Namecheap
            namecheap_records = self.namecheap_api.get_dns_records(domain_name)
            
            # Get local records
            local_records = self.get_dns_records(domain_name)
            
            # Update local storage with Namecheap records
            dns_path = self.workspace_root / domain_name / "content" / "records" / "dns.json"
            dns_data = {
                "records": {
                    "A": [],
                    "CNAME": [],
                    "MX": [],
                    "TXT": [],
                    "NS": []
                },
                "last_updated": datetime.now().isoformat()
            }
            
            for record in namecheap_records:
                record_type = record['type']
                if record_type in dns_data["records"]:
                    dns_data["records"][record_type].append({
                        'id': record['host_id'],
                        'name': record['name'],
                        'value': record['address'],
                        'ttl': int(record['ttl']),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    })
            
            with open(dns_path, 'w', encoding='utf-8') as f:
                json.dump(dns_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error syncing DNS records: {str(e)}")
            return False

    def push_dns_records(self, domain_name: str) -> bool:
        """Push local DNS records to Namecheap."""
        try:
            if not self.namecheap_api:
                raise Exception("Namecheap API not configured")
            
            # Get local records
            dns_path = self.workspace_root / domain_name / "content" / "records" / "dns.json"
            if not dns_path.exists():
                return False
            
            with open(dns_path, 'r', encoding='utf-8') as f:
                dns_data = json.load(f)
            
            # Push each record to Namecheap
            for record_type, records in dns_data["records"].items():
                for record in records:
                    if 'id' in record:  # Update existing record
                        self.namecheap_api.update_dns_record(
                            domain=domain_name,
                            host_id=record['id'],
                            record_type=record_type,
                            name=record['name'],
                            address=record['value'],
                            ttl=record['ttl']
                        )
                    else:  # Add new record
                        self.namecheap_api.add_dns_record(
                            domain=domain_name,
                            record_type=record_type,
                            name=record['name'],
                            address=record['value'],
                            ttl=record['ttl']
                        )
            
            return True
        except Exception as e:
            print(f"Error pushing DNS records: {str(e)}")
            return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python domain_manager.py <command> [options]")
        print("Commands:")
        print("  create <domain_name> - Create a new domain with template structure")
        print("  update <domain_name> - Update domain context")
        print("  delete <domain_name> - Delete a domain")
        print("  list - List all domains")
        return

    manager = DomainManager()
    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) != 3:
            print("Usage: python domain_manager.py create <domain_name>")
            return
        domain_name = sys.argv[2]
        if manager.create_domain_template(domain_name):
            print(f"Successfully created template for {domain_name}")
        else:
            print(f"Failed to create template for {domain_name}")
    elif command == "update":
        if len(sys.argv) != 3:
            print("Usage: python domain_manager.py update <domain_name>")
            return
        domain_name = sys.argv[2]
        if manager.update_context(domain_name, sys.argv[3]):
            print(f"Successfully updated context for {domain_name}")
        else:
            print(f"Failed to update context for {domain_name}")
    elif command == "delete":
        if len(sys.argv) != 3:
            print("Usage: python domain_manager.py delete <domain_name>")
            return
        domain_name = sys.argv[2]
        if manager.delete_domain(domain_name):
            print(f"Successfully deleted {domain_name}")
        else:
            print(f"Failed to delete {domain_name}")
    elif command == "list":
        domains = manager.list_domains()
        if domains:
            print("Available domains:")
            for domain in domains:
                print(f"- {domain}")
        else:
            print("No domains found")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main() 