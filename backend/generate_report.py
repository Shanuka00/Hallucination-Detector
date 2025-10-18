"""
Generate Final Evaluation Report from Manual Annotations
CLI tool to aggregate results and create comparison tables
"""

import sys
from pathlib import Path
import pandas as pd
from metrics_calculator import MetricsCalculator


def generate_report(models=None, annotations_dir=None):
    """
    Generate comprehensive evaluation report
    
    Args:
        models: List of model names to include (default: all 5 models)
        annotations_dir: Directory containing annotations
    """
    if models is None:
        models = ["mistral", "openai", "anthropic", "gemini", "deepseek"]
    
    if annotations_dir is None:
        annotations_dir = Path("data/annotations")
    
    if not annotations_dir.exists():
        print(f"❌ Annotations directory not found: {annotations_dir}")
        return
    
    print("\n" + "=" * 80)
    print("TruthfulQA Evaluation Report - Manual Annotation")
    print("=" * 80 + "\n")
    
    # Collect results for all models
    results = []
    for model in models:
        print(f"📊 Processing model: {model.upper()}...")
        metrics = MetricsCalculator.aggregate_metrics(model, annotations_dir)
        
        if 'error' in metrics:
            print(f"   ⚠️  {metrics['error']}")
            continue
        
        results.append(metrics)
        print(f"   ✓ Found {metrics['num_questions']} annotated questions")
    
    if not results:
        print("\n❌ No results found for any model.")
        print("Please ensure annotations are saved in: data/annotations/")
        return
    
    print("\n" + "-" * 80)
    print("MICRO-AVERAGED METRICS (Aggregated Confusion Matrix)")
    print("-" * 80 + "\n")
    
    # Create micro-averaged results table
    micro_data = []
    for r in results:
        micro_data.append({
            'Model': r['model'].upper(),
            'Questions': r['num_questions'],
            'Total Claims': r['total_claims'],
            'Precision': r['micro_averaged']['precision'],
            'Recall': r['micro_averaged']['recall'],
            'F1-Score': r['micro_averaged']['f1_score'],
            'Accuracy': r['micro_averaged']['accuracy']
        })
    
    df_micro = pd.DataFrame(micro_data)
    print(df_micro.to_string(index=False))
    
    print("\n" + "-" * 80)
    print("MACRO-AVERAGED METRICS (Average Per-Question Performance)")
    print("-" * 80 + "\n")
    
    # Create macro-averaged results table
    macro_data = []
    for r in results:
        macro_data.append({
            'Model': r['model'].upper(),
            'Questions': r['num_questions'],
            'Precision': r['macro_averaged']['precision'],
            'Recall': r['macro_averaged']['recall'],
            'F1-Score': r['macro_averaged']['f1_score'],
            'Accuracy': r['macro_averaged']['accuracy']
        })
    
    df_macro = pd.DataFrame(macro_data)
    print(df_macro.to_string(index=False))
    
    print("\n" + "-" * 80)
    print("CONFUSION MATRIX TOTALS")
    print("-" * 80 + "\n")
    
    # Create confusion matrix table
    cm_data = []
    for r in results:
        cm = r['confusion_matrix']
        cm_data.append({
            'Model': r['model'].upper(),
            'TP': cm['tp'],
            'FP': cm['fp'],
            'TN': cm['tn'],
            'FN': cm['fn'],
            'Total': cm['tp'] + cm['fp'] + cm['tn'] + cm['fn']
        })
    
    df_cm = pd.DataFrame(cm_data)
    print(df_cm.to_string(index=False))
    
    # Summary statistics
    total_questions = sum(r['num_questions'] for r in results)
    total_claims = sum(r['total_claims'] for r in results)
    avg_micro_f1 = sum(r['micro_averaged']['f1_score'] for r in results) / len(results)
    avg_macro_f1 = sum(r['macro_averaged']['f1_score'] for r in results) / len(results)
    
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80 + "\n")
    print(f"Total Models Evaluated: {len(results)}")
    print(f"Total Questions Annotated: {total_questions} (Target: {len(models) * 50})")
    print(f"Total Claims Annotated: {total_claims}")
    print(f"Average Micro F1-Score: {avg_micro_f1:.4f}")
    print(f"Average Macro F1-Score: {avg_macro_f1:.4f}")
    print(f"\nCompletion Rate: {(total_questions / (len(models) * 50)) * 100:.1f}%")
    
    # Best performing model
    best_model = max(results, key=lambda x: x['micro_averaged']['f1_score'])
    print(f"\n🏆 Best Performing Model: {best_model['model'].upper()}")
    print(f"   F1-Score: {best_model['micro_averaged']['f1_score']:.4f}")
    print(f"   Precision: {best_model['micro_averaged']['precision']:.4f}")
    print(f"   Recall: {best_model['micro_averaged']['recall']:.4f}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Save to CSV
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    csv_micro = output_dir / "truthfulqa_results_micro.csv"
    csv_macro = output_dir / "truthfulqa_results_macro.csv"
    csv_cm = output_dir / "truthfulqa_confusion_matrix.csv"
    
    df_micro.to_csv(csv_micro, index=False)
    df_macro.to_csv(csv_macro, index=False)
    df_cm.to_csv(csv_cm, index=False)
    
    print(f"📁 Results saved to:")
    print(f"   • {csv_micro}")
    print(f"   • {csv_macro}")
    print(f"   • {csv_cm}")
    print()


def check_progress(annotations_dir=None):
    """
    Check annotation progress for each model
    """
    if annotations_dir is None:
        annotations_dir = Path("data/annotations")
    
    if not annotations_dir.exists():
        print(f"❌ Annotations directory not found: {annotations_dir}")
        return
    
    models = ["mistral", "openai", "anthropic", "gemini", "deepseek"]
    
    print("\n" + "=" * 80)
    print("ANNOTATION PROGRESS")
    print("=" * 80 + "\n")
    
    total_completed = 0
    
    for model in models:
        # Count unique question IDs
        pattern = f"{model}_*_metrics.json"
        metrics_files = list(annotations_dir.glob(pattern))
        
        question_ids = set()
        for f in metrics_files:
            parts = f.stem.split('_')
            if len(parts) >= 2:
                question_ids.add(parts[1])
        
        completed = len(question_ids)
        total_completed += completed
        percentage = (completed / 50) * 100
        
        bar_length = 30
        filled = int(bar_length * completed / 50)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"{model.upper():<12} [{bar}] {completed:>2}/50 ({percentage:>5.1f}%)")
    
    total_required = 50 * len(models)
    overall_percentage = (total_completed / total_required) * 100
    
    print("\n" + "-" * 80)
    print(f"Overall Progress: {total_completed}/{total_required} ({overall_percentage:.1f}%)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate TruthfulQA evaluation report')
    parser.add_argument('--progress', action='store_true', 
                       help='Show annotation progress')
    parser.add_argument('--models', nargs='+', 
                       default=["mistral", "openai", "anthropic", "gemini", "deepseek"],
                       help='Models to include in report')
    parser.add_argument('--annotations-dir', type=str, 
                       default='data/annotations',
                       help='Directory containing annotations')
    
    args = parser.parse_args()
    
    annotations_dir = Path(args.annotations_dir)
    
    if args.progress:
        check_progress(annotations_dir)
    else:
        generate_report(args.models, annotations_dir)
