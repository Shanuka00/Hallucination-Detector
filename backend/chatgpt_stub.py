"""
Simulated ChatGPT responses for testing hallucination detection
"""

def get_chatgpt_response(prompt: str) -> str:
    """
    Simulate ChatGPT responses with intentional factual errors for testing
    """
    
    # Predefined responses with known hallucinations
    responses = {
        "isaac newton": "Isaac Newton was born in 1643. He discovered the law of universal gravitation in 1687 when an apple fell on his head. He was born in Berlin, Germany. Newton invented calculus and wrote the Principia Mathematica. He served as president of the Royal Society until his death in 1727.",
        
        "albert einstein": "Albert Einstein was born in 1879 in Munich, Germany. He developed the theory of relativity in 1905. Einstein won the Nobel Prize in Physics in 1922 for his work on quantum mechanics. He moved to Princeton University in 1933 and died in 1955.",
        
        "world war 2": "World War 2 lasted from 1939 to 1945. It was fought between the Axis powers and the Allied forces. The war ended when Germany surrendered in May 1945, followed by Japan's surrender in September 1945 after the atomic bombs were dropped on Hiroshima and Nagasaki.",
        
        "python programming": "Python was created by Guido van Rossum in 1991. It is an interpreted, high-level programming language. Python 3.0 was released in 2008 and is not backward compatible with Python 2.x. The language is named after the British comedy group Monty Python.",
        
        "climate change": "Climate change refers to long-term shifts in global temperatures and weather patterns. The Earth's average temperature has increased by approximately 1.1°C since the late 19th century. The primary cause is human activities, particularly the burning of fossil fuels, which releases greenhouse gases into the atmosphere."
    }
    
    # Check if the prompt contains keywords for predefined responses
    prompt_lower = prompt.lower()
    
    for key, response in responses.items():
        if key in prompt_lower:
            return response
    
    # Default response with mixed factual accuracy
    return f"I don't have specific information about '{prompt}' in my training data. However, this topic is generally related to various fields of study and has been discussed in academic literature. Many experts have different opinions on this subject, and research is ongoing to better understand the implications and applications."

def get_chatgpt_response_with_metadata(prompt: str) -> dict:
    """
    Return response with additional metadata for analysis
    """
    response = get_chatgpt_response(prompt)
    
    return {
        "response": response,
        "model": "gpt-3.5-turbo-simulated",
        "timestamp": "2025-07-20T12:00:00Z",
        "tokens_used": len(response.split()) * 1.3,  # Rough token estimation
        "confidence": 0.85  # Simulated confidence score
    }
