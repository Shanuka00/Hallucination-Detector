"""
Configuration file for Hallucination Detection System
Controls API modes and service settings
Loads sensitive data from .env file
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the hallucination detection system"""
    
    # API Mode Settings (can be overridden by .env file)
    USE_SIMULATION = os.getenv("USE_SIMULATION", "true").lower() == "true"
    
    # LLM Service Configuration
    LLM_PROVIDER_FOR_EXTRACTION = os.getenv("LLM_PROVIDER_FOR_EXTRACTION", "LLM1")
    
    # API Keys (loaded from environment variables)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    
    # Wikipedia Service Settings
    WIKIPEDIA_ENABLED = os.getenv("WIKIPEDIA_ENABLED", "true").lower() == "true"
    WIKIPEDIA_USE_SIMULATION = os.getenv("WIKIPEDIA_USE_SIMULATION", "true").lower() == "true"
    WIKIPEDIA_TIMEOUT = int(os.getenv("WIKIPEDIA_TIMEOUT", "10"))
    
    # Risk Assessment Settings
    WIKIPEDIA_CHECK_THRESHOLD = os.getenv("WIKIPEDIA_CHECK_THRESHOLD", "medium")
    BATCH_PROCESSING_ENABLED = os.getenv("BATCH_PROCESSING_ENABLED", "true").lower() == "true"
    MAX_CLAIMS_PER_BATCH = int(os.getenv("MAX_CLAIMS_PER_BATCH", "10"))
    
    # Performance Settings
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    # Debug Settings
    DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_api_settings(cls) -> Dict[str, Any]:
        """Get API-related settings"""
        return {
            "use_simulation": cls.USE_SIMULATION,
            "openai_key": cls.OPENAI_API_KEY,
            "anthropic_key": cls.ANTHROPIC_API_KEY,
            "google_key": cls.GOOGLE_API_KEY,
            "timeout": cls.REQUEST_TIMEOUT,
            "max_retries": cls.MAX_RETRIES
        }
    
    @classmethod
    def get_wikipedia_settings(cls) -> Dict[str, Any]:
        """Get Wikipedia service settings"""
        return {
            "enabled": cls.WIKIPEDIA_ENABLED,
            "use_simulation": cls.WIKIPEDIA_USE_SIMULATION,
            "timeout": cls.WIKIPEDIA_TIMEOUT,
            "check_threshold": cls.WIKIPEDIA_CHECK_THRESHOLD
        }
    
    @classmethod
    def toggle_simulation_mode(cls, use_simulation: bool):
        """Toggle between simulation and real API modes"""
        cls.USE_SIMULATION = use_simulation
        cls.WIKIPEDIA_USE_SIMULATION = use_simulation
        print(f"Switched to {'simulation' if use_simulation else 'real API'} mode")
    
    @classmethod
    def validate_api_keys(cls) -> Dict[str, bool]:
        """Check if required API keys are available"""
        return {
            "openai": bool(cls.OPENAI_API_KEY),
            "anthropic": bool(cls.ANTHROPIC_API_KEY),
            "google": bool(cls.GOOGLE_API_KEY)
        }
    
    @classmethod
    def print_config_status(cls):
        """Print current configuration status"""
        print("\n🔧 Configuration Status:")
        print(f"   Simulation Mode: {cls.USE_SIMULATION}")
        print(f"   Wikipedia Simulation: {cls.WIKIPEDIA_USE_SIMULATION}")
        print(f"   Debug Mode: {cls.DEBUG_MODE}")
        
        api_keys = cls.validate_api_keys()
        print("\n🔑 API Keys Status:")
        for service, available in api_keys.items():
            status = "✅ Available" if available else "❌ Missing"
            print(f"   {service.capitalize()}: {status}")
        
        if not cls.USE_SIMULATION and not any(api_keys.values()):
            print("\n⚠️  Warning: No API keys found but simulation mode is disabled!")
            print("   Either enable simulation mode or add API keys to .env file")
    
    @classmethod
    def load_from_env_file(cls, env_path: str = ".env"):
        """Manually load configuration from a specific .env file"""
        from dotenv import load_dotenv
        load_dotenv(env_path)
        
        # Reload all configuration values
        cls.USE_SIMULATION = os.getenv("USE_SIMULATION", "true").lower() == "true"
        cls.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        cls.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
        cls.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
        cls.DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"
        
        print(f"✅ Configuration reloaded from {env_path}")

# Global configuration instance
config = Config()

# Print config status on import (only in debug mode)
if config.DEBUG_MODE:
    config.print_config_status()
