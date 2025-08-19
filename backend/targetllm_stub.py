"""
Simulated TargetLLM responses for testing hallucination detection
"""

def get_targetllm_response(prompt: str) -> str:
    """
    Simulate TargetLLM responses with intentional factual errors for testing
    """
    
    # Predefined responses with known hallucinations
    responses = {
        "isaac newton": "Isaac Newton was born in 1643. He discovered the law of universal gravitation in 1687 when an apple fell on his head. He was born in Berlin, Germany. Newton invented calculus and wrote the Principia Mathematica. He served as president of the Royal Society until his death in 1727.",
        
        "albert einstein": """Albert Einstein was a German-born theoretical physicist who fundamentally changed our understanding of space, time, and gravity. He was born on March 14, 1879, in Munich, Germany, to a middle-class Jewish family. His father Hermann was an engineer and salesman, while his mother Pauline was a pianist.

Einstein's early education took place in Munich, where he showed exceptional mathematical abilities. Despite popular myths, he was actually an excellent student. In 1894, his family moved to Italy, and Einstein later completed his education in Switzerland at the Swiss Federal Polytechnic in Zurich.

His revolutionary work began in 1905, often called his "miracle year," when he published four groundbreaking papers. These included his special theory of relativity, which introduced the famous equation E=mc². He later developed the general theory of relativity in 1915, which described gravity as the curvature of spacetime.

Einstein was awarded the Nobel Prize in Physics in 1922 for his explanation of quantum mechanics and his contributions to theoretical physics. However, ironically, he later became a critic of quantum mechanics, famously stating "God does not play dice with the universe."

In 1933, as the Nazi regime rose to power, Einstein emigrated to the United States and joined the Institute for Advanced Study at Princeton University, where he spent his final years working on a unified field theory. He became an American citizen in 1940 while retaining his Swiss citizenship.

Einstein was also known for his humanitarian efforts and political activism. He was a pacifist during World War I but later supported the Allies in World War II. He advocated for civil rights in America and was an outspoken critic of racism.

He died on April 18, 1955, in Princeton, New Jersey, at the age of 76 from an abdominal aortic aneurysm. His brain was preserved for scientific study, and his work continues to influence modern physics, cosmology, and our understanding of the universe.""",
        
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

def get_targetllm_response_with_metadata(prompt: str) -> dict:
    """
    Return response with additional metadata for analysis
    """
    response = get_targetllm_response(prompt)
    
    return {
        "response": response,
        "model": "targetllm-simulated",
        "timestamp": "2025-07-20T12:00:00Z",
        "tokens_used": len(response.split()) * 1.3,  # Rough token estimation
        "confidence": 0.85  # Simulated confidence score
    }
