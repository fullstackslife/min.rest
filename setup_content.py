import os
import shutil
from pathlib import Path
import requests
from datetime import datetime
from PIL import Image, ImageDraw

# Site-specific content and image configurations
SITE_CONTENT = {
    'TouchedByChanelsCleaning.com': {
        'services': [
            {
                'title': 'Residential Cleaning',
                'description': 'Professional cleaning services for your home, including deep cleaning, regular maintenance, and special requests.',
                'image': 'residential-cleaning.jpg'
            },
            {
                'title': 'Commercial Cleaning',
                'description': 'Keep your business space clean and professional with our commercial cleaning services.',
                'image': 'commercial-cleaning.jpg'
            },
            {
                'title': 'Specialty Cleaning',
                'description': 'Carpet cleaning, window washing, and other specialty services to meet your specific needs.',
                'image': 'specialty-cleaning.jpg'
            }
        ],
        'hero_image': 'cleaning-hero.jpg'
    },
    'NewAgeWeb.it.com': {
        'services': [
            {
                'title': 'Web Development',
                'description': 'Custom web development solutions using the latest technologies and best practices.',
                'image': 'web-development.jpg'
            },
            {
                'title': 'Digital Marketing',
                'description': 'Comprehensive digital marketing strategies to grow your online presence.',
                'image': 'digital-marketing.jpg'
            },
            {
                'title': 'UI/UX Design',
                'description': 'Beautiful and intuitive user interfaces designed for optimal user experience.',
                'image': 'ui-design.jpg'
            }
        ],
        'hero_image': 'web-hero.jpg'
    },
    'FullStacks.live': {
        'services': [
            {
                'title': 'Live Coding Sessions',
                'description': 'Interactive live coding sessions covering various programming topics and technologies.',
                'image': 'live-coding.jpg'
            },
            {
                'title': 'Tutorial Videos',
                'description': 'Comprehensive video tutorials for learning full-stack development.',
                'image': 'tutorials.jpg'
            },
            {
                'title': 'Community Support',
                'description': 'Join our community of developers and get support for your coding journey.',
                'image': 'community.jpg'
            }
        ],
        'hero_image': 'coding-hero.jpg'
    },
    'FullStacks.life': {
        'services': [
            {
                'title': 'Development Resources',
                'description': 'Curated collection of resources for full-stack developers.',
                'image': 'resources.jpg'
            },
            {
                'title': 'Career Guidance',
                'description': 'Expert advice and guidance for advancing your development career.',
                'image': 'career.jpg'
            },
            {
                'title': 'Project Templates',
                'description': 'Ready-to-use templates for various full-stack projects.',
                'image': 'templates.jpg'
            }
        ],
        'hero_image': 'developer-hero.jpg'
    },
    'ForeverWingsLLC.com': {
        'services': [
            {
                'title': 'Aviation Consulting',
                'description': 'Expert consulting services for aviation businesses and professionals.',
                'image': 'aviation-consulting.jpg'
            },
            {
                'title': 'Flight Training',
                'description': 'Comprehensive flight training programs for aspiring pilots.',
                'image': 'flight-training.jpg'
            },
            {
                'title': 'Aircraft Management',
                'description': 'Professional aircraft management services for owners and operators.',
                'image': 'aircraft-management.jpg'
            }
        ],
        'hero_image': 'aviation-hero.jpg'
    },
    'C-Suite.xyz': {
        'services': [
            {
                'title': 'Executive Coaching',
                'description': 'One-on-one coaching for C-suite executives and business leaders.',
                'image': 'executive-coaching.jpg'
            },
            {
                'title': 'Leadership Development',
                'description': 'Programs to develop and enhance leadership skills at all levels.',
                'image': 'leadership.jpg'
            },
            {
                'title': 'Strategic Planning',
                'description': 'Expert guidance in developing and implementing business strategies.',
                'image': 'strategic-planning.jpg'
            }
        ],
        'hero_image': 'executive-hero.jpg'
    },
    'BucketGoats.com': {
        'services': [
            {
                'title': 'Business Solutions',
                'description': 'Innovative solutions to help your business grow and succeed.',
                'image': 'business-solutions.jpg'
            },
            {
                'title': 'Digital Transformation',
                'description': 'Guide your business through digital transformation with our expertise.',
                'image': 'digital-transformation.jpg'
            },
            {
                'title': 'Process Optimization',
                'description': 'Streamline your business processes for maximum efficiency.',
                'image': 'process-optimization.jpg'
            }
        ],
        'hero_image': 'business-hero.jpg'
    },
    'BellaAmour.me': {
        'services': [
            {
                'title': 'Beauty Services',
                'description': 'Comprehensive beauty services to enhance your natural beauty.',
                'image': 'beauty-services.jpg'
            },
            {
                'title': 'Wellness Programs',
                'description': 'Holistic wellness programs for mind, body, and spirit.',
                'image': 'wellness.jpg'
            },
            {
                'title': 'Spa Treatments',
                'description': 'Relaxing and rejuvenating spa treatments for ultimate self-care.',
                'image': 'spa-treatments.jpg'
            }
        ],
        'hero_image': 'beauty-hero.jpg'
    }
}

def download_image(url, path):
    """Download an image from a URL and save it to the specified path."""
    try:
        # Use Picsum Photos instead of Unsplash for more reliable image downloads
        image_id = hash(path) % 1000  # Generate a consistent but unique ID for each image
        image_url = f"https://picsum.photos/id/{image_id}/800/600"
        
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        print(f"Error downloading image: {e}")
        # Create a placeholder image
        img = Image.new('RGB', (800, 600), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((400, 300), "Placeholder", fill=(255, 255, 255))
        img.save(path)

def setup_images(repo_path, site_config):
    """Set up images for a site."""
    images_dir = os.path.join(repo_path, 'assets/images')
    os.makedirs(images_dir, exist_ok=True)
    
    # Download hero image
    hero_image_path = os.path.join(images_dir, site_config['hero_image'])
    if not os.path.exists(hero_image_path):
        # Use placeholder images for now
        download_image(f"https://source.unsplash.com/1600x900/?{site_config['hero_image'].split('-')[0]}", hero_image_path)
    
    # Download service images
    for service in site_config['services']:
        image_path = os.path.join(images_dir, service['image'])
        if not os.path.exists(image_path):
            download_image(f"https://source.unsplash.com/800x600/?{service['image'].split('.')[0]}", image_path)

def update_index_html(repo_path, site_config):
    """Update the index.html file with site-specific content."""
    with open(os.path.join(repo_path, 'index.html'), 'r') as f:
        content = f.read()
    
    # Update services section
    services_html = ''
    for service in site_config['services']:
        services_html += f"""
                <div class="feature">
                    <img src="assets/images/{service['image']}" alt="{service['title']}">
                    <h3>{service['title']}</h3>
                    <p>{service['description']}</p>
                </div>
        """
    
    content = content.replace('<!-- SERVICES_PLACEHOLDER -->', services_html)
    
    # Update hero image
    content = content.replace('hero-bg.jpg', site_config['hero_image'])
    
    with open(os.path.join(repo_path, 'index.html'), 'w') as f:
        f.write(content)

def main():
    for repo, config in SITE_CONTENT.items():
        print(f"Setting up content for {repo}...")
        repo_path = repo
        
        # Set up images
        setup_images(repo_path, config)
        
        # Update index.html
        update_index_html(repo_path, config)
        
        print(f"Completed content setup for {repo}")

if __name__ == "__main__":
    main() 