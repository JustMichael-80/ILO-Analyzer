"""
ChronoDyne Systems // ILO Analyzer v4.2
MCP Server — Model Context Protocol interface for AI agents

Exposes the ILO Analyzer as a native tool for MCP-compatible AI agents
(Claude Desktop, Claude Code, and any MCP client).

Dual-mode routing:
  Mode 1 — HOSTED (default)
    Routes requests to the live Render API endpoint.
    No local dependencies required. Uses ChronoDyne's shared API keys.
    Set ILO_MODE=hosted (or leave unset).

  Mode 2 — LOCAL (bring your own keys)
    Runs the engine locally with the user's own API keys.
    Full speed, private, no rate sharing, claims never leave local machine.
    Set ILO_MODE=local plus GEMINI_API_KEY and TAVILY_API_KEY.

Configuration (Claude Desktop ~/.config/claude/claude_desktop_config.json):

  Hosted mode:
  {
    "mcpServers": {
      "ilo-analyzer": {
        "command": "python",
        "args": ["/path/to/mcp_server.py"],
        "env": { "ILO_MODE": "hosted" }
      }
    }
  }

  Local mode (bring your own keys):
  {
    "mcpServers": {
      "ilo-analyzer": {
        "command": "python",
        "args": ["/path/to/mcp_server.py"],
        "env": {
          "ILO_MODE": "local",
          "GEMINI_API_KEY": "your-gemini-key",
          "TAVILY_API_KEY": "your-tavily-key"
        }
      }
    }
  }

Tools exposed:
  analyze_claim   — Full Π/Γ physics analysis + P4 Gate verdict
  generate_report — Full analyst report with pattern hypotheses
  check_source    — Classify a single URL against the bias table
  health_check    — Verify engine connectivity and version
"""

import asyncio
import json
import os
import sys

# Ensure local modules are importable in local mode
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ── Configuration ─────────────────────────────────────────────────────────────

