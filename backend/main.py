from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from backend.llm.gemini_client import classify_message
from backend.threat_intel.url_extractor import extract_urls
from backend.threat_intel.virustotal_client import check_url_reputation
from backend.graph.graph_builder import ScamGraph
from backend.graph.similarity import compute_similarity
from backend.ml_models import classify_with_model
from backend.db import crud   

logger = logging.getLogger("uvicorn")

app = FastAPI(title="Scam Shield", description="AI-powered scam detection")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize knowledge graph
scam_graph = ScamGraph()

# Load DB scams into graph at startup
@app.on_event("startup")
def load_graph_from_db():
    scams = crud.get_all_scam_messages()
    for scam in scams:
        scam_graph.add_message(scam.message, scam.verdict)
    logger.info(f"Loaded {len(scams)} scam messages from DB into graph.")

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/classify_text/")
async def classify_text(message: str = Form(...), msg_type: str = Form(...)):
    logger.info(f"Received message for classification: {message[:100]}... | Type: {msg_type}")

    # Step 1: ML classification
    try:
        ml_result = classify_with_model(message, msg_type)
        logger.info(f"ML verdict: {ml_result.get('verdict')} | Confidence: {ml_result.get('confidence')}")
    except Exception as e:
        logger.error(f"ML classification failed: {e}")
        ml_result = {"verdict": "error", "confidence": 0.0, "reasoning": f"ML error: {e}"}

    # Step 2: LLM classification
    try:
        llm_result = classify_message(message)
        logger.info(f"LLM verdict: {llm_result.get('verdict')} | Reasoning: {llm_result.get('reasoning')}")
    except Exception as e:
        logger.error(f"LLM classification failed: {e}")
        llm_result = {"verdict": "error", "reasoning": f"LLM error: {e}", "raw_response": ""}

    # Step 3: Threat Intelligence
    urls = extract_urls(message)
    vt_results = []
    if urls:
        for url in urls:
            try:
                vt_result = check_url_reputation(url)
                vt_results.append(vt_result)
                logger.info(f"VirusTotal verdict for {url}: {vt_result.get('verdict')}")
            except Exception as e:
                logger.error(f"VirusTotal check failed for {url}: {e}")
                vt_results.append({"url": url, "verdict": "unknown", "error": str(e)})

    # Step 4: Knowledge Graph
    try:
        scam_graph.add_message(message, llm_result.get("verdict", "unknown"))
        similarities = []
        for node in scam_graph.get_graph().nodes:
            if node != message:
                try:
                    sim = compute_similarity(message, node)
                    if sim > 0.7:
                        scam_graph.add_relationship(message, node, sim)
                        similarities.append({"message": node, "similarity": sim})
                except Exception as e:
                    logger.error(f"Similarity computation failed: {e}")
        if similarities:
            logger.info(f"Graph similarity found with {len(similarities)} nodes")
        else:
            logger.info("Graph: no similar scams detected")
    except Exception as e:
        logger.error(f"Graph update failed: {e}")
        similarities = []

    # Step 5: Fusion Layer
    try:
        final_verdict = llm_result.get("verdict", "unknown")

        confidence = 0.0
        if final_verdict not in ["error", "unknown"]:
            confidence = 0.3  # base from LLM
            confidence += ml_result.get("confidence", 0.0) * 0.4  # ML contributes
            if vt_results and any(res.get("verdict") == "scam" for res in vt_results):
                confidence += 0.15
            if similarities:
                confidence += 0.15
            confidence = min(confidence, 1.0)

        # Force safe verdicts to always be 100%
        if final_verdict == "safe":
            confidence_value = 100
        else:
            confidence_value = int(confidence * 100)

        fusion_result = {
            "final_verdict": final_verdict,
            "confidence": confidence_value,  # integer percent
            "sources": {
                "ml": ml_result.get("verdict"),
                "llm": llm_result.get("verdict"),
                "virustotal": [res.get("verdict") for res in vt_results],
                "graph": "scam" if similarities else "safe"
            },
            "reasoning": llm_result.get("reasoning", "")
        }
        logger.info(f"Fusion verdict: {fusion_result['final_verdict']} | Confidence: {fusion_result['confidence']}%")

        # NEW: Store scam messages in DB with category from LLM
        if final_verdict == "scam":
            crud.insert_scam_message(
                message=message,
                verdict=final_verdict,
                confidence=confidence_value,  # store integer percent
                category=llm_result.get("category", "unknown"),
                source_type=msg_type
            )

    except Exception as e:
        logger.error(f"Fusion failed: {e}")
        fusion_result = {
            "final_verdict": "unknown",
            "confidence": 0,
            "sources": {"ml": "error", "llm": "error", "virustotal": "error", "graph": "error"},
            "reasoning": f"Fusion error: {e}"
        }

    return JSONResponse(content={
        "fusion_result": fusion_result,
        "ml_result": ml_result,
        "llm_result": llm_result,
        "urls_found": urls,
        "virus_total": vt_results,
        "graph_similarity": similarities
    })
