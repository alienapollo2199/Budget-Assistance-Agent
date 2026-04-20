"""
GL Registry - Load GL definitions from JSON configuration files.
Enables scalable management of 115+ GL accounts without token bloat.
"""

import json
import os
from pathlib import Path


class GLRegistry:
    """Load and manage GL account rules from JSON definitions."""
    
    def __init__(self, gl_rules_dir="gl_rules"):
        self.gl_rules_dir = gl_rules_dir
        self._cache = {}
    
    def get_gl(self, gl_code):
        """Load GL definition by code."""
        if gl_code in self._cache:
            return self._cache[gl_code]
        
        gl_file = Path(self.gl_rules_dir) / f"gl_{gl_code}.json"
        if not gl_file.exists():
            raise ValueError(f"GL {gl_code} not found in {self.gl_rules_dir}/")
        
        with open(gl_file) as f:
            gl_def = json.load(f)
        
        self._cache[gl_code] = gl_def
        return gl_def
    
    def list_enabled_gls(self):
        """Return list of enabled GL codes."""
        gls = []
        for json_file in Path(self.gl_rules_dir).glob("gl_*.json"):
            try:
                with open(json_file) as f:
                    gl_def = json.load(f)
                    if gl_def.get("enabled", True):
                        gls.append(gl_def["code"])
            except json.JSONDecodeError:
                continue
        return sorted(gls)
    
    def get_path_a_keywords(self, gl_code):
        """Get Path A keywords for a GL."""
        gl_def = self.get_gl(gl_code)
        return gl_def["path_a"]["keywords"]
    
    def get_path_b_keywords(self, gl_code):
        """Get Path B keywords for a GL."""
        gl_def = self.get_gl(gl_code)
        return gl_def["path_b"]["keywords"]