ILO_MODE        = os.environ.get("ILO_MODE", "hosted").lower()
HOSTED_BASE_URL = os.environ.get("ILO_BASE_URL", "https://ilo-analyzer.onrender.com")
GEMINI_KEY      = os.environ.get("GEMINI_API_KEY", "")
TAVILY_KEY      = os.environ.get("TAVILY_API_KEY", "")
REQUEST_TIMEOUT = float(os.environ.get("ILO_TIMEOUT", "180"))   # seconds

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    Tool(
        name="analyze_claim",
        description=(
            "Analyze an unverified claim or narrative using the ChronoDyne ILO Analyzer. "
            "Computes the Persistence Ratio (Π = τ_observed / τ_predicted(S)) and Geographic "
            "Entropy (Γ = H_geographic / H_expected(t)) from the Principle of Persistent "
            "Structurization (PPS). Returns a structured verdict including ILO probability, "
            "wildness tier, signal pattern, thermodynamic assessment, saddle-point classification "
            "vs NOAA weather baseline, and Π/Γ diagnostic quadrant. "
            "Use this to determine whether a narrative is persisting naturally or being "
            "artificially sustained against entropic decay."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "description": "The unverified narrative or claim to analyze"
                },
                "fetch_cdx": {
                    "type": "boolean",
                    "description": "Enable Wayback Machine temporal measurement for τ_observed (slower but more accurate Π). Default: true",
                    "default": True
                }
            },
            "required": ["claim"]
        }
    ),
    Tool(
        name="generate_report",
        description=(
            "Generate a full investigative intelligence report for a claim. "
            "Runs the complete ILO analysis pipeline then passes the physics block to a "
            "Gemini analyst instance for pattern hypothesis generation, actor profiling, "
            "red flag identification, investigative next steps, and follow-up claim suggestions. "
            "Returns structured analyst output plus a downloadable markdown report. "
            "Use this when you need a complete intelligence product, not just a verdict."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "description": "The claim to analyze and report on"
                },
                "fetch_cdx": {
                    "type": "boolean",
                    "description": "Enable Wayback Machine temporal measurement. Default: true",
                    "default": True
                }
            },
            "required": ["claim"]
        }
    ),
    Tool(
        name="check_source",
        description=(
            "Classify a single URL or domain against the ChronoDyne bias table. "
            "Returns node class (A/B/C/D), trust weight, political lean, reliability score, "
            "capture status, volatility flag, geographic scope, and country. "
            "Class D sources (social media, forums) are inverted — their presence in a "
            "narrative's citation graph raises suspicion rather than credibility. "
            "Use this to quickly assess the credibility of a specific source."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL or domain to classify"
                }
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="health_check",
        description=(
            "Check ILO Analyzer engine status, version, and cache statistics. "
            "Use this to verify connectivity before running analyses."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
]


# ── Hosted mode — HTTP client ─────────────────────────────────────────────────

async def hosted_analyze(claim: str, fetch_cdx: bool = True) -> dict:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        r = await client.post(
            f"{HOSTED_BASE_URL}/analyze",
            json={"claim": claim, "fetch_cdx": fetch_cdx}
        )
        r.raise_for_status()
        return r.json()


async def hosted_report(claim: str, fetch_cdx: bool = True) -> dict:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        r = await client.post(
            f"{HOSTED_BASE_URL}/report",
            json={"claim": claim, "fetch_cdx": fetch_cdx}
        )
        r.raise_for_status()
        return r.json()


async def hosted_health() -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{HOSTED_BASE_URL}/health")
        r.raise_for_status()
        return r.json()


# ── Local mode — direct engine calls ─────────────────────────────────────────

def _require_local_deps():
    """Lazy import local engine modules — only needed in local mode."""
    if not GEMINI_KEY or not TAVILY_KEY:
        raise RuntimeError(
            "Local mode requires GEMINI_API_KEY and TAVILY_API_KEY environment variables. "
            "Set ILO_MODE=hosted to use the ChronoDyne hosted endpoint instead."
        )


async def local_analyze(claim: str, fetch_cdx: bool = True) -> dict:
    _require_local_deps()
    from engine import execute_triage_sieve, AnalysisRequest
    request = AnalysisRequest(claim=claim, fetch_cdx=fetch_cdx)
    result  = await execute_triage_sieve(request)
    return result.model_dump()


async def local_report(claim: str, fetch_cdx: bool = True) -> dict:
    _require_local_deps()
    from engine import execute_triage_sieve, AnalysisRequest
    from report_generator import generate_report
    request      = AnalysisRequest(claim=claim, fetch_cdx=fetch_cdx)
    verdict      = await execute_triage_sieve(request)
    verdict_dict = verdict.model_dump()
    result       = await generate_report(claim, verdict_dict, GEMINI_KEY)
    return {
        "claim":    claim,
        "report":   result["report"],
        "analyst":  result["analyst"],
        "markdown": result["markdown"],
    }


async def local_health() -> dict:
    return {
        "status":    "online",
        "mode":      "local",
        "framework": "ChronoDyne P4 Gate",
        "version":   "4.2.0",
        "keys": {
            "gemini": "configured" if GEMINI_KEY else "missing",
            "tavily": "configured" if TAVILY_KEY else "missing",
        }
    }


# ── Source check — works in both modes ───────────────────────────────────────

def check_source_local(url: str) -> dict:
    from bias_table import classify_domain
    record, trust = classify_domain(url)
    return {
        "url":        url,
        "node_class": trust.node_class,
        "trust":      trust.adjusted,
        "captured":   trust.captured,
        "volatile":   trust.volatile,
        "inverted":   trust.inverted,
        "geo_scope":  trust.geo_scope,
        "country":    trust.country,
        "notes":      trust.notes,
        "interpretation": (
            "⚠ Class D — Propagation node. Presence in citation graph raises suspicion."
            if trust.inverted else
            f"Class {trust.node_class} — Trust weight: {trust.adjusted:.3f}"
            + (" [CAPTURED]" if trust.captured else "")
            + (" [VOLATILE]" if trust.volatile else "")
        )
    }


# ── Format helpers ────────────────────────────────────────────────────────────

def _format_verdict(data: dict) -> str:
    """Format analyze_claim result as readable text for agent context."""
    pi   = data.get("pi_diagnostics", {})
    gam  = data.get("gamma_diagnostics", {})
    src  = data.get("source_analysis", {})

    lines = [
        f"## ILO Analyzer — Verdict",
        f"",
        f"**Verdict:** {data.get('verdict', '?')}",
        f"**ILO Probability:** {data.get('ilo_probability', 0)}%",
        f"**Wildness:** Tier {data.get('wildness_tier', '?')} // {data.get('wildness_label', '?')}",
        f"**Signal Pattern:** {data.get('signal_pattern', '?')}",
        f"**Thermodynamic Trend:** {data.get('pps_assessment', '?')}",
        f"",
        f"### Physics Block",
        f"- Π (Persistence Ratio): {pi.get('pi_final', 0):.4f}",
        f"- τ_observed: {pi.get('tau_observed_days', 0)} days",
        f"- τ_predicted(S): {pi.get('tau_predicted_days', 0)} days",
        f"- Γ (Geographic Entropy): {gam.get('gamma', 0):.4f}",
        f"- Diffusion Velocity: {gam.get('diffusion_velocity', '?')}",
        f"- Π/Γ Quadrant: {gam.get('quadrant', '?')}",
        f"- Saddle-Point: {pi.get('saddle_point', {}).get('classification', '?')}",
        f"- Class A nodes: {pi.get('class_a_count', 0)}",
        f"- Class D nodes: {pi.get('class_d_count', 0)}",
        f"",
        f"### Interpretation",
        f"{pi.get('pi_interpretation', '')}",
        f"{gam.get('gamma_interpretation', '')}",
        f"",
        f"### Summary",
        f"{data.get('verdict_summary', '')}",
        f"",
        f"**What Would Confirm:** {data.get('what_would_confirm', '')}",
    ]

    if data.get("wtf_factor") and "no significant" not in str(data.get("wtf_factor", "")).lower():
        lines.insert(6, f"**⚡ Core Anomaly:** {data.get('wtf_factor', '')}")
        lines.insert(7, "")

    return "\n".join(lines)


def _format_report(data: dict) -> str:
    """Format generate_report result — return markdown directly."""
    if data.get("markdown"):
        return data["markdown"]
    analyst = data.get("analyst", {})
    return (
        f"## Analyst Assessment\n\n"
        f"**Summary:** {analyst.get('executive_summary', '')}\n\n"
        f"**Campaign Type:** {analyst.get('campaign_type', '')} "
        f"({analyst.get('campaign_confidence', 0):.0%} confidence)\n\n"
        f"**Actor Profile:** {analyst.get('actor_profile', '')}\n"
    )


# ── MCP Server ────────────────────────────────────────────────────────────────

server = Server("ilo-analyzer")


@server.list_tools()
async def list_tools():
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "analyze_claim":
            claim     = arguments["claim"]
            fetch_cdx = arguments.get("fetch_cdx", True)

            if ILO_MODE == "local":
                data = await local_analyze(claim, fetch_cdx)
            else:
                data = await hosted_analyze(claim, fetch_cdx)

            return [TextContent(type="text", text=_format_verdict(data))]

        elif name == "generate_report":
            claim     = arguments["claim"]
            fetch_cdx = arguments.get("fetch_cdx", True)

            if ILO_MODE == "local":
                data = await local_report(claim, fetch_cdx)
            else:
                data = await hosted_report(claim, fetch_cdx)

            return [TextContent(type="text", text=_format_report(data))]

        elif name == "check_source":
            url    = arguments["url"]
            result = check_source_local(url)
            text   = (
                f"## Source Classification: {url}\n\n"
                f"- **Class:** {result['node_class']}\n"
                f"- **Trust Weight:** {result['trust']:.3f}\n"
                f"- **Geographic Scope:** {result['geo_scope']} ({result['country']})\n"
                f"- **Captured:** {result['captured']}\n"
                f"- **Volatile:** {result['volatile']}\n"
                f"- **Inverted (Class D):** {result['inverted']}\n"
                f"- **Notes:** {result['notes']}\n\n"
                f"**Assessment:** {result['interpretation']}"
            )
            return [TextContent(type="text", text=text)]

        elif name == "health_check":
            if ILO_MODE == "local":
                data = await local_health()
            else:
                data = await hosted_health()

            text = (
                f"## ILO Analyzer — Health\n\n"
                f"- **Status:** {data.get('status', '?')}\n"
                f"- **Version:** {data.get('version', '?')}\n"
                f"- **Framework:** {data.get('framework', '?')}\n"
                f"- **Mode:** {ILO_MODE}\n"
            )
            if data.get("cache"):
                cache = data["cache"]
                text += f"- **Cache:** {cache.get('live_entries', 0)} live entries\n"
            return [TextContent(type="text", text=text)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"API error {e.response.status_code}: {e.response.text}")]
    except httpx.TimeoutException:
        return [TextContent(type="text", text=f"Request timed out after {REQUEST_TIMEOUT}s. Try fetch_cdx=false for faster results.")]
    except RuntimeError as e:
        return [TextContent(type="text", text=f"Configuration error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    print(
        f"[ChronoDyne MCP] Starting ILO Analyzer MCP server\n"
        f"[ChronoDyne MCP] Mode: {ILO_MODE.upper()}\n"
        f"[ChronoDyne MCP] {'Base URL: ' + HOSTED_BASE_URL if ILO_MODE == 'hosted' else 'Local engine active'}\n"
        f"[ChronoDyne MCP] Tools: {', '.join(t.name for t in TOOLS)}",
        file=sys.stderr
    )
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
