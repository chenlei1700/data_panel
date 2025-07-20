#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append(".")
from base_server import BaseStockServer
from flask import jsonify
import json

class DemoServer(BaseStockServer):
    def get_dashboard_config(self):
        return {"layout": {"rows": 1, "cols": 1, "components": []}}
    
    def get_data_sources(self):
        return {}

if __name__ == "__main__":
    server = DemoServer(port=5005)
    print("演示服务器启动...")
    server.run(debug=True)
