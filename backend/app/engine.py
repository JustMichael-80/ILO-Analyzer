import math
import os
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from tavily import TavilyClient

# =====================================================================
# 1. FIXED TAILORED TAXONOMY SCHEMAS (Enforcing P4 Admissibility Bounds)
# =====================================================================

class SourceAnalysis(BaseModel):
    earliest_source_found: str
    source_diversity: str  # Must strictly map to: High, Medium, Low, Anomalously Uniform
    institutional_sources: List[str] = []
    grassroots_signals: str
    coverage_trajectory: str # Must strictly map to: Expanding, Contracting, Stable, Hard Cutoff, Never Consolidated

class PPSVerdict(BaseModel):
    wildness_tier: int = Field(..., description="Must be an integer from 1 to 6.")
    wildness_label: str = Field(..., description="Must be exactly one of: Mundane, Murky, Mysterious, Manufactured, Manic, Mythological")
    wildness_justification: str
    signal_pattern: str = Field(..., description="Must be exactly one of: True Signal, ILO Laundered, Narrative Spent, Suppressed Real Event, Anomalous Pattern, Insufficient Data")
    signal_justification: str
    pps_assessment: str = Field(..., description="Must be exactly one of: Structurizing, Entropifying, Hard Cutoff Detected, Unknown")
    pps_justification: str
    local_credibility: str = Field(..., description="Must be exactly one of: Threshold Met, Threshold Not Met, Unknown")
    local_credibility_justification: str
    admissibility_bound: str = Field(..., description="Must be exactly one of: Within Bound, Bound Violated, Approaching Limit")
    admissibility_justification: str
    vanish_pattern: str = Field(..., description="Must be exactly one of: Natural Taper, ILO Fade, Hard Cutoff, Still Active, Unknown")
    vanish_justification: str
    suppression_signals: List[str] = []
    anomalous_patterns: List[str] = []
    source_analysis: SourceAnalysis
    ilo_probability: float = Field(..., description="Float percentage from 0.0 to 100.0")
    verdict: str = Field(..., description="Must be exactly one of: Clean Signal, Likely ILO, Probable ILO, Confirmed ILO Pattern, Possible Suppression, Anomalous - Investigate Further, Insufficient Data")
    verdict_summary: str
    what_would_confirm: str
    wtf_factor: str = Field(..., description="The single most anomalous finding. If nothing is anomalous write: 'No significant anomaly detected.'")

# =====================================================================
# 2. THE ULTIMATE PPS THERMODYNAMIC CORE ENGINE
# =====================================================================

