import os
import re
import shutil
from datetime import datetime
from pathlib import Path

# HTML Templates
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {domain}</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <!-- Brevo Form Styles -->
    <style>
        @font-face {{
            font-display: block;
            font-family: Roboto;
            src: url(https://assets.brevo.com/font/Roboto/Latin/normal/normal/7529907e9eaf8ebb5220c5f9850e3811.woff2) format("woff2"), url(https://assets.brevo.com/font/Roboto/Latin/normal/normal/25c678feafdc175a70922a116c9be3e7.woff) format("woff")
        }}

        @font-face {{
            font-display: fallback;
            font-family: Roboto;
            font-weight: 600;
            src: url(https://assets.brevo.com/font/Roboto/Latin/medium/normal/6e9caeeafb1f3491be3e32744bc30440.woff2) format("woff2"), url(https://assets.brevo.com/font/Roboto/Latin/medium/normal/71501f0d8d5aa95960f6475d5487d4c2.woff) format("woff")
        }}

        @font-face {{
            font-display: fallback;
            font-family: Roboto;
            font-weight: 700;
            src: url(https://assets.brevo.com/font/Roboto/Latin/bold/normal/3ef7cf158f310cf752d5ad08cd0e7e60.woff2) format("woff2"), url(https://assets.brevo.com/font/Roboto/Latin/bold/normal/ece3a1d82f18b60bcce0211725c476aa.woff) format("woff")
        }}

        #sib-container input:-ms-input-placeholder {{
            text-align: left;
            font-family: Helvetica, sans-serif;
            color: #c0ccda;
        }}

        #sib-container input::placeholder {{
            text-align: left;
            font-family: Helvetica, sans-serif;
            color: #c0ccda;
        }}

        #sib-container textarea::placeholder {{
            text-align: left;
            font-family: Helvetica, sans-serif;
            color: #c0ccda;
        }}

        #sib-container a {{
            text-decoration: underline;
            color: #2BB2FC;
        }}
    </style>
    <link rel="stylesheet" href="https://sibforms.com/forms/end-form/build/sib-styles.css">
    <!-- HubSpot Tracking Code -->
    <script type="text/javascript" id="hs-script-loader" async defer src="//js.hs-scripts.com/{{HUBSPOT_PORTAL_ID}}.js"></script>
    <!-- Brevo Chat Widget -->
    <script>
        (function(d, w, c) {{
            w.BrevoConversationsID = '{{BREVO_CONVERSATIONS_ID}}';
            w[c] = w[c] || function() {{
                (w[c].q = w[c].q || []).push(arguments);
            }};
            var s = d.createElement('script');
            s.async = true;
            s.src = 'https://conversations-widget.brevo.com/brevo-conversations.js';
            if (d.head) d.head.appendChild(s);
        }})(document, window, 'BrevoConversations');
    </script>
</head>
<body>
    <header>
        <nav>
            <div class="logo">
                <img src="assets/logo.png" alt="{domain} Logo">
            </div>
            <ul>
                <li><a href="index.html">Home</a></li>
                <li><a href="about.html">About</a></li>
                <li><a href="services.html">Services</a></li>
                <li><a href="contact.html">Contact</a></li>
            </ul>
        </nav>
    </header>
    <main>
        {content}
    </main>
    <footer>
        <p>&copy; {year} {domain}. All rights reserved.</p>
    </footer>
    <!-- Brevo Form Scripts -->
    <script>
        window.REQUIRED_CODE_ERROR_MESSAGE = 'Please choose a country code';
        window.LOCALE = 'en';
        window.EMAIL_INVALID_MESSAGE = window.SMS_INVALID_MESSAGE = "The information provided is invalid. Please review the field format and try again.";
        window.REQUIRED_ERROR_MESSAGE = "This field cannot be left blank. ";
        window.GENERIC_INVALID_MESSAGE = "The information provided is invalid. Please review the field format and try again.";
        window.translation = {{
            common: {{
                selectedList: '{{quantity}} list selected',
                selectedLists: '{{quantity}} lists selected',
                selectedOption: '{{quantity}} selected',
                selectedOptions: '{{quantity}} selected',
            }}
        }};
        var AUTOHIDE = Boolean(0);
    </script>
    <script defer src="https://sibforms.com/forms/end-form/build/main.js"></script>
