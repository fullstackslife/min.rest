from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from pathlib import Path
from engine import parse_context, generate_project_folder, archive_context_file, log_action
import threading
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log/dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Configuration
CONFIG = {
    'context_dir': 'context',
    'archive_dir': 'archive',
    'log_dir': 'log',
    'templates_dir': 'templates',
    'page_types': ['home', 'about', 'services', 'blog', 'contact', 'portfolio', 'pricing', 'faq'],
    'theme_options': ['default', 'modern', 'classic', 'minimal', 'corporate'],
    'engine_thread': None,
    'engine_running': False
}

def get_domains():
    """Get list of domains from context files."""
    try:
        domains = []
        context_dir = Path(CONFIG['context_dir'])
        if not context_dir.exists():
            logger.warning(f"Context directory {context_dir} does not exist")
            return domains
        
        for file_path in context_dir.glob('*.md'):
            if file_path.name == 'website_engine.md':
                continue
            try:
                parsed_domains = parse_context(str(file_path))
                # Ensure each domain has required properties
                for domain in parsed_domains:
                    if isinstance(domain, dict) and 'name' in domain:
                        domains.append({
                            'name': domain['name'],
                            'description': domain.get('description', '')
                        })
                logger.info(f"Successfully parsed {file_path}")
            except Exception as e:
                logger.error(f"Error parsing {file_path}: {str(e)}")
        
        logger.info(f"Found {len(domains)} domains")
        return domains
    except Exception as e:
        logger.error(f"Error getting domains: {str(e)}")
        return []

def get_logs():
    """Get recent logs."""
    try:
        log_file = Path(CONFIG['log_dir']) / 'engine.log'
        if not log_file.exists():
            logger.warning(f"Log file {log_file} does not exist")
            return []
        
        with open(log_file, 'r') as f:
            return f.readlines()[-100:]  # Last 100 lines
    except Exception as e:
        logger.error(f"Error reading logs: {str(e)}")
        return []

