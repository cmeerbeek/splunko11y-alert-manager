#!/usr/bin/env python3
"""
SignalFX Alert Export Script

This script exports SignalFX detectors (alerts) from a Splunk Observability Cloud 
organization to YAML format for infrastructure-as-code management.

Usage:
    python export_signalfx_alerts.py --api-token <token> --realm <realm> --output-dir ./alerts

Requirements:
    - requests
    - pyyaml
    - click

Author: Generated for Splunk Observability Alert Management Project
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import click
import requests
import yaml


class SignalFXClient:
    """Client for interacting with SignalFX/Splunk Observability API."""
    
    def __init__(self, api_token: str, realm: str = "us0"):
        """
        Initialize SignalFX client.
        
        Args:
            api_token: SignalFX API token (org token)
            realm: SignalFX realm (e.g., us0, us1, eu0)
        """
        self.api_token = api_token
        self.realm = realm
        self.base_url = f"https://api.{realm}.signalfx.com" if realm != "us0" else "https://api.signalfx.com"
        self.headers = {
            "X-SF-Token": api_token,
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response content: {e.response.text}")
            raise
    
    def test_connection(self) -> bool:
        """Test API connection and token validity."""
        try:
            response = self._make_request("GET", "v2/detector", params={"limit": 1})
            self.logger.info("API connection successful")
            return True
        except Exception as e:
            self.logger.error(f"API connection failed: {e}")
            return False
    
    def get_detectors(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Retrieve detectors from SignalFX.
        
        Args:
            limit: Maximum number of detectors to retrieve (None for all)
            offset: Number of detectors to skip
            
        Returns:
            List of detector dictionaries
        """
        detectors = []
        current_offset = offset
        page_size = 50  # Default page size
        
        while True:
            params = {
                "offset": current_offset,
                "limit": page_size
            }
            
            if limit and len(detectors) >= limit:
                break
                
            self.logger.info(f"Fetching detectors (offset: {current_offset}, limit: {page_size})")
            
            try:
                response = self._make_request("GET", "v2/detector", params=params)
                data = response.json()
                
                if not data.get("results"):
                    break
                
                batch_detectors = data["results"]
                detectors.extend(batch_detectors)
                
                self.logger.info(f"Retrieved {len(batch_detectors)} detectors (total: {len(detectors)})")
                
                # Check if we have more pages
                if len(batch_detectors) < page_size:
                    break
                    
                current_offset += page_size
                
                # Apply limit if specified
                if limit and len(detectors) >= limit:
                    detectors = detectors[:limit]
                    break
                    
            except Exception as e:
                self.logger.error(f"Failed to fetch detectors: {e}")
                break
        
        return detectors
    
    def get_detector(self, detector_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific detector by ID.
        
        Args:
            detector_id: Detector ID
            
        Returns:
            Detector dictionary
        """
        response = self._make_request("GET", f"v2/detector/{detector_id}")
        return response.json()


class AlertExporter:
    """Export SignalFX alerts to YAML format."""
    
    def __init__(self, output_dir: str):
        """
        Initialize alert exporter.
        
        Args:
            output_dir: Directory to save exported alerts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _clean_detector_data(self, detector: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and prepare detector data for YAML export.
        
        Args:
            detector: Raw detector data from API
            
        Returns:
            Cleaned detector data
        """
        # Remove system-generated fields that shouldn't be in YAML
        excluded_fields = {
            "id", "createdOn", "lastUpdateUserId", "lastUpdatedOn", 
            "createdBy", "lastUpdateTime", "updateTime", "createTime"
        }
        
        cleaned = {}
        for key, value in detector.items():
            if key not in excluded_fields:
                cleaned[key] = value
        
        return cleaned
    
    def _generate_filename(self, detector: Dict[str, Any]) -> str:
        """
        Generate filename for detector YAML file.
        
        Args:
            detector: Detector data
            
        Returns:
            Filename string
        """
        name = detector.get("name", "unnamed")
        # Clean filename - remove special characters
        safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_", " ")).strip()
        safe_name = safe_name.replace(" ", "_")
        return f"{safe_name}.yaml"
    
    def export_detector(self, detector: Dict[str, Any]) -> str:
        """
        Export a single detector to YAML file.
        
        Args:
            detector: Detector data
            
        Returns:
            Path to exported file
        """
        cleaned_detector = self._clean_detector_data(detector)
        filename = self._generate_filename(detector)
        file_path = self.output_dir / filename
        
        # Add metadata
        export_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "original_id": detector.get("id"),
                "export_tool": "signalfx-alert-exporter"
            },
            "detector": cleaned_detector
        }
        
        with open(file_path, 'w') as f:
            yaml.dump(export_data, f, default_flow_style=False, sort_keys=False)
        
        self.logger.info(f"Exported detector '{detector.get('name')}' to {file_path}")
        return str(file_path)
    
    def export_detectors(self, detectors: List[Dict[str, Any]]) -> List[str]:
        """
        Export multiple detectors to YAML files.
        
        Args:
            detectors: List of detector data
            
        Returns:
            List of exported file paths
        """
        exported_files = []
        
        for detector in detectors:
            try:
                file_path = self.export_detector(detector)
                exported_files.append(file_path)
            except Exception as e:
                self.logger.error(f"Failed to export detector '{detector.get('name')}': {e}")
        
        return exported_files
    
    def create_summary(self, detectors: List[Dict[str, Any]], exported_files: List[str]) -> str:
        """
        Create export summary file.
        
        Args:
            detectors: List of detector data
            exported_files: List of exported file paths
            
        Returns:
            Path to summary file
        """
        summary_data = {
            "export_summary": {
                "exported_at": datetime.now().isoformat(),
                "total_detectors": len(detectors),
                "successfully_exported": len(exported_files),
                "failed_exports": len(detectors) - len(exported_files),
                "export_tool": "signalfx-alert-exporter"
            },
            "exported_files": exported_files,
            "detector_names": [d.get("name") for d in detectors]
        }
        
        summary_path = self.output_dir / "export_summary.yaml"
        with open(summary_path, 'w') as f:
            yaml.dump(summary_data, f, default_flow_style=False, sort_keys=False)
        
        return str(summary_path)


@click.command()
@click.option('--api-token', required=True, help='SignalFX API token (org token)')
@click.option('--realm', default='us0', help='SignalFX realm (e.g., us0, us1, eu0)')
@click.option('--output-dir', default='./alerts', help='Output directory for exported alerts')
@click.option('--limit', type=int, help='Maximum number of detectors to export')
@click.option('--test-connection', is_flag=True, help='Test API connection and exit')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def main(api_token: str, realm: str, output_dir: str, limit: Optional[int], 
         test_connection: bool, verbose: bool):
    """
    Export SignalFX detectors (alerts) to YAML format.
    
    This script connects to SignalFX/Splunk Observability Cloud and exports
    all detectors to individual YAML files for infrastructure-as-code management.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize client
    client = SignalFXClient(api_token, realm)
    
    if test_connection:
        if client.test_connection():
            click.echo("✓ API connection successful")
            sys.exit(0)
        else:
            click.echo("✗ API connection failed")
            sys.exit(1)
    
    # Test connection first
    if not client.test_connection():
        click.echo("✗ Failed to connect to SignalFX API. Please check your token and realm.")
        sys.exit(1)
    
    click.echo(f"🔍 Fetching detectors from SignalFX (realm: {realm})")
    
    try:
        # Fetch detectors
        detectors = client.get_detectors(limit=limit)
        
        if not detectors:
            click.echo("No detectors found.")
            sys.exit(0)
        
        click.echo(f"📊 Found {len(detectors)} detectors")
        
        # Export detectors
        exporter = AlertExporter(output_dir)
        exported_files = exporter.export_detectors(detectors)
        
        # Create summary
        summary_path = exporter.create_summary(detectors, exported_files)
        
        click.echo(f"✅ Export complete!")
        click.echo(f"   - Exported {len(exported_files)} detectors to {output_dir}")
        click.echo(f"   - Summary saved to {summary_path}")
        
        if len(exported_files) < len(detectors):
            failed_count = len(detectors) - len(exported_files)
            click.echo(f"   - ⚠️  {failed_count} detectors failed to export (check logs)")
        
    except Exception as e:
        click.echo(f"✗ Export failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()