import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime
import shutil
import re
from domain_manager import DomainManager
from engine import parse_context, generate_project_folder, log_action

class SiteGenerator:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.domain_manager = DomainManager(workspace_root)
        self.log_file = self.workspace_root / "log" / "generation.log"
        self.log_file.parent.mkdir(exist_ok=True)

    def log(self, message: str):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_message)
        print(log_message.strip())

    def get_undeployed_domains(self) -> List[str]:
        """Get list of domains that haven't been deployed yet."""
        try:
            with open("domain_list.md", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Find all domain entries
            domain_pattern = r'\d+\.\s+([a-zA-Z0-9.-]+)'
            all_domains = re.findall(domain_pattern, content)
            
            # Get already deployed domains
            deployed_domains = self.domain_manager.list_domains()
            
            # Return domains that haven't been deployed
            return [domain for domain in all_domains if domain not in deployed_domains]
        except Exception as e:
            self.log(f"Error getting undeployed domains: {str(e)}")
            return []

    def generate_site(self, domain: str, context_file: Optional[str] = None) -> bool:
        """Generate a complete website for a domain."""
        try:
            self.log(f"Starting generation for domain: {domain}")
            
            # Create domain structure
            if not self.domain_manager.create_domain(domain):
                self.log(f"Failed to create domain structure for {domain}")
                return False
            
            # Parse context if provided
            domain_info = {"name": domain, "description": ""}
            if context_file and os.path.exists(context_file):
                domains = parse_context(context_file)
                for d in domains:
                    if d["name"] == domain:
                        domain_info = d
                        break
            
            # Generate project folder with content
            generate_project_folder(domain_info, context_file if context_file else "")
            
            # Copy default assets if they exist
            default_assets = self.workspace_root / "static" / "default_assets"
            if default_assets.exists():
                target_assets = self.workspace_root / domain / "assets"
                shutil.copytree(default_assets, target_assets, dirs_exist_ok=True)
            
            self.log(f"Successfully generated site for {domain}")
            return True
            
        except Exception as e:
            self.log(f"Error generating site for {domain}: {str(e)}")
            return False

    def generate_all_undeployed(self, context_file: Optional[str] = None) -> Dict[str, bool]:
        """Generate all undeployed sites."""
        results = {}
        undeployed = self.get_undeployed_domains()
        
        if not undeployed:
            self.log("No undeployed domains found")
            return results
        
        self.log(f"Found {len(undeployed)} undeployed domains")
        
        for domain in undeployed:
            success = self.generate_site(domain, context_file)
            results[domain] = success
        
        return results

def main():
    if len(sys.argv) > 1:
        # Generate specific domain
        domain = sys.argv[1]
        context_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        generator = SiteGenerator()
        success = generator.generate_site(domain, context_file)
        sys.exit(0 if success else 1)
    else:
        # Generate all undeployed domains
        generator = SiteGenerator()
        results = generator.generate_all_undeployed()
        
        # Print summary
        print("\nGeneration Summary:")
        print("=" * 50)
        for domain, success in results.items():
            status = "✓ Success" if success else "✗ Failed"
            print(f"{domain}: {status}")
        
        total = len(results)
        successful = sum(1 for s in results.values() if s)
        print(f"\nTotal: {total}, Successful: {successful}, Failed: {total - successful}")

if __name__ == "__main__":
    main() 