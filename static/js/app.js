new Vue({
    el: '#app',
    data: {
        domains: [],
        logs: [],
        isRunning: false,
        logInterval: null,
        statusInterval: null,
        fileStructures: {},
        newPageType: 'home',
        newPageTheme: 'default',
        pageTypes: ['home', 'about', 'contact', 'blog', 'services', 'portfolio'],
        themeOptions: ['default', 'modern', 'classic', 'minimal'],
        error: null,
        // File Explorer
        fileExplorerItems: [],
        currentPath: '',
        pathHistory: [],
        loadingExplorer: false,
        selectedDomain: null,
        domainStructure: null,
        domainPages: [],
        // Preview
        previewContent: '',
        previewPath: '',
        loadingPreview: false,
        previewError: null,
        // Records
        records: {},
        newRecordType: '',
        newRecordData: {},
        selectedRecordType: null,
        loadingRecords: false,
        // DNS
        dnsRecords: {},
        newDnsType: 'A',
        newDnsData: {
            name: '',
            value: '',
            ttl: 3600
        },
        dnsTypes: ['A', 'CNAME', 'MX', 'TXT', 'NS'],
        loadingDns: false
    },
    methods: {
        async fetchDomains() {
            try {
                const response = await fetch('/api/domains');
                if (!response.ok) {
                    throw new Error(`Failed to fetch domains: ${response.statusText}`);
                }
                this.domains = await response.json();
                console.log('Fetched domains:', this.domains);
                
                // Initialize fileStructures for each domain
                this.domains.forEach(domain => {
                    if (!this.fileStructures[domain.name]) {
                        this.$set(this.fileStructures, domain.name, []);
                    }
                });
                
                // Pre-fetch file structures for all domains
                for (const domain of this.domains) {
                    await this.getFileStructure(domain.name);
                }
            } catch (error) {
                console.error('Error fetching domains:', error);
                this.error = error.message;
            }
        },
        async fetchLogs() {
            try {
                const response = await fetch('/api/logs');
                if (!response.ok) {
                    throw new Error(`Failed to fetch logs: ${response.statusText}`);
                }
                this.logs = await response.json();
            } catch (error) {
                console.error('Error fetching logs:', error);
                this.error = error.message;
            }
        },
        async checkStatus() {
            try {
                const response = await fetch('/api/status');
                if (!response.ok) {
                    throw new Error(`Failed to check status: ${response.statusText}`);
                }
                const data = await response.json();
                this.isRunning = data.isRunning;
            } catch (error) {
                console.error('Error checking status:', error);
                this.error = error.message;
            }
        },
        async getFileStructure(domain) {
            try {
                const response = await fetch(`/api/file_structure/${domain}`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch file structure: ${response.statusText}`);
                }
                const data = await response.json();
                console.log(`Fetched file structure for ${domain}:`, data);
                
                // Ensure data is an array and each item has required properties
                const validatedData = Array.isArray(data) ? data.map(item => ({
                    type: item?.type || 'file',
                    path: item?.path || '',
                    size: item?.size || 0
                })) : [];
                
                this.$set(this.fileStructures, domain, validatedData);
            } catch (error) {
                console.error(`Error fetching file structure for ${domain}:`, error);
                this.error = error.message;
                this.$set(this.fileStructures, domain, []);
            }
        },
        formatSize(bytes) {
            if (!bytes && bytes !== 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },
        async createPage(domain) {
            try {
                const response = await fetch('/api/create-page', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        domain,
                        pageType: this.newPageType,
                        theme: this.newPageTheme
                    })
                });
                if (response.ok) {
                    // Refresh file structure after creating page
                    delete this.fileStructures[domain];
                    await this.getFileStructure(domain);
                } else {
                    console.error('Error creating page:', await response.text());
                }
            } catch (error) {
                console.error('Error creating page:', error);
            }
        },
        async runEngine() {
            try {
                const response = await fetch('/api/run_engine', { method: 'POST' });
                if (response.ok) {
                    this.isRunning = true;
                }
            } catch (error) {
                console.error('Error starting engine:', error);
            }
        },
        async stopEngine() {
            try {
                const response = await fetch('/api/stop_engine', { method: 'POST' });
                if (response.ok) {
                    this.isRunning = false;
                }
            } catch (error) {
                console.error('Error stopping engine:', error);
            }
        },
        async fetchFileExplorer(path = '') {
            try {
                this.loadingExplorer = true;
                let url = '/api/file_explorer';
                if (this.selectedDomain) {
                    url = `/api/file_explorer/${this.selectedDomain}`;
                    if (path) {
                        url += `/${path}`;
                    }
                } else if (path) {
                    url += `/${path}`;
                }
                
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`Failed to fetch file explorer data: ${response.statusText}`);
                }
                this.fileExplorerItems = await response.json();
                this.currentPath = path;
                if (path) {
                    this.pathHistory.push(path);
                }
            } catch (error) {
                console.error('Error fetching file explorer:', error);
                this.error = error.message;
            } finally {
                this.loadingExplorer = false;
            }
        },
        async fetchDomainStructure(domain) {
            try {
                const response = await fetch(`/api/domain_structure/${domain}`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch domain structure: ${response.statusText}`);
                }
                this.domainStructure = await response.json();
            } catch (error) {
                console.error('Error fetching domain structure:', error);
                this.error = error.message;
            }
        },
        async fetchDomainPages(domain) {
            try {
                const response = await fetch(`/api/domain_pages/${domain}`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch domain pages: ${response.statusText}`);
                }
                this.domainPages = await response.json();
            } catch (error) {
                console.error('Error fetching domain pages:', error);
                this.error = error.message;
            }
        },
        async selectDomain(domain) {
            this.selectedDomain = domain;
            this.currentPath = '';
            this.pathHistory = [];
            this.clearPreview();
            await Promise.all([
                this.fetchFileExplorer(domain),
                this.fetchDomainStructure(domain),
                this.fetchDomainPages(domain)
            ]);
        },
        clearDomainSelection() {
            this.selectedDomain = null;
            this.currentPath = '';
            this.pathHistory = [];
            this.domainStructure = null;
            this.domainPages = [];
            this.clearPreview();
            this.fetchFileExplorer();
        },
        navigateUp() {
            if (this.currentPath) {
                const parentPath = this.currentPath.split('/').slice(0, -1).join('/');
                this.fetchFileExplorer(parentPath);
            }
        },
        formatDate(dateString) {
            return new Date(dateString).toLocaleString();
        },
        async previewFile(path) {
            try {
                this.loadingPreview = true;
                this.previewError = null;
                const response = await fetch(`/api/preview_file/${path}`);
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Failed to preview file');
                }
                const data = await response.json();
                this.previewContent = data.content;
                this.previewPath = data.path;
            } catch (error) {
                console.error('Error previewing file:', error);
                this.previewError = error.message;
                this.previewContent = '';
                this.previewPath = '';
            } finally {
                this.loadingPreview = false;
            }
        },
        clearPreview() {
            this.previewContent = '';
            this.previewPath = '';
            this.previewError = null;
        },
        async fetchRecords(domain) {
            try {
                this.loadingRecords = true;
                const response = await fetch(`/api/records/${domain}`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch records: ${response.statusText}`);
                }
                const data = await response.json();
                this.records = data.records;
            } catch (error) {
                console.error('Error fetching records:', error);
                this.error = error.message;
            } finally {
                this.loadingRecords = false;
            }
        },
        async addRecord(domain) {
            try {
                const response = await fetch(`/api/records/${domain}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        type: this.newRecordType,
                        data: this.newRecordData
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to add record: ${response.statusText}`);
                }
                
                await this.fetchRecords(domain);
                this.newRecordType = '';
                this.newRecordData = {};
            } catch (error) {
                console.error('Error adding record:', error);
                this.error = error.message;
            }
        },
        async updateRecord(domain, recordType, recordId, data) {
            try {
                const response = await fetch(`/api/records/${domain}/${recordType}/${recordId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to update record: ${response.statusText}`);
                }
                
                await this.fetchRecords(domain);
            } catch (error) {
                console.error('Error updating record:', error);
                this.error = error.message;
            }
        },
        async deleteRecord(domain, recordType, recordId) {
            try {
                const response = await fetch(`/api/records/${domain}/${recordType}/${recordId}`, {
                    method: 'DELETE'
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to delete record: ${response.statusText}`);
                }
                
                await this.fetchRecords(domain);
            } catch (error) {
                console.error('Error deleting record:', error);
                this.error = error.message;
            }
        },
        async fetchDnsRecords(domain) {
            try {
                this.loadingDns = true;
                const response = await fetch(`/api/dns/${domain}`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch DNS records: ${response.statusText}`);
                }
                const data = await response.json();
                this.dnsRecords = data.dns.records;
            } catch (error) {
                console.error('Error fetching DNS records:', error);
                this.error = error.message;
            } finally {
                this.loadingDns = false;
            }
        },
        async addDnsRecord(domain) {
            try {
                const response = await fetch(`/api/dns/${domain}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        type: this.newDnsType,
                        data: this.newDnsData
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to add DNS record: ${response.statusText}`);
                }
                
                await this.fetchDnsRecords(domain);
                this.newDnsData = {
                    name: '',
                    value: '',
                    ttl: 3600
                };
            } catch (error) {
                console.error('Error adding DNS record:', error);
                this.error = error.message;
            }
        },
        async updateDnsRecord(domain, recordType, recordId, data) {
            try {
                const response = await fetch(`/api/dns/${domain}/${recordType}/${recordId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to update DNS record: ${response.statusText}`);
                }
                
                await this.fetchDnsRecords(domain);
            } catch (error) {
                console.error('Error updating DNS record:', error);
                this.error = error.message;
            }
        },
        async deleteDnsRecord(domain, recordType, recordId) {
            try {
                const response = await fetch(`/api/dns/${domain}/${recordType}/${recordId}`, {
                    method: 'DELETE'
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to delete DNS record: ${response.statusText}`);
                }
                
                await this.fetchDnsRecords(domain);
            } catch (error) {
                console.error('Error deleting DNS record:', error);
                this.error = error.message;
            }
        }
    },
    mounted() {
        this.fetchDomains();
        this.fetchLogs();
        this.checkStatus();
        this.fetchFileExplorer();  // Initialize file explorer
        
        // Set up intervals for real-time updates
        this.logInterval = setInterval(this.fetchLogs, 5000);
        this.statusInterval = setInterval(this.checkStatus, 1000);
    },
    beforeDestroy() {
        // Clean up intervals
        if (this.logInterval) clearInterval(this.logInterval);
        if (this.statusInterval) clearInterval(this.statusInterval);
    }
}); 