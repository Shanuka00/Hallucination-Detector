"""
Setup script for Hallucination Detection System
Helps users configure their environment and API keys
"""

import os
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    template_file = Path("../.env.template")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if template_file.exists():
        shutil.copy(template_file, env_file)
        print("📄 Created .env file from template")
        print("   Please edit .env file and add your API keys")
        return True
    else:
        # Create a basic .env file
        with open(".env", "w") as f:
            f.write("""# Hallucination Detection System Configuration
USE_SIMULATION=true
WIKIPEDIA_USE_SIMULATION=true
DEBUG_MODE=true

# API Keys (add your actual keys here)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
""")
        print("📄 Created basic .env file")
        print("   Please edit .env file and add your API keys")
        return True

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n🔍 Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import pydantic
        import networkx
        import requests
        from dotenv import load_dotenv
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("   Run: pip install -r requirements.txt")
        return False

def validate_configuration():
    """Validate the current configuration"""
    print("\n⚙️  Validating configuration...")
    
    from config import config
    
    # The config will automatically print status in debug mode
    
    if config.USE_SIMULATION:
        print("✅ Running in simulation mode - no API keys required")
        return True
    else:
        api_keys = config.validate_api_keys()
        if any(api_keys.values()):
            print("✅ At least one API key is configured")
            return True
        else:
            print("❌ No API keys found and simulation mode is disabled")
            print("   Either enable simulation mode or add API keys to .env")
            return False

def run_demo():
    """Run the enhanced demo to test the system"""
    print("\n🚀 Running system demo...")
    
    try:
        from enhanced_demo import run_enhanced_demo
        result = run_enhanced_demo()
        print("✅ Demo completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🧠 Hallucination Detection System Setup")
    print("=" * 50)
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Create .env file
    if create_env_file():
        success_count += 1
    
    # Step 2: Check dependencies
    if check_dependencies():
        success_count += 1
    
    # Step 3: Validate configuration
    if validate_configuration():
        success_count += 1
    
    # Step 4: Run demo
    if run_demo():
        success_count += 1
    
    print(f"\n📊 Setup Summary: {success_count}/{total_steps} steps completed")
    
    if success_count == total_steps:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("   1. Start the server: py -m uvicorn app:app --reload --host 0.0.0.0 --port 8000")
        print("   2. Open: http://localhost:8000/static/index.html")
        print("   3. To use real APIs: Edit .env file and set USE_SIMULATION=false")
    else:
        print("⚠️  Setup incomplete. Please resolve the issues above.")
        
        if not os.path.exists(".env"):
            print("\n💡 Quick fix:")
            print("   1. Copy .env.template to .env")
            print("   2. Edit .env and add your API keys (or keep USE_SIMULATION=true)")

if __name__ == "__main__":
    main()