</body>
</html>
"""

def parse_context(file_path):
    """Parse a context file for domain names and descriptions."""
    domains = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all domain entries (e.g., "1. domain.com")
        domain_pattern = r'\d+\.\s+([a-zA-Z0-9.-]+)'
        domain_matches = re.finditer(domain_pattern, content)
        
        for match in domain_matches:
            try:
                domain = match.group(1)
                # Find the description after the domain
                start_idx = match.end()
                next_domain = re.search(r'\d+\.\s+[a-zA-Z0-9.-]+', content[start_idx:])
                end_idx = start_idx + next_domain.start() if next_domain else len(content)
                
                description = content[start_idx:end_idx].strip()
                if domain and isinstance(domain, str):
                    domain_info = {
                        'name': domain,
                        'description': description if description else 'No description available'
                    }
                    domains.append(domain_info)
                    log_action(f"Found domain: {domain}")
            except Exception as e:
                log_action(f"Error processing domain match: {str(e)}")
                continue
        
        return domains
    except Exception as e:
        log_action(f"Error parsing context file: {str(e)}")
        return []

def generate_project_folder(domain_info, original_file_path):
    """Generate the project folder structure for a domain."""
    domain = domain_info['name']
    description = domain_info['description']
    
    log_action(f"Starting to populate folder for: {domain}")
    
    # Create main domain folder
    domain_path = Path(domain)
    domain_path.mkdir(exist_ok=True)
    
    # Create assets directory and subdirectories
    assets_dir = domain_path / 'assets'
    assets_dir.mkdir(exist_ok=True)
    css_dir = assets_dir / 'css'
    css_dir.mkdir(exist_ok=True)
    
    # Create CSS file
    css_path = css_dir / 'style.css'
    css_content = """/* Theme Variables */
:root {
    /* Primary Colors */
    --primary-color: #2BB2FC;
    --primary-dark: #1a9de8;
    --primary-light: #e6f5ff;
    
    /* Secondary Colors */
    --secondary-color: #3C4858;
    --secondary-dark: #2C3440;
    --secondary-light: #EFF2F7;
    
    /* Accent Colors */
    --accent-color: #13ce66;
    --accent-dark: #0f9f4f;
    --accent-light: #e7faf0;
    
    /* Neutral Colors */
    --text-primary: #333;
    --text-secondary: #666;
    --text-light: #8390A4;
    --background: #f5f5f5;
    --surface: #fff;
    
    /* Spacing */
    --spacing-xs: 0.5rem;
    --spacing-sm: 1rem;
    --spacing-md: 2rem;
    --spacing-lg: 3rem;
    
    /* Border Radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    
    /* Shadows */
    --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
    --shadow-lg: 0 8px 16px rgba(0,0,0,0.1);
    
    /* Transitions */
    --transition-fast: 0.2s ease;
    --transition-normal: 0.3s ease;
    --transition-slow: 0.5s ease;
}

/* Base Styles */
body {
    font-family: 'Roboto', Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    background-color: var(--background);
    color: var(--text-primary);
}

/* Header & Navigation */
header {
    background: var(--secondary-color);
    color: var(--surface);
    padding: var(--spacing-sm);
    box-shadow: var(--shadow-sm);
    position: sticky;
    top: 0;
    z-index: 1000;
}

nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
}

.logo img {
    height: 50px;
    transition: transform var(--transition-normal);
}

.logo img:hover {
    transform: scale(1.05);
}

