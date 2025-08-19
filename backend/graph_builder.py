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
            "llm1_response": claim.llm1_verification,
            "llm2_response": claim.llm2_verification,
            "wikipedia_checked": claim.is_wikipedia_checked,
            "wikipedia_status": claim.wikipedia_status if claim.is_wikipedia_checked else None,
            "wikipedia_summary": claim.wikipedia_summary if claim.is_wikipedia_checked else None
        }
        
        # Add Wikipedia badge if checked
        if claim.is_wikipedia_checked:
            node["borderWidth"] = 3
            node["borderColor"] = "#2196F3"  # Blue border for Wikipedia-checked claims
            # Add a special icon/symbol in the label instead of using circularImage
            node["label"] = f"📖 {claim.id}: {claim.claim[:45]}{'...' if len(claim.claim) > 45 else ''}"
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
    
    # Add verifier nodes (including Wikipedia)
    verifier_nodes = [
        {
            "id": "LLM1",
            "label": "LLM1",
            "color": "#9C27B0",  # Purple
            "size": 30,
            "shape": "box",
            "font": {"color": "white"}
        },
        {
            "id": "LLM2",
            "label": "LLM2",
            "color": "#2196F3",  # Blue
            "size": 30,
            "shape": "box",
            "font": {"color": "white"}
        },
        {
            "id": "wikipedia",
            "label": "Wikipedia",
            "color": "#607D8B",  # Blue Gray
            "size": 25,
            "shape": "box",
            "font": {"color": "white"}
        }
    ]
    
    # Add edges from verifiers to claims
    verifier_edges = []
    for claim in claims:
        # LLM1 connections
        llm1_color = get_verification_color(claim.llm1_verification)
        llm1_edge = {
            "from": "LLM1",
            "to": claim.id,
            "color": llm1_color,
            "dashes": True,
            "title": f"LLM1: {claim.llm1_verification}"
        }
        verifier_edges.append(llm1_edge)
        
        # LLM2 connections
        llm2_color = get_verification_color(claim.llm2_verification)
        llm2_edge = {
            "from": "LLM2",
            "to": claim.id,
            "color": llm2_color,
            "dashes": True,
            "title": f"LLM2: {claim.llm2_verification}"
        }
        verifier_edges.append(llm2_edge)
        
        # Wikipedia connections (only for checked claims)
        if claim.is_wikipedia_checked:
            wikipedia_color = get_wikipedia_color(claim.wikipedia_status)
            wikipedia_edge = {
                "from": "wikipedia",
                "to": claim.id,
                "color": wikipedia_color,
                "dashes": [5, 5],  # Different dash pattern
                "title": f"Wikipedia: {claim.wikipedia_status}"
            }
            verifier_edges.append(wikipedia_edge)
    
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
    # Compare LLM1 responses
    llm1_agreement = 1.0 if claim1.llm1_verification == claim2.llm1_verification else 0.0
    
    # Compare LLM2 responses
    llm2_agreement = 1.0 if claim1.llm2_verification == claim2.llm2_verification else 0.0
    
    # Overall agreement is average
    overall_agreement = (llm1_agreement + llm2_agreement) / 2.0
    
    # Bonus for both being high confidence (both "Yes")
    if (claim1.llm1_verification == "Yes" and claim1.llm2_verification == "Yes" and
        claim2.llm1_verification == "Yes" and claim2.llm2_verification == "Yes"):
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

def get_wikipedia_color(status: str) -> str:
    """
    Get color for Wikipedia verification status
    """
    color_map = {
        "Supports": "#4CAF50",      # Green
        "Contradicts": "#F44336",   # Red
        "Unclear": "#FF9800",       # Orange
        "NotFound": "#9E9E9E",      # Gray
        "NotChecked": "#9E9E9E"     # Gray
    }
    return color_map.get(status, "#9E9E9E")  # Gray for unknown

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
        "wikipedia_checks_performed": sum(1 for claim in claims if claim.is_wikipedia_checked)
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
                "LLM1_response": claim.LLM1_verification,
                "gemini_response": claim.gemini_verification,
                "wikipedia_checked": claim.is_wikipedia_checked,
                "wikipedia_status": claim.wikipedia_status if claim.is_wikipedia_checked else None
            },
            "style": {
                "background-color": color_map[risk_level],
                "width": 30,
                "height": 30
            }
        })
    
    return {"elements": elements}
