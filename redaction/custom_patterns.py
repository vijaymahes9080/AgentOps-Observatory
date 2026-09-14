"""
AgentOps Observatory - Custom Redaction Pattern Registry (Phase 3+)
Enables enterprise operators to register organization-specific redaction patterns,
internal project code words, employee ID numbers, and custom token formats.
"""

import re
from typing import Dict, List, Pattern


class CustomRedactionRegistry:
    def __init__(self):
        self._custom_patterns: Dict[str, Pattern] = {}

    def register_pattern(self, name: str, regex_string: str, flags: int = re.IGNORECASE):
        self._custom_patterns[name.upper()] = re.compile(regex_string, flags)

    def get_patterns(self) -> Dict[str, Pattern]:
        return self._custom_patterns.copy()

    def remove_pattern(self, name: str):
        self._custom_patterns.pop(name.upper(), None)


# Global registry instance
custom_redaction_registry = CustomRedactionRegistry()

# Default enterprise patterns: Employee ID (EMP-XXXXX), Internal Project Codewords
custom_redaction_registry.register_pattern("EMPLOYEE_ID", r"\bEMP-\d{5,8}\b")
custom_redaction_registry.register_pattern("CONFIDENTIAL_PROJECT", r"\bPROJECT-(?:TITAN|VALKYRIE|APOLLO)-SECRET\b")
