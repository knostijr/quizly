"""
List all available Gemini models.
"""

import google.generativeai as genai
from django.conf import settings
import django
import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


def list_models():
    """List all available Gemini models."""
    print("Listing available Gemini models...")
    print(f"API Key: {settings.GEMINI_API_KEY[:10]}...\n")

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)

        print("Available models:\n")

        for model in genai.list_models():
            print(f"Model: {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Supported methods: {model.supported_generation_methods}")
            print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    list_models()
