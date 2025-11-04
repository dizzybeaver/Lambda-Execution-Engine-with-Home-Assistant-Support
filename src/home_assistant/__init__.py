"""
__init__.py - Home Assistant Extension Package
Version: 1.0.0 - PHASE 1
Date: 2025-11-03
Description: HA-SUGA Extension - Only loads when HOME_ASSISTANT_ENABLE=true

PHASE 1: Setup & Structure
- Created HA extension package
- Conditional loading based on environment variable
- Provides ha_interconnect when enabled

Architecture:
This package implements HA-SUGA (Home Assistant Single Universal Gateway Architecture)
parallel to LEE's SUGA pattern. All HA functionality is isolated in this package and
only loads when explicitly enabled.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os

# Check if Home Assistant extension is enabled
HA_ENABLED = os.getenv('HOME_ASSISTANT_ENABLE', 'false').lower() == 'true'

if HA_ENABLED:
    # PHASE 1: Import HA gateway when enabled
    from . import ha_interconnect
    
    __all__ = ['ha_interconnect', 'HA_ENABLED']
else:
    # HA disabled - export nothing
    __all__ = ['HA_ENABLED']

# Version info
__version__ = '1.0.0'
__ha_suga_version__ = 'PHASE_1'

# EOF
