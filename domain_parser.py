import json
import re
import os
from pathlib import Path

def parse_domain_section(content, domain_name):
    """Parse a domain section from the markdown content."""
    # Extract theme, voice, and use case
    theme_match = re.search(r'Theme: (.*?)\n', content)
    voice_match = re.search(r'Voice: (.*?)\n', content)
    use_case_match = re.search(r'Use Case: (.*?)\n', content)
    
    # Extract homepage sections
    homepage = {}
    
    # Extract hero section
    hero_match = re.search(r'Hero:.*?\n\s*_"(.*?)"_', content, re.DOTALL)
    if hero_match:
        hero_text = hero_match.group(1).strip()
        if '\n' in hero_text:
            # Split into main and sub if there are multiple lines
            hero_lines = [line.strip() for line in hero_text.split('\n') if line.strip()]
            homepage['hero'] = {
                'main': hero_lines[0],
                'sub': hero_lines[1] if len(hero_lines) > 1 else None
            }
        else:
            homepage['hero'] = hero_text
    
    # Extract about preview if exists
    about_match = re.search(r'About Preview:.*?\n\s*_"(.*?)"_', content, re.DOTALL)
    if about_match:
        homepage['about_preview'] = about_match.group(1).strip()
    
    # Extract email capture
    email_match = re.search(r'Email CTA:.*?\n\s*_"(.*?)"_', content, re.DOTALL)
    form_placement_match = re.search(r'✅ (.*?)\n', content)
    if email_match:
        homepage['email_capture'] = {
            'text': email_match.group(1).strip(),
            'form_placement': form_placement_match.group(1).strip() if form_placement_match else None
        }
    
    # Extract other sections based on domain type
    if 'adventures' in content.lower():
        adventures_match = re.findall(r'- "(.*?)"', content)
        if adventures_match:
            homepage['adventures'] = adventures_match
    
    if 'offerings' in content.lower():
        offerings_match = re.findall(r'- (.*?)\n', content)
        if offerings_match:
            homepage['offerings'] = [o.strip() for o in offerings_match if o.strip()]
    
    return {
        'domain': domain_name,
        'theme': theme_match.group(1).strip() if theme_match else None,
        'voice': voice_match.group(1).strip() if voice_match else None,
        'use_case': use_case_match.group(1).strip() if use_case_match else None,
        'homepage': homepage
    }

def process_domain_list(file_path):
    """Process the domain list markdown file and generate context files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into domain sections
    domain_sections = re.split(r'### [^\n]+\n', content)[1:]  # Skip the header section
    
    # Create context directory if it doesn't exist
    context_dir = Path('context')
    context_dir.mkdir(exist_ok=True)
    
    # Clean up any existing files in the context directory
    for file in context_dir.glob('*'):
        if file.is_file():
            file.unlink()
    
    for section in domain_sections:
        # Extract domain name from the section
        domain_match = re.search(r'(\*\*(\d+\.\s+)?([^\*]+)\*\*)', section)
        if not domain_match:
            continue
            
        domain_name = domain_match.group(3).strip()
        if not domain_name:
            continue
            
        # Clean the domain name to ensure it's a valid filename
        domain_name = re.sub(r'[^\w\.-]', '_', domain_name)
        
        # Parse the domain section
        domain_data = parse_domain_section(section, domain_name)
        
        # Write to JSON file
        output_file = context_dir / f"{domain_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(domain_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    process_domain_list('domain_list.md') 