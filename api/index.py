import os
import sys

# Ensure project root is on sys.path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app as application  # WSGI app for Vercel

# Vercel detects `app` or `application` for WSGI; keep both
app = application