nav ul {
    list-style: none;
    display: flex;
    margin: 0;
    padding: 0;
    gap: var(--spacing-md);
}

nav ul li a {
    color: var(--surface);
    text-decoration: none;
    font-weight: 500;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
}

nav ul li a:hover {
    color: var(--primary-color);
    background-color: rgba(255, 255, 255, 0.1);
}

/* Main Content */
main {
    padding: var(--spacing-md);
    max-width: 1200px;
    margin: 0 auto;
    min-height: calc(100vh - 200px);
}

/* Form Container */
.sib-form {
    max-width: 600px;
    margin: var(--spacing-lg) auto;
    padding: var(--spacing-md);
    background-color: var(--surface);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    transition: transform var(--transition-normal);
}

.sib-form:hover {
    transform: translateY(-2px);
}

#sib-container {
    background-color: transparent;
    padding: 0;
    border: none;
    box-shadow: none;
}

/* Form Elements */
.sib-form-block p {
    margin: 0;
    padding: var(--spacing-xs) 0;
    color: var(--text-primary);
}

.entry__field input {
    width: 100%;
    padding: var(--spacing-sm);
    margin: var(--spacing-xs) 0;
    border: 1px solid var(--secondary-light);
    border-radius: var(--radius-sm);
    font-size: 16px;
    transition: all var(--transition-fast);
    background-color: var(--surface);
}

.entry__field input:focus {
    border-color: var(--primary-color);
    outline: none;
    box-shadow: 0 0 0 2px var(--primary-light);
}

.entry__label {
    color: var(--text-primary);
    font-size: 16px;
    margin-bottom: var(--spacing-xs);
    display: block;
    font-weight: 500;
}

.entry__specification {
    color: var(--text-light);
    font-size: 14px;
    margin-top: var(--spacing-xs);
}

/* Buttons */
.sib-form-block__button {
    width: 100%;
    padding: var(--spacing-sm);
    margin-top: var(--spacing-md);
    background-color: var(--primary-color);
    color: var(--surface);
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-weight: bold;
    font-size: 16px;
    transition: all var(--transition-normal);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-xs);
}

.sib-form-block__button:hover {
    background-color: var(--primary-dark);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
}

.sib-form-block__button:active {
    transform: translateY(0);
}

/* Form Messages */
.sib-form-message-panel {
    margin: var(--spacing-sm) 0;
    padding: var(--spacing-sm);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
}

#error-message {
    background-color: #ffeded;
    border: 1px solid #ff4949;
    color: #661d1d;
}

#success-message {
    background-color: var(--accent-light);
    border: 1px solid var(--accent-color);
    color: var(--accent-dark);
}

.sib-icon {
    width: 24px;
    height: 24px;
    flex-shrink: 0;
}

/* Form Title and Description */
.sib-form-block:first-child p {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: var(--spacing-sm);
}

.sib-text-form-block p {
    font-size: 16px;
    color: var(--text-secondary);
    line-height: 1.5;
}

/* Footer */
footer {
    background: var(--secondary-color);
    color: var(--surface);
    text-align: center;
    padding: var(--spacing-sm);
    box-shadow: var(--shadow-sm);
    position: relative;
    z-index: 100;
}

/* Responsive Design */
@media (max-width: 768px) {
    :root {
        --spacing-md: 1.5rem;
        --spacing-lg: 2rem;
    }

    nav {
        flex-direction: column;
        text-align: center;
        gap: var(--spacing-sm);
    }

    nav ul {
        flex-direction: column;
        gap: var(--spacing-xs);
    }

    .sib-form {
        margin: var(--spacing-sm);
        padding: var(--spacing-sm);
    }

    .sib-form-block:first-child p {
        font-size: 24px;
    }
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.sib-form {
    animation: fadeIn 0.5s ease-out;
}

/* Loading States */
.sib-form-block__button-with-loader {
    position: relative;
}

.sib-form-block__button-with-loader .icon {
    animation: spin 1s linear infinite;
    opacity: 0;
    transition: opacity var(--transition-fast);
}

.sib-form-block__button-with-loader.loading .icon {
    opacity: 1;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--background);
}

