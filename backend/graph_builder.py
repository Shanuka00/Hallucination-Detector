"""
Build hallucination graph using NetworkX for visualization
"""

import networkx as nx
from typing import List, Dict, Any
from models import ClaimVerification

def build_hallucination_graph(claims: List[ClaimVerification]) -> Dict[str, Any]:
    """
    Build a graph representation of claims and their verification status
    """
    G = nx.Graph()
    
    # Add nodes for each claim
    nodes = []
    edges = []
    
    for claim in claims:
        risk_level = claim.get_risk_level()
        confidence = claim.get_confidence_score()
        
        # Color coding based on risk level
        color_map = {
            "low": "#4CAF50",      # Green
            "medium": "#FF9800",   # Orange
            "high": "#F44336"      # Red
        }
        
        node = {
            "id": claim.id,
            "label": f"{claim.id}: {claim.claim[:50]}{'...' if len(claim.claim) > 50 else ''}",
            "title": claim.claim,  # Full text for tooltip
            "color": color_map[risk_level],
            "size": 20 + (confidence * 20),  # Size based on confidence
            "risk_level": risk_level,
            "confidence": confidence,
            "claude_response": claim.claude_verification,
            "gemini_response": claim.gemini_verification
        }
        nodes.append(node)
        G.add_node(claim.id, **node)
    
    # Add edges between claims based on verification agreement
    for i, claim1 in enumerate(claims):
        for j, claim2 in enumerate(claims[i+1:], i+1):
            # Calculate agreement score between two claims
            agreement_score = calculate_agreement(claim1, claim2)
            
            if agreement_score > 0.3:  # Only add edges for significant relationships
                edge_color = "#4CAF50" if agreement_score > 0.7 else "#FF9800"
                edge = {
                    "from": claim1.id,
                    "to": claim2.id,
                    "width": agreement_score * 5,
                    "color": edge_color,
                    "title": f"Agreement: {agreement_score:.2f}"
                }
                edges.append(edge)
                G.add_edge(claim1.id, claim2.id, weight=agreement_score, **edge)
    
    # Add verifier nodes
    verifier_nodes = [
        {
            "id": "claude",
            "label": "Claude",
            "color": "#9C27B0",  # Purple
            "size": 30,
            "shape": "box",
            "font": {"color": "white"}
        },
        {
            "id": "gemini",
            "label": "Gemini",
            "color": "#2196F3",  # Blue
            "size": 30,
            "shape": "box",
            "font": {"color": "white"}
        }
    ]
    
    # Add edges from verifiers to claims
    verifier_edges = []
    for claim in claims:
        # Claude connections
        claude_color = get_verification_color(claim.claude_verification)
        claude_edge = {
            "from": "claude",
            "to": claim.id,
            "color": claude_color,
            "dashes": True,
            "title": f"Claude: {claim.claude_verification}"
        }
        verifier_edges.append(claude_edge)
        
        # Gemini connections
        gemini_color = get_verification_color(claim.gemini_verification)
        gemini_edge = {
            "from": "gemini",
            "to": claim.id,
            "color": gemini_color,
            "dashes": True,
            "title": f"Gemini: {claim.gemini_verification}"
        }
        verifier_edges.append(gemini_edge)
    
    # Calculate graph metrics
    metrics = calculate_graph_metrics(G, claims)
    
    return {
        "nodes": nodes + verifier_nodes,
        "edges": edges + verifier_edges,
        "metrics": metrics,
        "layout": "force-directed",
        "physics": {
            "enabled": True,
            "stabilization": {"iterations": 100}
        }
    }

def calculate_agreement(claim1: ClaimVerification, claim2: ClaimVerification) -> float:
    """
    Calculate agreement score between two claims based on verifier responses
    """
    # Compare Claude responses
    claude_agreement = 1.0 if claim1.claude_verification == claim2.claude_verification else 0.0
    
    # Compare Gemini responses
    gemini_agreement = 1.0 if claim1.gemini_verification == claim2.gemini_verification else 0.0
    
    # Overall agreement is average
    overall_agreement = (claude_agreement + gemini_agreement) / 2.0
    
    # Bonus for both being high confidence (both "Yes")
    if (claim1.claude_verification == "Yes" and claim1.gemini_verification == "Yes" and
        claim2.claude_verification == "Yes" and claim2.gemini_verification == "Yes"):
        overall_agreement = min(1.0, overall_agreement + 0.2)
    
    return overall_agreement

def get_verification_color(response: str) -> str:
    """
    Get color for verification response
    """
    color_map = {
        "Yes": "#4CAF50",      # Green
        "No": "#F44336",       # Red
        "Uncertain": "#FF9800" # Orange
    }
    return color_map.get(response, "#9E9E9E")  # Gray for unknown

def calculate_graph_metrics(G: nx.Graph, claims: List[ClaimVerification]) -> Dict[str, Any]:
    """
    Calculate various graph metrics for analysis
    """
    claim_nodes = [claim.id for claim in claims]
    subgraph = G.subgraph(claim_nodes)
    
    metrics = {
        "total_claims": len(claims),
        "connected_components": nx.number_connected_components(subgraph),
        "average_clustering": nx.average_clustering(subgraph) if len(claim_nodes) > 0 else 0,
        "density": nx.density(subgraph),
    }
    
    # Risk distribution
    risk_distribution = {"high": 0, "medium": 0, "low": 0}
    confidence_sum = 0
    
    for claim in claims:
        risk_level = claim.get_risk_level()
        risk_distribution[risk_level] += 1
        confidence_sum += claim.get_confidence_score()
    
    metrics["risk_distribution"] = risk_distribution
    metrics["average_confidence"] = confidence_sum / len(claims) if claims else 0
    
    # Overall hallucination risk assessment
    total_claims = len(claims)
    if total_claims > 0:
        risk_score = (
            risk_distribution["high"] * 1.0 +
            risk_distribution["medium"] * 0.5 +
            risk_distribution["low"] * 0.1
        ) / total_claims
        metrics["overall_risk_score"] = risk_score
        
        if risk_score > 0.7:
            metrics["risk_assessment"] = "High Risk"
        elif risk_score > 0.4:
            metrics["risk_assessment"] = "Medium Risk"
        else:
            metrics["risk_assessment"] = "Low Risk"
    else:
        metrics["overall_risk_score"] = 0
        metrics["risk_assessment"] = "No Claims"
    
    return metrics

def export_graph_data_for_cytoscape(claims: List[ClaimVerification]) -> Dict[str, Any]:
    """
    Export graph data in Cytoscape.js format for web visualization
    """
    elements = []
    
    # Add claim nodes
    for claim in claims:
        risk_level = claim.get_risk_level()
        color_map = {
            "low": "#4CAF50",
            "medium": "#FF9800", 
            "high": "#F44336"
        }
        
        elements.append({
            "data": {
                "id": claim.id,
                "label": claim.id,
                "claim_text": claim.claim,
                "risk_level": risk_level,
                "confidence": claim.get_confidence_score(),
                "claude_response": claim.claude_verification,
                "gemini_response": claim.gemini_verification
            },
            "style": {
                "background-color": color_map[risk_level],
                "width": 30,
                "height": 30
            }
        })
    
    return {"elements": elements}
