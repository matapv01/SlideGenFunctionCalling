#!/usr/bin/env python3
"""Test script to verify all tools are properly imported and accessible."""

from tool_registry import ToolRegistryService

def main():
    """Test tool registry service."""
    print("Initializing Tool Registry Service...")
    service = ToolRegistryService()
    
    print("\nRegistered tool categories:")
    all_tools = service.get_all_tools()
    
    print(all_tools)
    

if __name__ == "__main__":
    main()
