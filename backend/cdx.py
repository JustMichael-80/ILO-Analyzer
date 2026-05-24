"""
ChronoDyne Systems // ILO Analyzer v4
CDX Query Module — Wayback Machine historical snapshot analysis.

Computes τ_observed: the actual time delta between first and last confirmed
citation of a source URL, measured in days. Also extracts snapshot frequency
curve for saddle-point analysis.

API: https://web.archive.org/cdx/search/cdx
Rate limit: ~1 req/sec — all calls are cached via cache.py (7-day TTL).
"""

import time
import math
import requests
from typing import Optional
from urllib.parse import urlparse, quote_plus

import cache

CDX_BASE = "https://web.archive.org/cdx/search/cdx"
CDX_TIMEOUT = 3   # seconds
CDX_RATE_LIMIT = 1.1  # seconds between uncached requests

_last_cdx_request: float = 0.0


def _rate_limit() -> None:
    """Enforce polite rate limiting against Wayback Machine."""
    global _last_cdx_request
    elapsed = time.time() - _last_cdx_request
    if elapsed < CDX_RATE_LIMIT:
        time.sleep(CDX_RATE_LIMIT - elapsed)
    _last_cdx_request = time.time()


def _extract_domain(url: str) -> str:
    """Pull clean domain from URL for CDX querying."""
    try:
        parsed = urlparse(url)
        return parsed.netloc or url
    except Exception:
        return url


def fetch_snapshot_history(url: str, max_snapshots: int = 100) -> Optional[dict]:
    """
    Query CDX API for the snapshot history of a given URL.

    Returns a dict with:
      first_seen:         ISO timestamp of earliest archive
      last_seen:          ISO timestamp of most recent archive
      snapshot_count:     Total snapshots found
      tau_observed_days:  Time delta first→last in days
      frequency_curve:    List of (unix_timestamp, statuscode) tuples
                          for saddle-point analysis
      domain:             Extracted domain

    Returns None on API failure or zero results.
    """
    cache_key = f"cdx:{url[:200]}"
    cached = cache.get("cdx", cache_key)
    if cached is not None:
        return cached

    _rate_limit()

    try:
        params = {
            "url":        url,
            "output":     "json",
            "fl":         "timestamp,statuscode",
            "limit":      max_snapshots,
            "fastLatest": "true",
            "collapse":   "timestamp:8",   # Collapse to daily granularity
        }
        resp = requests.get(CDX_BASE, params=params, timeout=CDX_TIMEOUT)
        resp.raise_for_status()
        raw = resp.json()

    except Exception:
        return None

    # CDX returns [["timestamp","statuscode"], [row], ...] with header row
    if not raw or len(raw) < 2:
        return None

    rows = raw[1:]  # Skip header
    if not rows:
        return None

    # Parse timestamps: CDX format is YYYYMMDDHHmmss
    def parse_cdx_ts(ts: str) -> Optional[float]:
        try:
            import datetime
            dt = datetime.datetime.strptime(ts[:14], "%Y%m%d%H%M%S")
            return dt.timestamp()
        except Exception:
            return None

    timestamps = []
    statuscodes = []
    for row in rows:
        if len(row) >= 2:
            ts = parse_cdx_ts(row[0])
            if ts is not None:
                timestamps.append(ts)
                statuscodes.append(row[1])

    if not timestamps:
        return None

    timestamps.sort()
    first_ts = timestamps[0]
    last_ts  = timestamps[-1]
    tau_days = (last_ts - first_ts) / 86400.0

    frequency_curve = list(zip(timestamps, statuscodes))

    result = {
        "domain":            _extract_domain(url),
        "first_seen":        _ts_to_iso(first_ts),
        "last_seen":         _ts_to_iso(last_ts),
        "snapshot_count":    len(timestamps),
        "tau_observed_days": round(tau_days, 2),
        "frequency_curve":   frequency_curve,
    }

    cache.set("cdx", cache_key, result)
    return result


def _ts_to_iso(unix_ts: float) -> str:
    import datetime
    return datetime.datetime.utcfromtimestamp(unix_ts).strftime("%Y-%m-%dT%H:%M:%SZ")


def compute_snapshot_decay_lambda(frequency_curve: list) -> Optional[float]:
    """
    Fit an exponential decay λ to the snapshot frequency curve.

    Model: count(t) = A · e^(-λ · t)

    Uses log-linear regression on binned daily counts.
    Returns λ (decay constant, per day) or None if insufficient data.
    """
    if len(frequency_curve) < 4:
        return None

    # Bin by day relative to first snapshot
    if not frequency_curve:
        return None

    t0 = frequency_curve[0][0]
    daily_bins: dict[int, int] = {}
    for ts, _ in frequency_curve:
        day = int((ts - t0) / 86400)
        daily_bins[day] = daily_bins.get(day, 0) + 1

    if len(daily_bins) < 3:
        return None

    days = sorted(daily_bins.keys())
    counts = [daily_bins[d] for d in days]

    # Log-linear regression: log(count) = log(A) - λ·day
    log_counts = []
    valid_days  = []
    for d, c in zip(days, counts):
        if c > 0:
            log_counts.append(math.log(c))
            valid_days.append(d)

    if len(valid_days) < 3:
        return None

    n = len(valid_days)
    sum_x  = sum(valid_days)
    sum_y  = sum(log_counts)
    sum_xy = sum(x * y for x, y in zip(valid_days, log_counts))
    sum_x2 = sum(x * x for x in valid_days)

    denom = (n * sum_x2 - sum_x ** 2)
    if denom == 0:
        return None

    slope = (n * sum_xy - sum_x * sum_y) / denom
    # λ = -slope (positive decay constant)
    lam = -slope
    return round(lam, 6) if lam > 0 else None


def batch_fetch(urls: list[str], max_per_batch: int = 10) -> dict[str, Optional[dict]]:
    """
    Fetch CDX data for multiple URLs with cache-first logic.
    Returns {url: result_or_none}.
    """
    results = {}
    for url in urls[:max_per_batch]:
        results[url] = fetch_snapshot_history(url)
    return results
