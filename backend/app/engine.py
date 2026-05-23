import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai
from google.genai import types
from tavily import TavilyClient

app = FastAPI(
    title="ChronoDyne Systems // ILO Analyzer Engine",
    description="Thermodynamic information triage via the Principle of Persistent Structurization",
    version="2.0.0"
)

# Enable CORS so your Vercel frontend can safely communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you can restrict this to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INGESTION SCHEMAS ---
class AnalysisRequest(BaseModel):
    claim: str = Field(..., description="The unverified target flux string / narrative element to analyze")

class SourceMatrix(BaseModel):
    earliest_source_found: str
    source_diversity: str
    institutional_sources: List[str]
    grassroots_signals: str
    coverage_trajectory: str

class PPSVerdict(BaseModel):
    wildness_tier: int
    wildness_label: str
    wildness_justification: str
    signal_pattern: str
    signal_justification: str
    pps_assessment: str
    pps_justification: str
    local_credibility: str
    local_credibility_justification: str
    admissibility_bound: str
    admissibility_justification: str
    vanish_pattern: str
    vanish_justification: str
    suppression_signals: List[str]
    anomalous_patterns: List[str]
    source_analysis: SourceMatrix
    ilo_probability: float
    verdict: str
    verdict_summary: str
    what_would_confirm: str
    wtf_factor: str

# --- SYSTEM PROMPT SETUP ---
SYSTEM_PROMPT = """You are the P4 Gate processing module of the Information Laundering Operation (ILO) Analyzer, powered by the Principle of Persistent Structurization (PPS).

Analyze the submitted claim and return a structured verdict using the results provided by the search tool.

TAXONOMY INTEGRITY PROTOCOL — use ONLY these exact values:
- wildness_label: 'Mundane' | 'Murky' | 'Mysterious' | 'Manufactured' | 'Manic' | 'Mythological'
- signal_pattern: 'True Signal' | 'ILO Laundered' | 'Narrative Spent' | 'Suppressed Real Event' | 'Anomalous Pattern' | 'Insufficient Data'
- pps_assessment: 'Structurizing' | 'Entropifying' | 'Hard Cutoff Detected' | 'Unknown'
- local_credibility: 'Threshold Met' | 'Threshold Not Met' | 'Unknown'
- admissibility_bound: 'Within Bound' | 'Bound Violated' | 'Approaching Limit'
- vanish_pattern: 'Natural Taper' | 'ILO Fade' | 'Hard Cutoff' | 'Still Active' | 'Unknown'
- source_diversity: 'High' | 'Medium' | 'Low' | 'Anomalously Uniform'
- coverage_trajectory: 'Expanding' | 'Contracting' | 'Stable' | 'Hard Cutoff' | 'Never Consolidated'
- verdict: 'Clean Signal' | 'Likely ILO' | 'Probable ILO' | 'Confirmed ILO Pattern' | 'Possible Suppression' | 'Anomalous - Investigate Further' | 'Insufficient Data'

SUPPRESSION LOGIC: If persistence ratio is very low with no debunking trail, weight toward 'Possible Suppression' or 'Suppressed Real Event'."""

# --- API ENDPOINT ---
@app.post("/analyze", response_model=PPSVerdict)
async def execute_triage_sieve(request: AnalysisRequest):
    # Ensure keys are present in the hosting environment
    gemini_key = os.environ.get("GEMINI_API_KEY")
    tavily_key = os.environ.get("TAVILY_API_KEY")
    
    if not gemini_key or not tavily_key:
        raise HTTPException(
            status_code=500, 
            detail="Environment configuration missing required secure credentials."
        )

    try:
        # Initialize API Clients
        tavily = TavilyClient(api_key=tavily_key)
        ai = genai.Client(api_key=gemini_key)

        # 1. Execute Multi-Phase Search Cascade
        search_queries = [
            request.claim,
            f"{request.claim} local news reports",
            f"{request.claim} historical archives timeline",
            f"{request.claim} debunked verified",
            f"{request.claim} institutional research study"
        ]
        
        compiled_search_context = []
        for query in search_queries:
            try:
                # Use QnA tool mode for high-signal paragraph summaries from Tavily
                search_res = tavily.search(query=query, max_results=3, topic="general")
                compiled_search_context.append(f"Query: {query}\nResults:\n{search_res}\n---")
            except Exception:
                continue  # Tolerate individual network dropouts to prevent pipeline lock
                
        search_telemetry_string = "\n".join(compiled_search_context)

        # 2. Fire Matrix to Gemini P4 Gate with Structured JSON Enforcement
        response = ai.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Target Ingestion Claim: {request.claim}\n\nCompiled Search Matrix Telemetry:\n{search_telemetry_string}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.1,  # Low variance for deterministic analytical profiles
                response_mime_type="application/json",
                response_schema=PPSVerdict,
            ),
        )

        # 3. Deliver Validated Object Back to UI
        # Gemini's SDK natively parses the schema into response.text when mime_type is enforced
        import json
        return json.loads(response.text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline collapsed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "online", "framework": "ChronoDyne P4 Gate"}