class PPSEngine:
    def __init__(self):
        """
        Initializes the live production engine with optimized tier query lengths,
        strict URL deduplication, and graduated suppression confidence analytics.
        """
        self.gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.search_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
        self.cache: Dict[str, List[Dict[str, Any]]] = {}

        self.domain_blacklist = [
            "reddit.com/r/factorio", "reddit.com/r/gaming", "steamcommunity.com", 
            "gamefaqs", "fandom.com", "twitch.tv", "youtube.com/watch?v=",
            "discord.gg", "resetera", "neogaf", "kotaku", "polygon"
        ]
        
        self.domain_whitelist = [
            "reuters.com", "apnews.com", "bloomberg.com", "nytimes.com", 
            "wsj.com", "politico.com", "bbc.com", "ieee.org", "sciencedirect.com",
            "gov", "edu", "mil", "epri.com", "pnnl.gov", "sandia.gov"
        ]

    def _deduplicate(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicates results by URL across distinct cascade phases to prevent skew."""
        seen = set()
        unique = []
        for r in results:
            url = r.get("url", "").lower().strip()
            if url not in seen:
                seen.add(url)
                unique.append(r)
        return unique

    def _filter_and_score_results(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        clean_results = []
        for item in search_results:
            url = item.get("url", "").lower()
            if any(blacklisted in url for blacklisted in self.domain_blacklist):
                continue
                
            score = 1.0
            if any(whitelisted in url for whitelisted in self.domain_whitelist):
                score += 1.5
                
            item["credibility_score"] = score
            clean_results.append(item)
        return clean_results

    def _calculate_persistence_ratio(self, search_results: List[Dict[str, Any]]) -> float:
        """Calculates P3 thermodynamic filtering with logarithmic domain diversity scaling."""
        if not search_results:
            return 0.0
        
        named_sources = 0
        unverified_claims = 0
        weighted_total_score = 0.0
        
        for item in search_results:
            text = item.get("content", "").lower() + " " + item.get("title", "").lower()
            url = item.get("url", "").lower()
            weight = item.get("credibility_score", 1.0)
            
            # Named Entity Whitelist Multiplier
            is_whitelisted = any(domain in url for domain in self.domain_whitelist)
            has_attribution = any(marker in text for marker in ["said", "reported by", "according to", "confirmed by"])
            
            if is_whitelisted and has_attribution:
                weight *= 1.25
                
            weighted_total_score += weight
            
            if has_attribution:
                named_sources += (1 * weight)
            if any(marker in text for marker in ["alleged", "unconfirmed", "anonymous", "rumor", "speculation"]):
                unverified_claims += (1 * weight)
                
        structural_weight = named_sources / weighted_total_score if weighted_total_score > 0 else 0
        entropy_weight = unverified_claims / weighted_total_score if weighted_total_score > 0 else 0
        
        base_ratio = structural_weight / (1.0 + entropy_weight)
        
        try:
            unique_domains = len(set(item.get("url", "").split("/")[2] for item in search_results if "://" in item.get("url", "")))
        except Exception:
            unique_domains = 1
            
        diversity_bonus = math.log1p(unique_domains) / 10.0
        persistence_ratio = base_ratio + diversity_bonus
        return min(max(persistence_ratio, 0.0), 1.0)

    def _compress_matrix(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Formats and compresses matrix context down to optimize token utilization."""
        return [{
            "url": r.get("url", ""),
            "score": r.get("credibility_score", 1.0),
            "snippet": r.get("content", "")[:300]
        } for r in results]

    def _execute_search_cascade(self, claim: str) -> tuple[List[Dict[str, Any]], bool, str]:
        """Executes sequential search cascade with credit optimization strategies."""
        accumulated_data = []
        possible_suppression = False
        suppression_confidence = "None"
        
        # Credit optimized sizing: max_results dropped to 3 on raw background scans
        phases = [
            {"query": f'"{claim}" primary source reports', "depth": "basic", "max": 3},
            {"query": f'{claim} local news reports journalism', "depth": "basic", "max": 3},
            {"query": f'{claim} local archives timeline historical', "depth": "advanced", "max": 5},
            {"query": f'{claim} debunked verified factual truth', "depth": "basic", "max": 3},
            {"query": f'{claim} study research institutional corroboration verification', "depth": "basic", "max": 3}
        ]
        
        for idx, phase in enumerate(phases, 1):
            query = phase["query"]
            depth = phase["depth"]
            max_r = phase["max"]
            cache_key = f"{query}_{depth}_{max_r}"
            
            if cache_key in self.cache:
                phase_data = self.cache[cache_key]
            else:
                try:
                    print(f"[*] Dispatching Sieve Query Matrix Phase {idx}: '{query}' [Depth: {depth}, Max Results: {max_r}]")
                    response = self.search_client.search(
                        query=query, 
                        max_results=max_r, 
                        include_answer=False,
                        search_depth=depth
                    )
                    phase_data = response.get("results", [])
                    self.cache[cache_key] = phase_data
                except Exception as e:
                    print(f"[-] Search Phase {idx} Error: {e}")
                    phase_data = []
            
            filtered_phase_data = self._filter_and_score_results(phase_data)
            accumulated_data.extend(filtered_phase_data)
            
            checkpoint_matrix = self._deduplicate(accumulated_data)
            pi = self._calculate_persistence_ratio(checkpoint_matrix)
            print(f"[~] Phase {idx} Complete. Running Persistence Ratio (Π) = {pi:.2f}")
            
            if idx == 1 and len(filtered_phase_data) == 0:
                print("[-] Early Cutoff: Absolute structural absence at primary source tier.")
                break
                
            # Graduated Suppression Confidence Matrix
            if idx == 2:
                if pi < 0.05:
                    print("[!] Critical Signal Deficit — High Suppression signature detected.")
                    possible_suppression = True
                    suppression_confidence = "High"
                elif pi < 0.12:
                    print("[!] Low Persistence Target Hit — Medium Suppression signature flagged.")
                    possible_suppression = True
                    suppression_confidence = "Medium"
                
            # Inverted Early Exit. If data is flat and NOT suppressed, exit early.
            if idx == 3 and pi < 0.15 and not possible_suppression:
                print("[+] Early Exit: Signal cleanly entropifying with no suppression signature. ILO Highly Probable.")
                break
                
        return accumulated_data, possible_suppression, suppression_confidence

    def analyze_claim(self, claim: str) -> PPSVerdict:
        print(f"\n[*] Ingesting Target Flux Line: '{claim}'")
        
        # Step 1: Ingestion and Cascade Trace
        raw_matrix, is_suppressed_profile, suppression_confidence = self._execute_search_cascade(claim)
        
        # Core Deduplication
        validated_matrix = self._deduplicate(raw_matrix)
        pi_final = self._calculate_persistence_ratio(validated_matrix)
        
        # Data Compression Layer
        compressed_payload = self._compress_matrix(validated_matrix)
        
        # Step 2: Isolated Type-Safe Generation Phase
        print("[*] Passing matrices to P4 Gate for absolute schema validation...")
        
        system_prompt = (
            "You are the processing module of the Information Laundering Operation Analyzer.\n"
            "Evaluate data using the Principle of Persistent Structurization (PPS).\n\n"
            "CRITICAL SUPPRESSION LOGIC WEIGHTING:\n"
            "If 'Physical Suppression Adaptive Branch Engaged' is True, you must heavily weight your diagnostic verdict "
            "toward 'Possible Suppression' or 'Suppressed Real Event'. Use the 'Suppression Confidence Metric' "
            "to scale your certainty (High means aggressive suppression profile tracking, Medium means marginal variance), "
            "unless the compressed payload data explicitly and unambiguously contradicts this conclusion.\n\n"
            "TAXONOMY INTEGRITY PROTOCOL: You must map your findings strictly to the allowed text values defined in the response schema. "
            "Do NOT invent or extrapolate custom classifications outside of the following taxonomy definitions:\n"
            "- wildness_label must be EXACTLY: 'Mundane', 'Murky', 'Mysterious', 'Manufactured', 'Manic', or 'Mythological'\n"
            "- signal_pattern must be EXACTLY: 'True Signal', 'ILO Laundered', 'Narrative Spent', 'Suppressed Real Event', 'Anomalous Pattern', or 'Insufficient Data'\n"
            "- pps_assessment must be EXACTLY: 'Structurizing', 'Entropifying', 'Hard Cutoff Detected', or 'Unknown'\n"
            "- local_credibility must be EXACTLY: 'Threshold Met', 'Threshold Not Met', or 'Unknown'\n"
            "- admissibility_bound must be EXACTLY: 'Within Bound', 'Bound Violated', or 'Approaching Limit'\n"
            "- vanish_pattern must be EXACTLY: 'Natural Taper', 'ILO Fade', 'Hard Cutoff', 'Still Active', or 'Unknown'\n"
            "- source_diversity must be EXACTLY: 'High', 'Medium', 'Low', or 'Anomalously Uniform'\n"
            "- coverage_trajectory must be EXACTLY: 'Expanding', 'Contracting', 'Stable', 'Hard Cutoff', or 'Never Consolidated'\n"
            "- verdict must be EXACTLY: 'Clean Signal', 'Likely ILO', 'Probable ILO', 'Confirmed ILO Pattern', 'Possible Suppression', 'Anomalous - Investigate Further', or 'Insufficient Data'\n\n"
            "If structural markers are missing, drop down to 'Insufficient Data' or 'Murky'—do NOT create custom labels."
        )
        
        user_prompt = f"""
        Analyze this narrative target: "{claim}"
        
        Compressed and Scored Validation Data Matrix Sourced:
        {str(compressed_payload)}
        
        Calculated Structural Accumulation Metrics:
        - Final Persistence Ratio (Π): {pi_final:.4f}
        - Physical Suppression Adaptive Branch Engaged: {is_suppressed_profile}
        - Suppression Confidence Metric: {suppression_confidence}
        
        Output the final verdict strictly populating the schema parameters without conversational markup.
        """

        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=PPSVerdict,
                temperature=0.05
            ),
        )
        
        return response.parsed

