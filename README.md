# SignalFX Alert Export Script

This script exports SignalFX detectors (alerts) from a Splunk Observability Cloud organization to YAML format for infrastructure-as-code management.

## Features

- Export all detectors from a SignalFX organization
- Support for multiple realms (us0, us1, eu0, etc.)
- Automatic pagination for large alert sets
- YAML export with metadata tracking
- Connection testing functionality
- Comprehensive error handling and logging

## Prerequisites

- Python 3.8+
- SignalFX API token (organization access token)
- Required Python packages (see requirements.txt)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Export
```bash
python export_signalfx_alerts.py --api-token YOUR_API_TOKEN --realm us0 --output-dir ./alerts
```

### Test Connection
```bash
python export_signalfx_alerts.py --api-token YOUR_API_TOKEN --realm us0 --test-connection
```

### Export with Limit
```bash
python export_signalfx_alerts.py --api-token YOUR_API_TOKEN --realm us0 --limit 50 --output-dir ./alerts
```

### Verbose Output
```bash
python export_signalfx_alerts.py --api-token YOUR_API_TOKEN --realm us0 --verbose --output-dir ./alerts
```

## Command Line Options

- `--api-token`: Required. SignalFX API token (organization access token)
- `--realm`: SignalFX realm (default: us0). Examples: us0, us1, eu0, ap0
- `--output-dir`: Output directory for exported alerts (default: ./alerts)
- `--limit`: Maximum number of detectors to export (optional)
- `--test-connection`: Test API connection and exit
- `--verbose`: Enable verbose logging
- `--help`: Show help message

## Output Format

Each detector is exported as a separate YAML file with the following structure:

```yaml
metadata:
  exported_at: "2025-07-09T22:40:54.145595"
  original_id: "detector-123"
  export_tool: "signalfx-alert-exporter"
detector:
  name: "CPU Usage Alert"
  description: "Alert when CPU usage exceeds 80%"
  programText: "A = data('cpu.utilization').mean(by=['host']).mean(over='5m')"
  rules:
    - severity: "Major"
      disabled: false
      notifications: []
      # ... other rule properties
```

## API Token Setup

1. Log into Splunk Observability Cloud
2. Go to Settings > Access Tokens
3. Create a new organization access token
4. Copy the token value for use with the script

## Realm Detection

Find your realm in the Splunk Observability Cloud UI:
- Go to Settings > Organization Overview
- Your realm is shown in the "Realm" field

Common realms:
- `us0`: Default US realm
- `us1`: US East realm  
- `eu0`: European realm
- `ap0`: Asia Pacific realm

## Error Handling

The script includes comprehensive error handling:
- API connection validation
- Rate limiting compliance
- Graceful handling of API errors
- Detailed error logging

## Output Files

- Individual detector YAML files (one per detector)
- `export_summary.yaml`: Summary of the export operation

## Troubleshooting

1. **Authentication errors**: Verify your API token is correct and has organization access
2. **Realm errors**: Ensure you're using the correct realm for your organization
3. **Rate limiting**: The script handles rate limits automatically with proper error handling
4. **Connection issues**: Use `--test-connection` to verify API connectivity

## Security Notes

- Never commit API tokens to version control
- Use environment variables or secure credential storage
- API tokens should have minimal required permissions
- Rotate API tokens regularly

## Examples

Export all detectors from us0 realm:
```bash
python export_signalfx_alerts.py --api-token $SIGNALFX_TOKEN --realm us0
```

Export first 100 detectors with verbose logging:
```bash
python export_signalfx_alerts.py --api-token $SIGNALFX_TOKEN --limit 100 --verbose
```

Test connection only:
```bash
python export_signalfx_alerts.py --api-token $SIGNALFX_TOKEN --test-connection
```