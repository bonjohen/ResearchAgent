# Deployment Guide for Research Agent

This guide provides instructions for deploying the Research Agent to a GoDaddy hosting environment.

## Prerequisites

Before deploying, ensure you have:

1. A GoDaddy hosting plan with Python support
2. SSH access to your GoDaddy server
3. The following information:
   - Server hostname
   - SSH username
   - Path to deploy the application

## System Requirements

### Production Environment
- Linux-based server with Python 3.9+ support
- Minimum 4GB RAM for cloud-based models only (8GB+ if using local models)
- 10GB+ disk space (50GB+ if using local models)
- HTTPS support for secure API communication

## Deployment Steps

### 1. Set Up Environment Variables

Set the following environment variables on your local machine:

```
GODADDY_HOST=your-domain.com
GODADDY_USER=your-ssh-username
GODADDY_PATH=/path/to/deploy
```

### 2. Run the Deployment Script

Run the deployment script from the project root:

```
scripts/deploy_godaddy.cmd
```

This script will:
- Create a deployment package
- Generate necessary configuration files
- Upload the package to your GoDaddy server
- Install dependencies
- Configure the application

### 3. Configure Environment Variables on the Server

Set up the following environment variables on your GoDaddy server:

```
OPENAI_API_KEY=your-openai-api-key
SERPER_API_KEY=your-serper-api-key (optional)
TAVILY_API_KEY=your-tavily-api-key (optional)
GOOGLE_API_KEY=your-google-api-key (optional)
GOOGLE_CSE_ID=your-google-cse-id (optional)
EXTERNAL_STORAGE_PATH=/path/to/storage
```

You can set these variables through the GoDaddy hosting control panel or by creating a `.env` file in the application directory.

### 4. Configure Web Server

The deployment script creates a `.htaccess` file for Apache configuration. If you're using a different web server, you'll need to configure it manually:

#### Apache (already configured by the script)
The `.htaccess` file redirects requests to the WSGI application.

#### Nginx
Create a configuration file in `/etc/nginx/sites-available/` with the following content:

```
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Then, start Gunicorn:

```
cd /path/to/deploy
gunicorn --bind 127.0.0.1:8000 wsgi:application
```

### 5. Set Up SSL Certificate

Enable HTTPS for your domain through the GoDaddy control panel or by using Let's Encrypt.

### 6. Test the Deployment

Visit your domain in a web browser to ensure the application is running correctly.

## Troubleshooting

### Common Issues

1. **Application not starting**
   - Check the error logs at `/path/to/deploy/logs/error.log`
   - Ensure all dependencies are installed
   - Verify Python version compatibility

2. **API keys not working**
   - Confirm environment variables are set correctly
   - Check for typos in API keys
   - Verify API key permissions and quotas

3. **Permission errors**
   - Ensure the application directory has appropriate permissions
   - Check file ownership and group settings

4. **Database or storage issues**
   - Verify the external storage path exists and is writable
   - Check disk space availability

## Maintenance

### Updating the Application

To update the deployed application:

1. Make changes to your local codebase
2. Run the deployment script again
3. The script will update the files on the server

### Backup Procedures

Regularly back up the following:

1. Application code
2. Environment variables
3. Research data in the external storage path

### Monitoring

Set up monitoring for:

1. Server health and resource usage
2. Application errors and exceptions
3. API usage and quotas

## Support

If you encounter issues with the deployment, please:

1. Check the troubleshooting section above
2. Review the server logs
3. Consult the GoDaddy hosting documentation
4. Contact the project maintainers for assistance