# =====================================================================
# 3. COLAB RUNNER EXECUTION BLOCK
# =====================================================================

if __name__ == "__main__":
    target_claim = "Illegal insider trading was 200 times (NOT percent) normal trade volume for put calls on UA and AA through the CBOE in the days leading up to 9-11"

    if not os.environ.get("GEMINI_API_KEY") or not os.environ.get("TAVILY_API_KEY"):
        print("[-] Initialization Error: Set GEMINI_API_KEY and TAVILY_API_KEY environment variables.")
    else:
        engine = PPSEngine()
        
        if target_claim.strip():
            try:
                verdict_payload = engine.analyze_claim(target_claim)
                print("\n=====================================================================")
                print("[+] P4 NATIVE GATE METRIC: HIGH-SIGNAL THERMODYNAMIC PAYLOAD GENERATED")
                print("=====================================================================\n")
                print(json.dumps(verdict_payload.model_dump(), indent=2))
            except Exception as e:
                print(f"[-] Execution Pipeline Collapsed: {e}")
        else:
            print("[-] Target input null. Shutting down sieve.")

    # Alternate baseline operational test
    print("\n[*] Running alternate trace verification sequence...")
    pps_analyzer = PPSEngine()
    sample_claim = "Substation grid grids down following tracking interference signals."
    try:
        verdict = pps_analyzer.analyze_claim(sample_claim)
        print("\n=====================================================================")
        print("[+] P4 NATIVE GATE METRIC: ALTERNATE PAYLOAD LOGGED CLEANLY")
        print("=====================================================================\n")
        print(verdict.model_dump_json(indent=2))
    except Exception as e:
        print(f"[-] Alternate Baseline Pipeline Collapsed: {e}")