::-webkit-scrollbar-thumb {
    background: var(--primary-color);
    border-radius: var(--radius-sm);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--primary-dark);
}
"""
    css_path.write_text(css_content)
    
    # Create CNAME file
    cname_path = domain_path / 'CNAME'
    cname_path.write_text(domain)
    
    # Create HTML pages
    pages = {
        'index.html': f"""
        <h1>Welcome to {domain}</h1>
        <p>{description}</p>
        <section class="services">
            <h2>Our Services</h2>
            <p>Discover our range of professional services designed to meet your needs.</p>
        </section>
        """,
        'about.html': f"""
        <h1>About {domain}</h1>
        <p>Learn more about our company and our mission.</p>
        """,
        'services.html': f"""
        <h1>Our Services</h1>
        <p>Explore our comprehensive range of services designed to help you succeed.</p>
        """,
        'contact.html': f"""
        <h1>Contact Us</h1>
        <div class="sib-form">
            <div id="sib-form-container" class="sib-form-container">
                <div id="error-message" class="sib-form-message-panel" style="font-size:16px; text-align:left; font-family:Helvetica, sans-serif; color:#661d1d; background-color:#ffeded; border-radius:3px; border-color:#ff4949;max-width:540px;">
                    <div class="sib-form-message-panel__text sib-form-message-panel__text--center">
                        <svg viewBox="0 0 512 512" class="sib-icon sib-notification__icon">
                            <path d="M256 40c118.621 0 216 96.075 216 216 0 119.291-96.61 216-216 216-119.244 0-216-96.562-216-216 0-119.203 96.602-216 216-216m0-32C119.043 8 8 119.083 8 256c0 136.997 111.043 248 248 248s248-111.003 248-248C504 119.083 392.957 8 256 8zm-11.49 120h22.979c6.823 0 12.274 5.682 11.99 12.5l-7 168c-.268 6.428-5.556 11.5-11.99 11.5h-8.979c-6.433 0-11.722-5.073-11.99-11.5l-7-168c-.283-6.818 5.167-12.5 11.99-12.5zM256 340c-15.464 0-28 12.536-28 28s12.536 28 28 28 28-12.536 28-28-12.536-28-28-28z" />
                        </svg>
                        <span class="sib-form-message-panel__inner-text">
                            Your subscription could not be saved. Please try again.
                        </span>
                    </div>
                </div>
                <div id="success-message" class="sib-form-message-panel" style="font-size:16px; text-align:left; font-family:Helvetica, sans-serif; color:#085229; background-color:#e7faf0; border-radius:3px; border-color:#13ce66;max-width:540px;">
                    <div class="sib-form-message-panel__text sib-form-message-panel__text--center">
                        <svg viewBox="0 0 512 512" class="sib-icon sib-notification__icon">
                            <path d="M256 8C119.033 8 8 119.033 8 256s111.033 248 248 248 248-111.033 248-248C504 119.083 392.957 8 256 8zm0 464c-118.664 0-216-96.055-216-216 0-118.663 96.055-216 216-216 118.664 0 216 96.055 216 216 0 118.663-96.055 216-216 216zm141.63-274.961L217.15 376.071c-4.705 4.667-12.303 4.637-16.97-.068l-85.878-86.572c-4.667-4.705-4.637-12.303.068-16.97l8.52-8.451c4.705-4.667 12.303-4.637 16.97.068l68.976 69.533 163.441-162.13c4.705-4.667 12.303-4.637 16.97.068l8.451 8.52c4.668 4.705 4.637 12.303-.068 16.97z" />
                        </svg>
                        <span class="sib-form-message-panel__inner-text">
                            Your subscription has been successful.
                        </span>
                    </div>
                </div>
                <div id="sib-container" class="sib-container--large sib-container--vertical">
                    <form id="sib-form" method="POST" action="https://sibforms.com/serve/MUIFAIjEJzLnT_uO9YkBt64DY7XTJFCmWXgiS8Au-w6FONS1_FeAb3M5c1fZRJy-J8aPLxdUd6WQ8ykOk-Gj_yJbdK_GuZgMR1gZfuTAwCWKncX5FUX8_m5mesyzxIagL5-VCfJMknVIowif9Mr4aUZVXiIC09LLsKgDwfPpJ7SgAqc5pJsReHjSCCXJqeCAPxHz_X26iaN-8_T8" data-type="subscription">
                        <div style="padding: 8px 0;">
                            <div class="sib-form-block" style="font-size:32px; text-align:left; font-weight:700; font-family:Helvetica, sans-serif; color:#3C4858; background-color:transparent; text-align:left">
                                <p>Subscribe for updates!</p>
                            </div>
                        </div>
                        <div style="padding: 8px 0;">
                            <div class="sib-form-block" style="font-size:16px; text-align:left; font-family:Helvetica, sans-serif; color:#3C4858; background-color:transparent; text-align:left">
                                <div class="sib-text-form-block">
                                    <p>Subscribe to our newsletter and stay updated.</p>
                                </div>
                            </div>
                        </div>
                        <div style="padding: 8px 0;">
                            <div class="sib-input sib-form-block">
                                <div class="form__entry entry_block">
                                    <div class="form__label-row ">
                                        <label class="entry__label" style="font-weight: 700; text-align:left; font-size:16px; text-align:left; font-weight:700; font-family:Helvetica, sans-serif; color:#3c4858;" for="EMAIL" data-required="*">Enter your email address to subscribe</label>
                                        <div class="entry__field">
                                            <input class="input " type="text" id="EMAIL" name="EMAIL" autocomplete="off" placeholder="EMAIL" data-required="true" required />
                                        </div>
                                    </div>
                                    <label class="entry__error entry__error--primary" style="font-size:16px; text-align:left; font-family:Helvetica, sans-serif; color:#661d1d; background-color:#ffeded; border-radius:3px; border-color:#ff4949;">
                                    </label>
                                    <label class="entry__specification" style="font-size:12px; text-align:left; font-family:Helvetica, sans-serif; color:#8390A4; text-align:left">
                                        Provide your email address to subscribe. For e.g abc@xyz.com
                                    </label>
                                </div>
                            </div>
                        </div>
                        <div style="padding: 8px 0;">
                            <div class="sib-form-block" style="text-align: left">
                                <button class="sib-form-block__button sib-form-block__button-with-loader" style="font-size:16px; text-align:left; font-weight:700; font-family:Helvetica, sans-serif; color:#FFFFFF; background-color:#3E4857; border-radius:3px; border-width:0px;" form="sib-form" type="submit">
                                    <svg class="icon clickable__icon progress-indicator__icon sib-hide-loader-icon" viewBox="0 0 512 512">
                                        <path d="M460.116 373.846l-20.823-12.022c-5.541-3.199-7.54-10.159-4.663-15.874 30.137-59.886 28.343-131.652-5.386-189.946-33.641-58.394-94.896-95.833-161.827-99.676C261.028 55.961 256 50.751 256 44.352V20.309c0-6.904 5.808-12.337 12.703-11.982 83.556 4.306 160.163 50.864 202.11 123.677 42.063 72.696 44.079 162.316 6.031 236.832-3.14 6.148-10.75 8.461-16.728 5.01z" />
                                    </svg>
                                    SUBSCRIBE
                                </button>
                            </div>
                        </div>
                        <input type="text" name="email_address_check" value="" class="input--hidden">
                        <input type="hidden" name="locale" value="en">
                    </form>
                </div>
            </div>
        </div>
        """
    }
    
    for page_name, content in pages.items():
        page_path = domain_path / page_name
        page_content = HTML_TEMPLATE.format(
            title=page_name.replace('.html', '').title(),
            domain=domain,
            content=content,
            year=datetime.now().year
        )
        page_path.write_text(page_content)
        log_action(f"Created/Updated {page_name} for {domain}")
    
    # Initialize git repository
    if not (domain_path / '.git').exists():
        os.system(f'cd {domain_path} && git init')
        log_action(f"Initialized git repository for {domain}")
    
    # Create .gitignore with enhanced security
    gitignore_path = domain_path / '.gitignore'
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

# Dependencies
node_modules/

# Environment and Configuration
.env
*.env
.env.*
config.json
secrets.json
credentials.json
*.key
*.pem
*.cert
*.crt

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build output
dist/
build/
out/
"""
    gitignore_path.write_text(gitignore_content)
    
    # Create configuration template file
    config_template_path = domain_path / 'config.template.json'
    config_template_content = """{
    "hubspot": {
        "portalId": "YOUR_HUBSPOT_PORTAL_ID",
        "formId": "YOUR_HUBSPOT_FORM_ID"
    },
    "brevo": {
        "conversationsId": "YOUR_BREVO_CONVERSATIONS_ID"
    }
}
"""
    config_template_path.write_text(config_template_content)
    
    # Create README with setup instructions
    readme_path = domain_path / 'README.md'
    readme_content = f"""# {domain} Website

## Setup Instructions

1. Copy `config.template.json` to `config.json`:
   ```bash
   cp config.template.json config.json
   ```

2. Update `config.json` with your actual credentials:
   - HubSpot Portal ID
   - HubSpot Form ID
   - Brevo Conversations ID

3. Never commit `config.json` to version control. It's already in `.gitignore`.

4. For GitHub Pages deployment:
   - Push your code to GitHub
   - Enable GitHub Pages in repository settings
   - Set up your custom domain in GitHub Pages settings

## Integration Notes

- HubSpot forms handle all form submissions
- Brevo chat widget provides live chat support
- No backend required - everything works on GitHub Pages
- HubSpot and Brevo can be synced through their respective platforms

## Security Notes

- Keep your API keys and credentials secure
- Use environment variables in production if needed
- Regularly rotate your API keys
- Monitor your API usage for suspicious activity
"""
    readme_path.write_text(readme_content)
    
    log_action(f"Successfully populated project folder for {domain}")

