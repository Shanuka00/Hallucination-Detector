"""
Metrics Calculator for Manual Annotation Evaluation
Calculates precision, recall, F1-score, accuracy
"""

from typing import Dict, List
from pathlib import Path
import json
from datetime import datetime


class MetricsCalculator:
    """Calculate classification metrics for manual annotations"""
    
    @staticmethod
    def calculate_metrics(annotations: Dict[str, str], 
                         predictions: Dict[str, Dict]) -> Dict:
        """
        Calculate precision, recall, F1, accuracy from annotations
        
        Args:
            annotations: {claim_id: 'correct' or 'incorrect'}
            predictions: {claim_id: {'final_verdict': 'Yes/No/Uncertain', ...}}
            
        Returns:
            Dictionary with metrics
        """
        # Initialize confusion matrix
        tp = 0  # True Positive: System verified, Manual correct
        fp = 0  # False Positive: System verified, Manual incorrect
        tn = 0  # True Negative: System flagged, Manual incorrect
        fn = 0  # False Negative: System flagged, Manual correct
        
        for claim_id, manual_label in annotations.items():
            if claim_id not in predictions:
                continue
                
            system_verdict = predictions[claim_id]['final_verdict']
            
            # Map verdicts to binary
            system_says_verified = (system_verdict == 'Yes')
            manual_says_correct = (manual_label == 'correct')
            
            if system_says_verified and manual_says_correct:
                tp += 1
            elif system_says_verified and not manual_says_correct:
                fp += 1
            elif not system_says_verified and not manual_says_correct:
                tn += 1
            elif not system_says_verified and manual_says_correct:
                fn += 1
        
        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = (2 * precision * recall / (precision + recall) 
                   if (precision + recall) > 0 else 0.0)
        accuracy = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0.0
        
        return {
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1_score, 4),
            'accuracy': round(accuracy, 4),
            'confusion_matrix': {
                'tp': tp,
                'fp': fp,
                'tn': tn,
                'fn': fn,
                'total': tp + fp + tn + fn
            }
        }
    
    @staticmethod
    def aggregate_metrics(model_name: str, annotations_dir: Path = None) -> Dict:
        """
        Aggregate metrics across all questions for a model
        
        Args:
            model_name: Name of the target model
            annotations_dir: Directory containing annotation files
            
        Returns:
            Aggregated metrics dictionary
        """
        if annotations_dir is None:
            annotations_dir = Path("data/annotations")
        
        if not annotations_dir.exists():
            return {"error": "No annotations directory found"}
        
        # Find all metrics files for this model
        pattern = f"{model_name}_*_metrics.json"
        metrics_files = list(annotations_dir.glob(pattern))
        
        if not metrics_files:
            return {"error": f"No metrics found for model: {model_name}"}
        
        # Collect all metrics
        all_metrics = []
        total_tp = 0
        total_fp = 0
        total_tn = 0
        total_fn = 0
        
        for metrics_file in metrics_files:
            with open(metrics_file, 'r') as f:
                data = json.load(f)
                metrics = data['metrics']
                all_metrics.append(metrics)
                
                # Aggregate confusion matrix
                cm = metrics['confusion_matrix']
                total_tp += cm['tp']
                total_fp += cm['fp']
                total_tn += cm['tn']
                total_fn += cm['fn']
        
        # Calculate micro-averaged metrics (based on aggregated confusion matrix)
        micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        micro_f1 = (2 * micro_precision * micro_recall / (micro_precision + micro_recall)
                   if (micro_precision + micro_recall) > 0 else 0.0)
        micro_accuracy = ((total_tp + total_tn) / (total_tp + total_fp + total_tn + total_fn)
                         if (total_tp + total_fp + total_tn + total_fn) > 0 else 0.0)
        
        # Calculate macro-averaged metrics (average of per-question metrics)
        macro_precision = sum(m['precision'] for m in all_metrics) / len(all_metrics)
        macro_recall = sum(m['recall'] for m in all_metrics) / len(all_metrics)
        macro_f1 = sum(m['f1_score'] for m in all_metrics) / len(all_metrics)
        macro_accuracy = sum(m['accuracy'] for m in all_metrics) / len(all_metrics)
        
        return {
            'model': model_name,
            'num_questions': len(all_metrics),
            'total_claims': total_tp + total_fp + total_tn + total_fn,
            'micro_averaged': {
                'precision': round(micro_precision, 4),
                'recall': round(micro_recall, 4),
                'f1_score': round(micro_f1, 4),
                'accuracy': round(micro_accuracy, 4)
            },
            'macro_averaged': {
                'precision': round(macro_precision, 4),
                'recall': round(macro_recall, 4),
                'f1_score': round(macro_f1, 4),
                'accuracy': round(macro_accuracy, 4)
            },
            'confusion_matrix': {
                'tp': total_tp,
                'fp': total_fp,
                'tn': total_tn,
                'fn': total_fn
            }
        }
    
    @staticmethod
    def generate_comparison_report(models: List[str], annotations_dir: Path = None) -> str:
        """
        Generate comparison report for multiple models
        
        Args:
            models: List of model names
            annotations_dir: Directory containing annotations
            
        Returns:
            Formatted report string
        """
        if annotations_dir is None:
            annotations_dir = Path("data/annotations")
        
        results = []
        for model in models:
            metrics = MetricsCalculator.aggregate_metrics(model, annotations_dir)
            if 'error' not in metrics:
                results.append(metrics)
        
        if not results:
            return "No results found for any model."
        
        # Generate report
        report = "\n" + "=" * 80 + "\n"
        report += "TruthfulQA Evaluation Results - Manual Annotation\n"
        report += "=" * 80 + "\n\n"
        
        # Table header
        report += f"{'Model':<15} {'Questions':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Accuracy':<12}\n"
        report += "-" * 80 + "\n"
        
        # Table rows
        for r in results:
            model = r['model']
            questions = r['num_questions']
            metrics = r['micro_averaged']
            report += f"{model:<15} {questions:<12} "
            report += f"{metrics['precision']:<12.4f} {metrics['recall']:<12.4f} "
            report += f"{metrics['f1_score']:<12.4f} {metrics['accuracy']:<12.4f}\n"
        
        # Summary statistics
        total_questions = sum(r['num_questions'] for r in results)
        total_claims = sum(r['total_claims'] for r in results)
        avg_f1 = sum(r['micro_averaged']['f1_score'] for r in results) / len(results)
        
        report += "-" * 80 + "\n"
        report += f"\nTotal Questions Evaluated: {total_questions}\n"
        report += f"Total Claims Annotated: {total_claims}\n"
        report += f"Average F1-Score: {avg_f1:.4f}\n"
        report += f"Evaluation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "\n" + "=" * 80 + "\n"
        
        return report


if __name__ == "__main__":
    # Example usage
    calculator = MetricsCalculator()
    
    # Test metrics calculation
    annotations = {
        'claim_1': 'correct',
        'claim_2': 'incorrect',
        'claim_3': 'correct',
        'claim_4': 'incorrect',
        'claim_5': 'correct'
    }
    
    predictions = {
        'claim_1': {'final_verdict': 'Yes'},
        'claim_2': {'final_verdict': 'No'},
        'claim_3': {'final_verdict': 'Yes'},
        'claim_4': {'final_verdict': 'Uncertain'},
        'claim_5': {'final_verdict': 'Uncertain'}
    }
    
    metrics = calculator.calculate_metrics(annotations, predictions)
    print("\n=== Test Metrics ===")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1-Score: {metrics['f1_score']:.4f}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Confusion Matrix: {metrics['confusion_matrix']}")
