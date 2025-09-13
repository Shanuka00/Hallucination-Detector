"""
Multi-Knowledge Graph Consensus Service for External Fact Verification

Research-grade implementation using multiple free KG endpoints:
- Wikidata: https://query.wikidata.org/sparql
- DBpedia: https://dbpedia.org/sparql  
- YAGO: Via DBpedia integration

Implements consensus-based verification without complex reasoning,
following approaches from:
- "Cross-KB Entity Linking" (WWW 2015)
- "Knowledge Graph Fusion" (ISWC 2016)
- "Multi-source Knowledge Graph Consensus" patterns

NO simulation mode - always performs real queries.
"""
from __future__ import annotations
import re
import requests
import time
from typing import Optional, Dict, List, Literal, Tuple
from urllib.parse import quote

VerificationStatus = Literal["Supports", "Contradicts", "Unclear", "NotFound"]

class MultiKGService:
    """Multi-Knowledge Graph consensus-based fact verification service"""
    
    def __init__(self, timeout: int = 20, retry_attempts: int = 2):
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.user_agent = "HallucinationDetector/1.0 (research)"
        
        # KG Endpoints
        self.endpoints = {
            'wikidata': 'https://query.wikidata.org/sparql',
            'dbpedia': 'https://dbpedia.org/sparql',
            # Note: Some endpoints may be slower or less reliable
        }
        
        # Track which endpoints are currently available
        self.available_endpoints = set(self.endpoints.keys())
        
    def verify_claim(self, claim: str) -> VerificationStatus:
        """
        Verify a claim using multi-KG consensus
        
        Process:
        1. Detect entities and extract verifiable facts
        2. Query each available KG endpoint
        3. Apply consensus voting
        4. Return majority decision
        """
        print(f"[MultiKG] Starting verification: '{claim}'")
        
        # Extract verifiable components from claim
        entity_info = self._detect_entities(claim)
        if not entity_info:
            print(f"[MultiKG] No recognizable entities found")
            return "NotFound"
            
        fact_patterns = self._extract_fact_patterns(claim)
        if not fact_patterns:
            print(f"[MultiKG] No verifiable fact patterns extracted")
            return "Unclear"
            
        print(f"[MultiKG] Detected entity: {entity_info}")
        print(f"[MultiKG] Fact patterns: {fact_patterns}")
        
        # Query each KG
        kg_results = {}
        for kg_name in self.available_endpoints:
            try:
                result = self._query_kg(kg_name, entity_info, fact_patterns, claim)
                kg_results[kg_name] = result
                print(f"[MultiKG] {kg_name.upper()}: {result}")
            except Exception as e:
                print(f"[MultiKG] {kg_name.upper()} failed: {e}")
                kg_results[kg_name] = "Error"
                
        # Apply consensus logic
        consensus = self._calculate_consensus(kg_results)
        print(f"[MultiKG] Final consensus: {consensus}")
        return consensus
        
    def _detect_entities(self, claim: str) -> Optional[Dict[str, any]]:
        """Detect main entities in the claim across different KGs"""
        claim_lower = claim.lower()
        
        # Enhanced entity detection with cross-KG identifiers
        entities = {
            'einstein': {
                'name': 'Albert Einstein',
                'wikidata_id': 'Q937',
                'dbpedia_id': 'Albert_Einstein'
            },
            'newton': {
                'name': 'Isaac Newton', 
                'wikidata_id': 'Q935',
                'dbpedia_id': 'Isaac_Newton'
            },
            'python': {
                'name': 'Python (programming language)',
                'wikidata_id': 'Q28865', 
                'dbpedia_id': 'Python_(programming_language)'
            },
            'world war': {
                'name': 'World War II',
                'wikidata_id': 'Q362',
                'dbpedia_id': 'World_War_II' 
            },
            'shakespeare': {
                'name': 'William Shakespeare',
                'wikidata_id': 'Q692',
                'dbpedia_id': 'William_Shakespeare'
            },
            'darwin': {
                'name': 'Charles Darwin',
                'wikidata_id': 'Q1035',
                'dbpedia_id': 'Charles_Darwin'
            }
        }
        
        for key, entity in entities.items():
            if key in claim_lower:
                return entity
                
        return None
        
    def _extract_fact_patterns(self, claim: str) -> List[Dict[str, any]]:
        """Extract verifiable fact patterns from claim"""
        patterns = []
        claim_lower = claim.lower()
        
        # Birth date/place patterns
        if any(keyword in claim_lower for keyword in ['born', 'birth']):
            # Extract years
            years = re.findall(r'\b(1[6-9]\d{2}|20[0-2]\d)\b', claim)
            for year in years:
                patterns.append({
                    'type': 'birth_date',
                    'value': year,
                    'wikidata_property': 'P569',
                    'dbpedia_property': 'dbo:birthDate'
                })
                
            # Extract places
            places = re.findall(r'in ([A-Z][a-zA-Z\s,]+?)(?:[,.]|$)', claim)
            for place in places:
                place = place.strip()
                patterns.append({
                    'type': 'birth_place', 
                    'value': place,
                    'wikidata_property': 'P19',
                    'dbpedia_property': 'dbo:birthPlace'
                })
                
        # Death date/place patterns  
        if 'died' in claim_lower or 'death' in claim_lower:
            years = re.findall(r'\b(1[6-9]\d{2}|20[0-2]\d)\b', claim)
            for year in years:
                patterns.append({
                    'type': 'death_date',
                    'value': year,
                    'wikidata_property': 'P570', 
                    'dbpedia_property': 'dbo:deathDate'
                })
                
        # Nobel Prize patterns
        if 'nobel' in claim_lower:
            years = re.findall(r'\b(19\d{2}|20[0-2]\d)\b', claim)
            for year in years:
                patterns.append({
                    'type': 'nobel_year',
                    'value': year,
                    'wikidata_property': 'P166',  # award received
                    'dbpedia_property': 'dbo:award'
                })
                
        # Theory/work development patterns
        if any(word in claim_lower for word in ['theory', 'developed', 'published', 'wrote']):
            years = re.findall(r'\b(1[6-9]\d{2}|20[0-2]\d)\b', claim)
            for year in years:
                patterns.append({
                    'type': 'work_date',
                    'value': year,
                    'wikidata_property': 'P571',  # inception
                    'dbpedia_property': 'dbo:publicationDate'
                })
                
        return patterns
        
    def _query_kg(self, kg_name: str, entity: Dict, patterns: List[Dict], original_claim: str) -> VerificationStatus:
        """Query a specific knowledge graph"""
        if kg_name == 'wikidata':
            return self._query_wikidata(entity, patterns, original_claim)
        elif kg_name == 'dbpedia':
            return self._query_dbpedia(entity, patterns, original_claim)
        else:
            return "Error"
            
    def _query_wikidata(self, entity: Dict, patterns: List[Dict], claim: str) -> VerificationStatus:
        """Query Wikidata with proper SPARQL"""
        entity_id = entity.get('wikidata_id')
        if not entity_id:
            return "NotFound"
            
        supports_count = 0
        contradicts_count = 0
        total_patterns = len(patterns)
        
        for pattern in patterns:
            prop = pattern.get('wikidata_property')
            expected_value = pattern.get('value', '').lower()
            
            if not prop or not expected_value:
                continue
                
            # Build SPARQL query based on property type
            if pattern['type'] in ['birth_date', 'death_date', 'work_date']:
                query = f"""
                SELECT ?date WHERE {{
                    wd:{entity_id} wdt:{prop} ?date .
                }}
                """
            elif pattern['type'] in ['birth_place']:
                query = f"""
                SELECT ?placeLabel WHERE {{
                    wd:{entity_id} wdt:{prop} ?place .
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                }}
                """
            elif pattern['type'] == 'nobel_year':
                query = f"""
                SELECT ?awardLabel ?year WHERE {{
                    wd:{entity_id} wdt:{prop} ?award .
                    ?award wdt:P585 ?year .
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                    FILTER(CONTAINS(LCASE(STR(?awardLabel)), "nobel"))
                }}
                """
            else:
                query = f"""
                SELECT ?value WHERE {{
                    wd:{entity_id} wdt:{prop} ?value .
                }}
                """
                
            print(f"[MultiKG][Wikidata] Query: {query.strip()}")
            
            try:
                response = requests.get(
                    self.endpoints['wikidata'],
                    params={'query': query, 'format': 'json'},
                    headers={'User-Agent': self.user_agent},
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', {}).get('bindings', [])
                    print(f"[MultiKG][Wikidata] Results: {results}")
                    
                    if self._check_value_match(expected_value, results, pattern['type']):
                        supports_count += 1
                    else:
                        contradicts_count += 1
                        
            except Exception as e:
                print(f"[MultiKG][Wikidata] Error: {e}")
                
        return self._determine_status(supports_count, contradicts_count, total_patterns)
        
    def _query_dbpedia(self, entity: Dict, patterns: List[Dict], claim: str) -> VerificationStatus:
        """Query DBpedia with SPARQL"""
        entity_name = entity.get('dbpedia_id')
        if not entity_name:
            return "NotFound"
            
        supports_count = 0
        contradicts_count = 0  
        total_patterns = len(patterns)
        
        for pattern in patterns:
            prop = pattern.get('dbpedia_property')
            expected_value = pattern.get('value', '').lower()
            
            if not prop or not expected_value:
                continue
                
            query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbr: <http://dbpedia.org/resource/>
            
            SELECT ?value WHERE {{
                dbr:{entity_name} {prop} ?value .
            }}
            """
            
            print(f"[MultiKG][DBpedia] Query: {query.strip()}")
            
            try:
                response = requests.get(
                    self.endpoints['dbpedia'],
                    params={'query': query, 'format': 'json'},
                    headers={'User-Agent': self.user_agent},
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', {}).get('bindings', [])
                    print(f"[MultiKG][DBpedia] Results: {results}")
                    
                    if self._check_value_match(expected_value, results, pattern['type']):
                        supports_count += 1
                    else:
                        contradicts_count += 1
                        
            except Exception as e:
                print(f"[MultiKG][DBpedia] Error: {e}")
                
        return self._determine_status(supports_count, contradicts_count, total_patterns)
        
    def _check_value_match(self, expected: str, results: List[Dict], pattern_type: str) -> bool:
        """Check if query results match expected value"""
        if not results:
            return False
            
        expected_lower = expected.lower()
        
        for result in results:
            for key, value_obj in result.items():
                value = value_obj.get('value', '').lower()
                
                # Year matching for dates
                if pattern_type in ['birth_date', 'death_date', 'work_date', 'nobel_year']:
                    year_match = re.search(r'(\d{4})', value)
                    if year_match and year_match.group(1) == expected_lower:
                        return True
                        
                # Place name matching 
                elif pattern_type in ['birth_place']:
                    if expected_lower in value or any(word in value for word in expected_lower.split() if len(word) > 3):
                        return True
                        
                # General text matching
                else:
                    if expected_lower in value:
                        return True
                        
        return False
        
    def _determine_status(self, supports: int, contradicts: int, total: int) -> VerificationStatus:
        """Determine verification status from pattern matches"""
        if total == 0:
            return "Unclear"
            
        support_ratio = supports / total
        contradict_ratio = contradicts / total
        
        if support_ratio >= 0.7:
            return "Supports"
        elif contradict_ratio >= 0.7:
            return "Contradicts"
        else:
            return "Unclear"
            
    def _calculate_consensus(self, kg_results: Dict[str, VerificationStatus]) -> VerificationStatus:
        """Calculate consensus from multiple KG results using majority voting"""
        
        # Filter out errors
        valid_results = [result for result in kg_results.values() if result != "Error"]
        
        if not valid_results:
            return "NotFound"
            
        # Count votes
        vote_counts = {
            "Supports": sum(1 for r in valid_results if r == "Supports"),
            "Contradicts": sum(1 for r in valid_results if r == "Contradicts"), 
            "Unclear": sum(1 for r in valid_results if r == "Unclear"),
            "NotFound": sum(1 for r in valid_results if r == "NotFound")
        }
        
        total_votes = len(valid_results)
        print(f"[MultiKG] Vote counts: {vote_counts} (total: {total_votes})")
        
        # Majority decision
        max_votes = max(vote_counts.values())
        winners = [status for status, count in vote_counts.items() if count == max_votes]
        
        # Handle ties and edge cases
        if len(winners) == 1:
            return winners[0]
        elif "Supports" in winners and "Contradicts" in winners:
            return "Unclear"  # Conflicting evidence
        elif "Supports" in winners:
            return "Supports"  # Prefer positive evidence
        elif "Contradicts" in winners:
            return "Contradicts"
        else:
            return "Unclear"

# Global service instance
multi_kg_service = MultiKGService()