def archive_context_file(file_path):
    """Archive a processed context file with version and date."""
    archive_dir = Path('archive')
    archive_dir.mkdir(exist_ok=True)
    
    filename = Path(file_path).name
    date_str = datetime.now().strftime('%Y%m%d')
    archive_name = f"{filename}_v1_{date_str}.md"
    archive_path = archive_dir / archive_name
    
    shutil.move(file_path, archive_path)
    log_action(f"Moved {file_path} to archive as {archive_path}")
    return archive_path

def log_action(message):
    """Log an action to the engine log file."""
    log_dir = Path('log')
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}\n"
    
    # Print to console for immediate feedback
    print(log_message.strip())
    
    with open(log_dir / 'engine.log', 'a', encoding='utf-8') as f:
        f.write(log_message)

def main():
    """Main function to process context files."""
    context_dir = Path('context')
    if not context_dir.exists():
        log_action("Error: context directory not found")
        return
    
    for file_path in context_dir.glob('*.md'):
        if file_path.name == 'website_engine.md':
            continue
            
        log_action(f"Processing {file_path}")
        domains = parse_context(file_path)
        
        if not domains:
            log_action(f"No domain data found in {file_path}")
            continue
            
        for domain_info in domains:
            log_action(f"Processing domain: {domain_info['name']}")
            generate_project_folder(domain_info, file_path)
        
        archive_context_file(file_path)

if __name__ == '__main__':
    main() 