"""
TruthfulQA Dataset Loader
Handles loading and sampling questions from TruthfulQA benchmark
"""

import pandas as pd
import random
from pathlib import Path
from typing import List, Dict


class TruthfulQALoader:
    def __init__(self, csv_path: str = "data/TruthfulQA.csv"):
        """
        Initialize TruthfulQA loader
        
        Args:
            csv_path: Path to TruthfulQA.csv file
        """
        self.csv_path = Path(csv_path)
        self.df = None
        
    def load_dataset(self) -> pd.DataFrame:
        """Load the full TruthfulQA dataset"""
        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"TruthfulQA.csv not found at {self.csv_path}. "
                "Please download from: https://github.com/sylinrl/TruthfulQA"
            )
        
        self.df = pd.read_csv(self.csv_path)
        return self.df
    
    def sample_questions(self, num_questions: int = 50, seed: int = 42) -> List[Dict]:
        """
        Sample random questions from TruthfulQA
        
        Args:
            num_questions: Number of questions to sample
            seed: Random seed for reproducibility
            
        Returns:
            List of question dictionaries
        """
        if self.df is None:
            self.load_dataset()
        
        random.seed(seed)
        sample_df = self.df.sample(n=num_questions, random_state=seed)
        
        questions = []
        for idx, row in sample_df.iterrows():
            questions.append({
                'question_id': f"Q{idx}",
                'question': row['Question'],
                'best_answer': row.get('Best Answer', ''),
                'correct_answers': row.get('Correct Answers', ''),
                'incorrect_answers': row.get('Incorrect Answers', ''),
                'category': row.get('Category', 'General'),
                'source': row.get('Source', '')
            })
        
        return questions
    
    def save_evaluation_set(self, num_questions: int = 50, seed: int = 42):
        """
        Save sampled questions to CSV for reproducibility
        
        Args:
            num_questions: Number of questions to sample
            seed: Random seed
            
        Returns:
            Path to saved file
        """
        questions = self.sample_questions(num_questions, seed)
        
        output_dir = Path("data")
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / f"evaluation_set_{num_questions}.csv"
        pd.DataFrame(questions).to_csv(output_path, index=False)
        
        print(f"✓ Saved {num_questions} questions to {output_path}")
        return output_path
    
    def get_question_by_id(self, question_id: str) -> Dict:
        """Get a specific question by ID"""
        questions = self.sample_questions()
        for q in questions:
            if q['question_id'] == question_id:
                return q
        return None


if __name__ == "__main__":
    # Test the loader
    loader = TruthfulQALoader()
    
    # Save evaluation set
    output_path = loader.save_evaluation_set(num_questions=50, seed=42)
    
    # Load and display sample
    questions = loader.sample_questions(num_questions=5)
    
    print("\n=== Sample Questions ===\n")
    for q in questions:
        print(f"ID: {q['question_id']}")
        print(f"Q: {q['question']}")
        print(f"Category: {q['category']}")
        print(f"Best Answer: {q['best_answer'][:100]}...")
        print("-" * 80)
