#!/usr/bin/env python3
"""
File_Processor Agent - Create a file processing agent that can handle JSON, CSV, and text files

Be concise, intelligent, and avoid rambling.
Agent ID: agent_735f52f6
Created: 2025-10-01T19:12:37.271708
"""

import os
import json
from pathlib import Path

class File_ProcessorAgent:
    """Create a file processing agent that can handle JSON, CSV, and text files

Be concise, intelligent, and avoid rambling."""
    
    def __init__(self):
        self.agent_id = "agent_735f52f6"
        self.agent_type = "file_processor"
        self.capabilities = ['file_processing']
        self.status = "active"
    
    def get_info(self):
        """Get agent information."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "status": self.status
        }
    
    
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
    agent = File_ProcessorAgent()
    print("Agent created successfully!")
    print(agent.get_info())
