"""
Quick Start Setup for TruthfulQA Evaluation
Prepares the evaluation environment
"""

import os
from pathlib import Path
import subprocess


def setup_evaluation():
    """Setup evaluation environment"""
    
    print("\n" + "=" * 80)
    print("TruthfulQA Evaluation Setup")
    print("=" * 80 + "\n")
    
    # Create directories
    print("📁 Creating directories...")
    directories = [
        Path("data"),
        Path("data/annotations")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {directory}")
    
    # Check for TruthfulQA.csv
    print("\n📥 Checking for TruthfulQA dataset...")
    truthfulqa_path = Path("data/TruthfulQA.csv")
    
    if truthfulqa_path.exists():
        print(f"   ✓ Found: {truthfulqa_path}")
    else:
        print(f"   ⚠️  Not found: {truthfulqa_path}")
        print("\n   Please download TruthfulQA.csv:")
        print("   https://raw.githubusercontent.com/sylinrl/TruthfulQA/main/TruthfulQA.csv")
        print(f"\n   Save to: {truthfulqa_path.absolute()}")
        
        download = input("\n   Would you like to download it now? (y/n): ")
        if download.lower() == 'y':
            try:
                import urllib.request
                print("\n   Downloading...")
                url = "https://raw.githubusercontent.com/sylinrl/TruthfulQA/main/TruthfulQA.csv"
                urllib.request.urlretrieve(url, truthfulqa_path)
                print(f"   ✓ Downloaded to {truthfulqa_path}")
            except Exception as e:
                print(f"   ❌ Download failed: {e}")
                print("   Please download manually.")
                return False
    
    # Generate evaluation set
    print("\n🎲 Generating random 50-question evaluation set...")
    try:
        from truthfulqa_loader import TruthfulQALoader
        loader = TruthfulQALoader()
        output_path = loader.save_evaluation_set(num_questions=50, seed=42)
        print(f"   ✓ Saved to: {output_path}")
        
        # Show sample questions
        print("\n   📋 Sample Questions:")
        questions = loader.sample_questions(num_questions=3)
        for i, q in enumerate(questions, 1):
            print(f"\n   {i}. {q['question']}")
            print(f"      Category: {q['category']}")
    
    except Exception as e:
        print(f"   ❌ Failed to generate evaluation set: {e}")
        return False
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    required_packages = [
        'fastapi',
        'uvicorn',
        'pandas',
        'openai',
        'anthropic',
        'google-generativeai'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n   ⚠️  Missing packages: {', '.join(missing_packages)}")
        print(f"   Install with: pip install {' '.join(missing_packages)}")
    
    # Check API keys
    print("\n🔑 Checking API keys...")
    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
        'MISTRAL_API_KEY': os.getenv('MISTRAL_API_KEY')
    }
    
    for key_name, key_value in api_keys.items():
        if key_value:
            masked = key_value[:8] + "..." + key_value[-4:]
            print(f"   ✓ {key_name}: {masked}")
        else:
            print(f"   ✗ {key_name}: NOT SET")
    
    # Instructions
    print("\n" + "=" * 80)
    print("✅ Setup Complete!")
    print("=" * 80)
    
    print("\n📖 Next Steps:\n")
    print("1. Start the backend server:")
    print("   cd backend")
    print("   python app.py")
    print()
    print("2. Open frontend in browser:")
    print("   http://localhost:8001/static/index.html")
    print()
    print("3. Start annotation workflow:")
    print("   - Load questions from: data/evaluation_set_50.csv")
    print("   - Annotate claims for each model")
    print("   - Save and calculate metrics")
    print()
    print("4. Check progress anytime:")
    print("   python generate_report.py --progress")
    print()
    print("5. Generate final report:")
    print("   python generate_report.py")
    print()
    print("📚 Full guide: EVALUATION_GUIDE.md")
    print()
    
    return True


if __name__ == "__main__":
    setup_evaluation()
