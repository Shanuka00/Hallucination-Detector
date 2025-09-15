"""Wikidata integration for structured fact verification.

Free, no API key required. Uses public SPARQL endpoint:
https://query.wikidata.org/sparql

We implement a minimal service that can:
- Simulate results for demo speed (use_simulation=True)
- Run simple property lookups in real mode

Current strategy:
1. Attempt to detect an entity (Einstein, Newton, etc.)
2. Map to a Wikidata Q-ID
3. For specific fact patterns (birth date/place, death date/place, Nobel prize year)
   run a SPARQL query to fetch matching properties.
4. Return Supports / Contradicts / Unclear / NotFound similar to Wikipedia service.

This keeps interface parallel so we can drop-in replace or augment.
"""
from __future__ import annotations
import re
import requests
from typing import Optional, Dict, Literal

WikidataStatus = Literal["Supports", "Contradicts", "Unclear", "NotFound"]

class WikidataService:
    endpoint = "https://query.wikidata.org/sparql"
    user_agent = "HallucinationDetector/0.1 (test)"

    def __init__(self, use_simulation: bool = True, timeout: int = 15):
        self.use_simulation = use_simulation
        self.timeout = timeout

    def verify_claim(self, claim: str) -> WikidataStatus:
        # Log the incoming claim
        print(f"[WikidataService] Verifying claim: '{claim}' (simulation={self.use_simulation})")
        if self.use_simulation:
            status = self._simulate(claim)
            print(f"[WikidataService][SIM] Claim: '{claim}' -> Status: {status}")
            return status
        status = self._real_check(claim)
        print(f"[WikidataService][REAL] Claim: '{claim}' -> Status: {status}")
        return status

    # --- Simulation logic (mirrors patterns in other stubs) ---
    def _simulate(self, claim: str) -> WikidataStatus:
        c = claim.lower()
        # Simple pattern heuristics
        if "einstein" in c and "1879" in c and "ulm" in c:
            return "Supports"
        if "einstein" in c and "1885" in c:
            return "Contradicts"
        if "newton" in c and "1643" in c:
            return "Supports"
        if "world war" in c and ("1939" in c and "1945" in c):
            return "Supports"
        if "python" in c and "1991" in c:
            return "Supports"
        # Ambiguous
        if any(y in c for y in ["1687", "1922", "1955"]):
            return "Unclear"
        return "NotFound"

    # --- Real lookup ---
    def _real_check(self, claim: str) -> WikidataStatus:
        entity = self._detect_entity(claim)
        print(f"[WikidataService][REAL] Detected entity: {entity}")
        if not entity:
            return "NotFound"
        patterns = self._extract_patterns(claim)
        if not patterns:
            return "Unclear"
        # For each pattern fetch property values
        supports = False
        contradicts = False
        for p in patterns:
            wd_vals = self._fetch_property(entity["qid"], p["pid"])
            if wd_vals is None:
                continue
            if any(self._value_matches(claim, v) for v in wd_vals):
                supports = True
            else:
                # If user stated a concrete year/place and it's absent
                if p.get("type") == "year" and p.get("year"):
                    contradicts = True
                if p.get("type") == "place" and p.get("place"):
                    contradicts = True
        if supports and not contradicts:
            return "Supports"
        if contradicts and not supports:
            return "Contradicts"
        if supports and contradicts:
            return "Unclear"
        return "Unclear"

    # --- Helpers ---
    def _detect_entity(self, claim: str) -> Optional[Dict[str, str]]:
        cl = claim.lower()
        # Minimal map; extend as needed
        if "einstein" in cl:
            return {"label": "Albert Einstein", "qid": "Q937"}
        if "newton" in cl:
            return {"label": "Isaac Newton", "qid": "Q935"}
        if "python" in cl and "program" in cl:
            return {"label": "Python (programming language)", "qid": "Q28865"}
        if "world war" in cl and "2" in cl:
            return {"label": "World War II", "qid": "Q362"}
        return None

    def _extract_patterns(self, claim: str):
        patterns = []
        # Years
        years = re.findall(r"\b(1[6-9][0-9]{2}|20[0-2][0-9])\b", claim)
        for y in years:
            patterns.append({"type": "year", "pid": "P585", "year": y})  # P585 = point in time (approx)
        # Birth
        if any(k in claim.lower() for k in ["born", "birth"]):
            # birth date P569, birth place P19
            year_match = re.findall(r"\b(1[6-9][0-9]{2}|20[0-2][0-9])\b", claim)
            if year_match:
                patterns.append({"type": "year", "pid": "P569", "year": year_match[0]})
            place_match = re.findall(r"in ([A-Z][a-zA-Z\- ]+)", claim)
            if place_match:
                patterns.append({"type": "place", "pid": "P19", "place": place_match[0]})
        # Death
        if "died" in claim.lower():
            year_match = re.findall(r"\b(1[6-9][0-9]{2}|20[0-2][0-9])\b", claim)
            if year_match:
                patterns.append({"type": "year", "pid": "P570", "year": year_match[0]})
            place_match = re.findall(r"in ([A-Z][a-zA-Z\- ]+)", claim)
            if place_match:
                patterns.append({"type": "place", "pid": "P20", "place": place_match[0]})
        return patterns

    def _fetch_property(self, qid: str, pid: str):
        query = f"""
        SELECT ?valueLabel WHERE {{
          wd:{qid} wdt:{pid} ?value .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'en'. }}
        }} LIMIT 10
        """
        # Log the SPARQL query
        print(f"[WikidataService] SPARQL Query for {qid}/{pid}: {query.strip()}")
        try:
            r = requests.get(
                self.endpoint,
                params={"query": query, "format": "json"},
                headers={"User-Agent": self.user_agent},
                timeout=self.timeout
            )
            if r.status_code != 200:
                return None
            data = r.json()
            vals = [b["valueLabel"]["value"] for b in data.get("results", {}).get("bindings", [])]
            print(f"[WikidataService] SPARQL Response for {qid}/{pid}: {vals}")
            return vals
        except Exception:
            return None

    def _value_matches(self, claim: str, wd_value: str) -> bool:
        cl = claim.lower()
        val = wd_value.lower()
        # Simple containment / year test
        # Extract year from wikidata value if present
        year_match = re.search(r"(1[6-9][0-9]{2}|20[0-2][0-9])", val)
        if year_match and year_match.group(1) in cl:
            return True
        # Place containment
        if any(tok in val for tok in cl.split() if len(tok) > 3):
            return True
        return False

# Optional global instance (mirrors wikipedia_service pattern)
from config import config
wikidata_service = WikidataService(use_simulation=config.WIKIDATA_USE_SIMULATION if hasattr(config, 'WIKIDATA_USE_SIMULATION') else True)
