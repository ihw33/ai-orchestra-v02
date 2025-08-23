"""
Test configuration and fixtures
"""
import sys
from pathlib import Path

# Add project root to Python path for test imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))