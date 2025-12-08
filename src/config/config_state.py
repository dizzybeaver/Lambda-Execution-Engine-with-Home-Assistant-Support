"""
config_state.py
Version: 2025.10.14.01
Description: Configuration state management dataclasses for Lambda Execution Engine

Copyright 2025 Joseph Hersey

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from variables import ConfigurationTier


# ===== STATE MANAGEMENT DATACLASSES =====

@dataclass
class ConfigurationVersion:
    """Track configuration version history."""
    version: str
    timestamp: float
    changes: Dict[str, Any]


@dataclass
class ConfigurationState:
    """Track configuration state."""
    current_version: str = "1.0.0"
    active_tier: ConfigurationTier = ConfigurationTier.STANDARD
    active_preset: Optional[str] = None
    version_history: List[ConfigurationVersion] = field(default_factory=list)
    pending_changes: Dict[str, Any] = field(default_factory=dict)
    last_reload_time: float = 0.0
    reload_count: int = 0
    validation_failures: int = 0


# ===== EXPORTS =====

__all__ = [
    'ConfigurationVersion',
    'ConfigurationState'
]

# EOF
