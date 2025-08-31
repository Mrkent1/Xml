#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script kiểm tra trạng thái GitHub Actions
"""

import requests
import json

def check_github_actions():
    """Kiểm tra trạng thái GitHub Actions"""
    try:
        repo = "Mrkent1/Xml"
        url = f"https://api.github.com/repos/{repo}/actions/runs"
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            runs = response.json().get("workflow_runs", [])
            print("📊 GitHub Actions Status:")
            print("=" * 40)
            
            for i, run in enumerate(runs[:5]):
                run_id = run["id"]
                name = run["name"]
                status = run["status"]
                conclusion = run.get("conclusion", "running")
                created_at = run["created_at"]
                
                print(f"• Run {run_id}: {name}")
                print(f"  Status: {status}")
                print(f"  Conclusion: {conclusion}")
                print(f"  Created: {created_at}")
                print()
                
            return runs
        else:
            print(f"❌ Lỗi API GitHub: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return []

if __name__ == "__main__":
    check_github_actions()
