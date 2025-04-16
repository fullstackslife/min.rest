import os
import re
from pathlib import Path

def extract_domain_context(domain_list_content):
    """Extract context for each domain from the domain list."""
    domains = {}
    current_domain = None
    current_content = []
    
    # Split content into lines and process
    lines = domain_list_content.split('\n')
    for line in lines:
        # Check for domain headers (they follow the pattern ### 💕 **1. Domain.com**)
        domain_match = re.match(r'###\s+[^\s]+\s+\*\*(\d+\.\s+([^\*]+))\*\*', line)
        if domain_match:
            if current_domain and current_content:
                domains[current_domain] = '\n'.join(current_content)
            current_domain = domain_match.group(2).strip()
            current_content = [line]
        elif current_domain:
            current_content.append(line)
    
    # Add the last domain
    if current_domain and current_content:
        domains[current_domain] = '\n'.join(current_content)
    
    return domains

def ensure_directory_structure(domain):
    """Ensure the content directory exists for a domain."""
    content_dir = Path(domain) / 'content'
    content_dir.mkdir(parents=True, exist_ok=True)
    return content_dir

def write_context_file(domain, content, content_dir):
    """Write the context to a file."""
    context_file = content_dir / 'context.md'
    with open(context_file, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    # Read the domain list
    with open('domain_list.md', 'r', encoding='utf-8') as f:
        domain_list_content = f.read()
    
    # Extract context for each domain
    domains = extract_domain_context(domain_list_content)
    
    # Process each domain
    for domain, content in domains.items():
        print(f"Processing {domain}...")
        content_dir = ensure_directory_structure(domain)
        write_context_file(domain, content, content_dir)
        print(f"✓ Created context file for {domain}")

if __name__ == "__main__":
    main() 