from backend.fusion.scoring import calculate_confidence

def fuse_decisions(llm_result: dict, vt_results: list, graph_similarity: list) -> dict:
    """
    Fuse decisions from LLM, VirusTotal, and Knowledge Graph.
    Returns final verdict, confidence score, and reasoning.
    """

    # Step 1: LLM verdict
    llm_verdict = llm_result.get("verdict", "unknown")

    # Step 2: VirusTotal verdict (if any URLs)
    vt_verdicts = [res.get("verdict", "unknown") for res in vt_results]
    vt_verdict = "safe"
    if "malicious" in vt_verdicts:
        vt_verdict = "malicious"
    elif "unknown" in vt_verdicts and not vt_results == []:
        vt_verdict = "unknown"

    # Step 3: Graph similarity (if similar scams found)
    graph_verdict = "safe"
    if graph_similarity:
        graph_verdict = "scam"

    # Step 4: Fusion scoring
    scores = {}
    if llm_verdict == "scam":
        scores["llm"] = 0.95
    elif llm_verdict == "safe":
        scores["llm"] = 0.7
    else:
        scores["llm"] = 0.6  # fallback for unknown

    if vt_verdict == "malicious":
        scores["virustotal"] = 0.95
    elif vt_verdict == "safe":
        scores["virustotal"] = 0.7
    else:
        scores["virustotal"] = 0.6

    if graph_verdict == "scam":
        scores["graph"] = 0.85
    else:
        scores["graph"] = 0.65

    confidence = calculate_confidence(scores)

    # Final verdict: majority rule with fallback
    verdicts = [llm_verdict, vt_verdict, graph_verdict]
    try:
        final_verdict = max(set(verdicts), key=verdicts.count)
    except Exception:
        final_verdict = "unknown"

    # Build reasoning string
    reasoning_parts = []
    reasoning_parts.append(f"LLM: {llm_result.get('reasoning', '')}")
    reasoning_parts.append(f"VirusTotal: {vt_verdict}")
    if graph_similarity:
        reasoning_parts.append(f"Graph similarity found with {len(graph_similarity)} messages")
    else:
        reasoning_parts.append("Graph: no similar scams detected")

    reasoning = " | ".join(reasoning_parts)

    return {
        "final_verdict": final_verdict,
        "confidence": confidence,
        "sources": {
            "llm": llm_verdict,
            "virustotal": vt_verdict,
            "graph": graph_verdict
        },
        "reasoning": reasoning
    }