def get_file_structure(domain):
    """Get the file structure for a domain."""
    try:
        domain_path = Path(domain)
        if not domain_path.exists():
            logger.warning(f"Domain path {domain_path} does not exist")
            return []
        
        structure = []
        for path in domain_path.rglob('*'):
            try:
                if path.is_file():
                    structure.append({
                        'type': 'file',
                        'path': str(path.relative_to(domain_path)),
                        'size': path.stat().st_size,
                        'modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                    })
                elif path.is_dir():
                    structure.append({
                        'type': 'directory',
                        'path': str(path.relative_to(domain_path)),
                        'size': sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                    })
            except Exception as e:
                logger.warning(f"Error processing path {path}: {str(e)}")
                continue
        
        logger.info(f"Found {len(structure)} items in file structure for {domain}")
        return structure
    except Exception as e:
        logger.error(f"Error getting file structure for {domain}: {str(e)}")
        return []

@app.route('/')
def index():
    """Render the main dashboard."""
    try:
        domains = get_domains()
        logs = get_logs()
        logger.info(f"Rendering index with {len(domains)} domains and {len(logs)} log entries")
        return render_template('index.html', 
                             domains=domains, 
                             logs=logs,
                             page_types=CONFIG['page_types'],
                             theme_options=CONFIG['theme_options'])
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}", exc_info=True)  # Add full traceback
        return f"An error occurred: {str(e)}", 500  # Return the actual error message

@app.route('/api/run_engine', methods=['POST'])
def run_engine():
    """API endpoint to run the engine."""
    try:
        if CONFIG['engine_running']:
            return jsonify({'status': 'error', 'message': 'Engine is already running'}), 400

        def engine_worker():
            try:
                CONFIG['engine_running'] = True
                context_dir = Path(CONFIG['context_dir'])
                for file_path in context_dir.glob('*.md'):
                    if file_path.name == 'website_engine.md':
                        continue
                    domains = parse_context(str(file_path))
                    for domain_info in domains:
                        generate_project_folder(domain_info, str(file_path))
                    archive_context_file(str(file_path))
            except Exception as e:
                logger.error(f"Error in engine worker: {str(e)}")
            finally:
                CONFIG['engine_running'] = False

        CONFIG['engine_thread'] = threading.Thread(target=engine_worker)
        CONFIG['engine_thread'].start()
        
        return jsonify({'status': 'success', 'message': 'Engine started'})
    except Exception as e:
        logger.error(f"Error starting engine: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stop_engine', methods=['POST'])
def stop_engine():
    """API endpoint to stop the engine."""
    try:
        if not CONFIG['engine_running']:
            return jsonify({'status': 'error', 'message': 'Engine is not running'}), 400
        
        # Add logic to safely stop the engine
        CONFIG['engine_running'] = False
        return jsonify({'status': 'success', 'message': 'Engine stopped'})
    except Exception as e:
        logger.error(f"Error stopping engine: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/domains')
def get_domains_api():
    """API endpoint to get domains."""
    return jsonify(get_domains())

@app.route('/api/logs')
def get_logs_api():
    """API endpoint to get logs."""
    return jsonify(get_logs())

@app.route('/api/status')
def get_status():
    """API endpoint to get engine status."""
    return jsonify({'is_running': CONFIG['engine_running']})

@app.route('/api/file_structure/<path:domain>')
def get_file_structure_api(domain):
    """API endpoint to get file structure for a domain."""
    return jsonify(get_file_structure(domain))

@app.route('/api/create_page', methods=['POST'])
def create_page():
    """API endpoint to create a new page."""
    try:
        data = request.json
        domain = data.get('domain')
        page_type = data.get('page_type')
        theme = data.get('theme')
        
        if not all([domain, page_type, theme]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        # Add logic to create the page
        return jsonify({'status': 'success', 'message': f'Page {page_type} created for {domain}'})
    except Exception as e:
        logger.error(f"Error creating page: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/file_explorer')
def get_file_explorer():
    """API endpoint to get file explorer data for root directory."""
    try:
        root_path = Path('.')
        items = []
        
        # Only show domain directories and important root files
        for item in root_path.iterdir():
            try:
                # Skip hidden directories and files
                if item.name.startswith('.'):
                    continue
                    
                # Check if it's a domain directory (has index.html)
                is_domain = item.is_dir() and (item / 'index.html').exists()
                
                item_info = {
                    'name': item.name,
                    'type': 'domain' if is_domain else ('directory' if item.is_dir() else 'file'),
                    'path': str(item.relative_to(root_path)),
                    'size': item.stat().st_size if item.is_file() else 0,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
                items.append(item_info)
            except Exception as e:
                logger.warning(f"Error processing {item}: {str(e)}")
                continue
        
        return jsonify(items)
    except Exception as e:
        logger.error(f"Error in file explorer: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/file_explorer/<path:subpath>')
def get_file_explorer_subpath(subpath):
    """API endpoint to get file explorer data for a subdirectory."""
    try:
        root_path = Path('.')
        target_path = root_path / subpath
        
        # Security check to prevent directory traversal
        if not str(target_path.resolve()).startswith(str(root_path.resolve())):
            return jsonify({'error': 'Invalid path'}), 400
            
        if not target_path.exists():
            return jsonify({'error': 'Path not found'}), 404
            
        items = []
        for item in target_path.iterdir():
            try:
                # Skip hidden directories and files
                if item.name.startswith('.'):
                    continue
                    
                item_info = {
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'path': str(item.relative_to(root_path)),
                    'size': item.stat().st_size if item.is_file() else 0,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
                items.append(item_info)
            except Exception as e:
                logger.warning(f"Error processing {item}: {str(e)}")
                continue
        
        return jsonify(items)
    except Exception as e:
        logger.error(f"Error in file explorer subpath: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview_file/<path:filepath>')
def preview_file(filepath):
    """API endpoint to preview file content."""
    try:
        root_path = Path('.')
        target_path = root_path / filepath
        
        # Security check to prevent directory traversal
        if not str(target_path.resolve()).startswith(str(root_path.resolve())):
            return jsonify({'error': 'Invalid path'}), 400
            
        if not target_path.exists():
            return jsonify({'error': 'File not found'}), 404
            
        if target_path.is_dir():
            return jsonify({'error': 'Cannot preview directories'}), 400
            
        # Only allow previewing HTML files for security
        if not target_path.suffix.lower() in ['.html', '.htm']:
            return jsonify({'error': 'Only HTML files can be previewed'}), 400
            
        try:
            content = target_path.read_text(encoding='utf-8')
            return jsonify({
                'content': content,
                'path': str(target_path.relative_to(root_path))
            })
        except UnicodeDecodeError:
            return jsonify({'error': 'File contains invalid characters'}), 400
    except Exception as e:
        logger.error(f"Error previewing file {filepath}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/domain_structure/<path:domain>')
def get_domain_structure(domain):
    """API endpoint to get the complete structure of a domain."""
    try:
        domain_path = Path(domain)
        if not domain_path.exists() or not domain_path.is_dir():
            return jsonify({'error': 'Domain not found'}), 404
            
        structure = {
            'name': domain_path.name,
            'path': str(domain_path),
            'files': [],
            'directories': []
        }
        
        for item in domain_path.rglob('*'):
            try:
                if item.is_file():
                    structure['files'].append({
                        'name': item.name,
                        'path': str(item.relative_to(domain_path)),
                        'size': item.stat().st_size,
                        'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
                elif item.is_dir():
                    structure['directories'].append({
                        'name': item.name,
                        'path': str(item.relative_to(domain_path))
                    })
            except Exception as e:
                logger.warning(f"Error processing {item}: {str(e)}")
                continue
        
        return jsonify(structure)
    except Exception as e:
        logger.error(f"Error getting domain structure: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/domain_pages/<path:domain>')
def get_domain_pages(domain):
    """API endpoint to get all HTML pages in a domain."""
    try:
        domain_path = Path(domain)
        if not domain_path.exists() or not domain_path.is_dir():
            return jsonify({'error': 'Domain not found'}), 404
            
        pages = []
        for item in domain_path.rglob('*.html'):
            try:
                pages.append({
                    'name': item.name,
                    'path': str(item.relative_to(domain_path)),
                    'size': item.stat().st_size,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            except Exception as e:
                logger.warning(f"Error processing {item}: {str(e)}")
                continue
        
        return jsonify(pages)
    except Exception as e:
        logger.error(f"Error getting domain pages: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)

@app.route('/api/records/<domain>', methods=['GET'])
def get_domain_records(domain):
    """Get all records for a domain."""
    try:
        record_type = request.args.get('type')
        records = domain_manager.get_records(domain, record_type)
        return jsonify({'status': 'success', 'records': records})
    except Exception as e:
        logger.error(f"Error getting records: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/records/<domain>', methods=['POST'])
def add_domain_record(domain):
    """Add a new record to a domain."""
    try:
        data = request.json
        record_type = data.get('type')
        record_data = data.get('data')
        
        if not all([record_type, record_data]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        success = domain_manager.add_record(domain, record_type, record_data)
        if success:
            return jsonify({'status': 'success', 'message': 'Record added successfully'})
        return jsonify({'status': 'error', 'message': 'Failed to add record'}), 500
    except Exception as e:
        logger.error(f"Error adding record: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/records/<domain>/<record_type>/<record_id>', methods=['PUT'])
def update_domain_record(domain, record_type, record_id):
    """Update an existing record."""
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        success = domain_manager.update_record(domain, record_type, record_id, data)
        if success:
            return jsonify({'status': 'success', 'message': 'Record updated successfully'})
        return jsonify({'status': 'error', 'message': 'Failed to update record'}), 500
    except Exception as e:
        logger.error(f"Error updating record: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/records/<domain>/<record_type>/<record_id>', methods=['DELETE'])
def delete_domain_record(domain, record_type, record_id):
    """Delete a record."""
    try:
        success = domain_manager.delete_record(domain, record_type, record_id)
        if success:
            return jsonify({'status': 'success', 'message': 'Record deleted successfully'})
        return jsonify({'status': 'error', 'message': 'Failed to delete record'}), 500
    except Exception as e:
        logger.error(f"Error deleting record: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/dns/<domain>', methods=['GET'])
def get_domain_dns(domain):
    """Get all DNS records for a domain."""
    try:
        record_type = request.args.get('type')
        dns_records = domain_manager.get_dns_records(domain, record_type)
        return jsonify({'status': 'success', 'dns': dns_records})
    except Exception as e:
        logger.error(f"Error getting DNS records: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/dns/<domain>', methods=['POST'])
def add_domain_dns(domain):
    """Add a new DNS record to a domain."""
    try:
        data = request.json
        record_type = data.get('type')
        record_data = data.get('data')
        
        if not all([record_type, record_data]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        success = domain_manager.add_dns_record(domain, record_type, record_data)
        if success:
            return jsonify({'status': 'success', 'message': 'DNS record added successfully'})
        return jsonify({'status': 'error', 'message': 'Failed to add DNS record'}), 500
    except Exception as e:
        logger.error(f"Error adding DNS record: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/dns/<domain>/<record_type>/<record_id>', methods=['PUT'])
def update_domain_dns(domain, record_type, record_id):
    """Update an existing DNS record."""
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        success = domain_manager.update_dns_record(domain, record_type, record_id, data)
        if success:
            return jsonify({'status': 'success', 'message': 'DNS record updated successfully'})
        return jsonify({'status': 'error', 'message': 'Failed to update DNS record'}), 500
    except Exception as e:
        logger.error(f"Error updating DNS record: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/dns/<domain>/<record_type>/<record_id>', methods=['DELETE'])
def delete_domain_dns(domain, record_type, record_id):
    """Delete a DNS record."""
    try:
        success = domain_manager.delete_dns_record(domain, record_type, record_id)
        if success:
            return jsonify({'status': 'success', 'message': 'DNS record deleted successfully'})
        return jsonify({'status': 'error', 'message': 'Failed to delete DNS record'}), 500
    except Exception as e:
        logger.error(f"Error deleting DNS record: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    for dir_name in CONFIG.values():
        if isinstance(dir_name, str):
            Path(dir_name).mkdir(exist_ok=True)
    
    # Create static directories if they don't exist
    Path('static').mkdir(exist_ok=True)
    Path('static/js').mkdir(exist_ok=True)
    
    app.run(debug=True, port=5000) 