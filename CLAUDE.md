# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Splunk Observability Alert Management** project - a Python-based infrastructure-as-code solution for managing Splunk Observability alerts. The project aims to transform manual UI-based alert management into a declarative, version-controlled workflow using Python scripts, YAML configurations, and Terraform.

## Project Architecture

### Core Components (To Be Implemented)

**Export System**
- Python scripts to export existing Splunk Observability alerts to YAML format
- API client for Splunk Observability REST API integration
- Support for all alert types: detectors, events, anomaly detection
- Batch processing capabilities for large alert sets (150+ alerts)

**YAML Schema & Validation**
- Comprehensive YAML schema supporting all Splunk Observability alert fields
- Python validation scripts with detailed error reporting
- Schema versioning for future compatibility
- Cross-reference validation for alert dependencies

**Terraform Integration**
- Terraform configurations using SignalFX provider
- YAML-driven alert provisioning with full CRUD lifecycle
- Multi-organization support via configuration variables
- State management for tracking deployed alerts

**CI/CD Pipeline**
- Azure DevOps pipeline for automated validation and deployment
- Environment-specific deployment stages (dev/staging/production)
- Pull request validation with comprehensive error reporting
- Integration with approval workflows

## Technology Stack

- **Python 3.8+**: Core scripting with requests, PyYAML, click libraries
- **Terraform 1.0+**: Infrastructure provisioning using SignalFX provider
- **Azure DevOps**: CI/CD pipeline orchestration
- **YAML**: Configuration format with JSON Schema validation
- **Splunk Observability REST API**: Data export and management

## Development Workflow

### Initial Setup (Project is in early stage)
```bash
# Project structure will include:
# ├── src/
# │   ├── export/          # Alert export scripts
# │   ├── validation/      # YAML validation tools
# │   └── terraform/       # Terraform configurations
# ├── schemas/             # YAML schema definitions
# ├── tests/              # Unit and integration tests
# └── pipelines/          # Azure DevOps pipeline definitions
```

### Key APIs and CLI Commands (To Be Implemented)

**Export Operations**
```bash
splunk-alerts export --org-token <token> --output-dir ./alerts
```

**Validation**
```bash
splunk-alerts validate --schema-version 1.0 --alert-dir ./alerts
```

**Deployment**
```bash
terraform plan -var-file=environments/prod.tfvars
terraform apply -var-file=environments/prod.tfvars
```

## Performance Requirements

- Export script: Process 150 alerts within 5 minutes
- Validation: Complete within 30 seconds for typical alert sets
- Terraform operations: Complete within 10 minutes for full alert set
- Pipeline execution: Commit to deployment within 15 minutes

## Security Considerations

- API tokens must be stored as secure pipeline variables
- Rate limiting compliance with Splunk Observability API limits
- Support for credential rotation without workflow disruption
- No sensitive information in code or version control

## Testing Strategy

- Unit tests for all Python functions with mock API responses
- Integration tests using test organizations or sandbox environments
- Terraform validation tests with plan-only execution
- End-to-end pipeline testing with sample alert configurations
- Performance testing with large alert sets (150+ alerts)

## Error Handling Requirements

- Comprehensive error messages with file names and line numbers
- Graceful handling of API rate limits and timeouts
- Clear validation feedback for YAML schema violations
- Detailed deployment logs with success/failure indicators

## Development Notes

This project is in the requirements definition phase based on the PRD.md file. The implementation will focus on:

1. **Infrastructure-as-Code principles** for alert management
2. **GitOps workflows** with version control and code review
3. **Multi-environment support** with consistent deployment processes
4. **Enterprise-grade** performance and security requirements
5. **Comprehensive testing** and validation at all stages

The codebase structure and implementation details will be developed following the technical architecture outlined in the PRD, with emphasis on maintainable, well-tested Python code and robust Terraform configurations.