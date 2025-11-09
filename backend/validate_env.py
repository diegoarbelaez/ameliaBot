#!/usr/bin/env python3
"""
Environment Variables Validation Script
Run this script to validate your .env configuration before starting the application.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path to import from app
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Found .env file at: {env_path}")
else:
    print(f"❌ No .env file found at: {env_path}")
    print("💡 Copy .env.example to .env and fill in your values")
    sys.exit(1)

# Define required environment variables
REQUIRED_VARS = [
    # Database
    "DATABASE_URL",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    
    # Slack
    "SLACK_BOT_TOKEN",
    "SLACK_APP_TOKEN",
    "SLACK_SIGNING_SECRET",
    
    # Digital Ocean
    "DIGITALOCEAN_API_KEY",
    "DIGITALOCEAN_AGENT_ID",
    
    # Whapi
    "WHAPI_API_KEY",
    "WHAPI_BASE_URL",
    
    # Security
    "SECRET_KEY",
    
    # CORS
    "CORS_ORIGINS",
]

OPTIONAL_VARS = [
    "DIGITALOCEAN_API_URL",
    "WHAPI_CHANNEL_ID",
    "ENVIRONMENT",
    "LOG_LEVEL",
    "RATE_LIMIT_PER_MINUTE",
]


def validate_variable(var_name: str) -> Tuple[bool, str]:
    """
    Validate a single environment variable.
    Returns (is_valid, message)
    """
    value = os.getenv(var_name)
    
    if value is None or value == "":
        return False, f"❌ {var_name}: Not set"
    
    # Check for placeholder values
    placeholder_indicators = [
        "your-",
        "your_",
        "here",
        "example",
        "placeholder",
        "changeme",
        "change_me"
    ]
    
    value_lower = value.lower()
    if any(indicator in value_lower for indicator in placeholder_indicators):
        return False, f"⚠️  {var_name}: Contains placeholder value"
    
    # Specific validations
    if var_name == "SLACK_BOT_TOKEN" and not value.startswith("xoxb-"):
        return False, f"⚠️  {var_name}: Should start with 'xoxb-'"
    
    if var_name == "SLACK_APP_TOKEN" and not value.startswith("xapp-"):
        return False, f"⚠️  {var_name}: Should start with 'xapp-'"
    
    if var_name == "DIGITALOCEAN_API_KEY" and not value.startswith("dop_"):
        return False, f"⚠️  {var_name}: Should start with 'dop_'"
    
    if var_name == "SECRET_KEY" and len(value) < 32:
        return False, f"⚠️  {var_name}: Should be at least 32 characters long"
    
    if var_name == "CORS_ORIGINS":
        origins = [o.strip() for o in value.split(",")]
        if len(origins) == 0:
            return False, f"⚠️  {var_name}: Should contain at least one origin"
        for origin in origins:
            if not origin.startswith("http://") and not origin.startswith("https://"):
                return False, f"⚠️  {var_name}: '{origin}' should start with http:// or https://"
    
    # If all checks pass, mask sensitive data in output
    masked_value = mask_value(var_name, value)
    return True, f"✅ {var_name}: {masked_value}"


def mask_value(var_name: str, value: str) -> str:
    """
    Mask sensitive values for display.
    """
    sensitive_vars = [
        "PASSWORD", "TOKEN", "SECRET", "KEY", "API_KEY"
    ]
    
    if any(sensitive in var_name.upper() for sensitive in sensitive_vars):
        if len(value) <= 8:
            return "***"
        return f"{value[:4]}...{value[-4:]}"
    
    return value


def main():
    """
    Main validation function.
    """
    print("\n" + "="*60)
    print("🔍 ENVIRONMENT VARIABLES VALIDATION")
    print("="*60 + "\n")
    
    errors: List[str] = []
    warnings: List[str] = []
    success: List[str] = []
    
    print("📋 Required Variables:")
    print("-" * 60)
    for var_name in REQUIRED_VARS:
        is_valid, message = validate_variable(var_name)
        print(message)
        
        if not is_valid:
            if "❌" in message:
                errors.append(message)
            else:
                warnings.append(message)
        else:
            success.append(message)
    
    print("\n📋 Optional Variables:")
    print("-" * 60)
    for var_name in OPTIONAL_VARS:
        value = os.getenv(var_name)
        if value:
            is_valid, message = validate_variable(var_name)
            print(message)
        else:
            print(f"ℹ️  {var_name}: Not set (optional)")
    
    # Summary
    print("\n" + "="*60)
    print("📊 VALIDATION SUMMARY")
    print("="*60)
    print(f"✅ Valid: {len(success)}")
    print(f"⚠️  Warnings: {len(warnings)}")
    print(f"❌ Errors: {len(errors)}")
    
    if errors:
        print("\n" + "="*60)
        print("❌ VALIDATION FAILED")
        print("="*60)
        print("\nPlease fix the following errors:")
        for error in errors:
            print(f"  {error}")
        print("\n💡 Tip: Check documentation/ENV_SETUP.md for instructions on how to get credentials")
        sys.exit(1)
    
    if warnings:
        print("\n" + "="*60)
        print("⚠️  VALIDATION PASSED WITH WARNINGS")
        print("="*60)
        print("\nPlease review the following warnings:")
        for warning in warnings:
            print(f"  {warning}")
        print("\n💡 The application may not work correctly with placeholder values")
        print("💡 Check documentation/ENV_SETUP.md for instructions on how to get real credentials")
        sys.exit(0)
    
    print("\n" + "="*60)
    print("✅ VALIDATION PASSED")
    print("="*60)
    print("\n🚀 All environment variables are properly configured!")
    print("You can now start the application with: docker-compose up\n")
    sys.exit(0)


if __name__ == "__main__":
    main()

