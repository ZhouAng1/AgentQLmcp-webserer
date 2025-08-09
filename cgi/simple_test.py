#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json

print("Content-Type: application/json")
print()

try:
    # 读取环境变量
    content_length = int(os.environ.get('CONTENT_LENGTH', 0))
    
    if content_length > 0:
        post_data = sys.stdin.read(content_length)
        request_data = json.loads(post_data)
        message = request_data.get('message', '')
        
        response = {
            "success": True,
            "response": f"收到消息: {message}",
            "session_id": "test-session-123"
        }
    else:
        response = {
            "success": False,
            "error": "No message provided"
        }
    
    print(json.dumps(response))
    
except Exception as e:
    error_response = {
        "success": False,
        "error": f"CGI Error: {str(e)}"
    }
    print(json.dumps(error_response)) 