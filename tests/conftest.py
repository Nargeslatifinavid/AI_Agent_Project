# tests/conftest.py
import sys, os


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

sys.path.insert(0, PROJECT_ROOT)