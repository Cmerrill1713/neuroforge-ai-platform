#!/usr/bin/env python3
"""
General Agent - Create a content generation agent that can write blog posts and social media content

Be concise, intelligent, and avoid rambling.
Agent ID: agent_1b895177
Created: 2025-10-01T19:14:30.098987
"""

import numpy as np
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
import matplotlib.pyplot as plt
import json
import time

class GeneralAgent:
    """Create a content generation agent that can write blog posts and social media content

Be concise, intelligent, and avoid rambling."""
    
    def __init__(self):
        self.agent_id = "agent_1b895177"
        self.agent_type = "general"
        self.capabilities = ['web_scraping', 'data_analysis', 'file_processing']
        self.status = "active"
    
    def get_info(self):
        """Get agent information."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "status": self.status
        }
    
    
    def scrape_website(self, url: str):
        """Scrape data from a website."""
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.get_text()
        except Exception as e:
            return f"Error scraping {url}: {e}"


    def analyze_data(self, data):
        """Analyze data using pandas and numpy."""
        try:
            if isinstance(data, str):
                df = pd.read_csv(data)
            else:
                df = pd.DataFrame(data)
            
            analysis = {
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.to_dict(),
                'summary': df.describe().to_dict()
            }
            return analysis
        except Exception as e:
            return f"Error analyzing data: {e}"


    def process_file(self, file_path: str):
        """Process various file types."""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"File {file_path} not found"
            
            if path.suffix == '.json':
                with open(path, 'r') as f:
                    return json.load(f)
            elif path.suffix == '.csv':
                return pd.read_csv(path).to_dict()
            else:
                with open(path, 'r') as f:
                    return f.read()
        except Exception as e:
            return f"Error processing file: {e}"

    
    def execute_task(self, task: str, **kwargs):
        """Execute a task based on capabilities."""
        try:
            if "scrape" in task.lower():
                url = kwargs.get('url', '')
                return self.scrape_website(url)
            elif "analyze" in task.lower():
                data = kwargs.get('data', '')
                return self.analyze_data(data)
            elif "process" in task.lower():
                file_path = kwargs.get('file_path', '')
                return self.process_file(file_path)
            else:
                return f"Task '{task}' not supported by this agent"
        except Exception as e:
            return f"Error executing task: {e}"

# Example usage
if __name__ == "__main__":
    agent = GeneralAgent()
    print("Agent created successfully!")
    print(agent.get_info())
