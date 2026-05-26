"""
Search Optimizer Service to run multi-strategy queries, merge, and score results.
"""
import logging
import concurrent.futures

logger = logging.getLogger(__name__)

def _score_result(result: dict) -> int:
    """
    Assigns a relevance score to a search result based on its URL and Title.
    """
    score = 0
    url = result.get("url", "").lower()
    title = result.get("title", "").lower()
    
    # 1. Prioritize PDFs
    if ".pdf" in url or "pdf" in title:
        score += 50
        
    # 2. Prioritize specific exam boards and exams
    exam_keywords = ["rpsc", "reet", "rssb", "ssc", "bank", "banking", "upsc", "pyq", "si", "teacher"]
    for keyword in exam_keywords:
        if keyword in url or keyword in title:
            score += 30
            break
            
    # 3. Prioritize high-quality educational sites
    edu_domains = [
        ".edu", "drishtiias.com", "testbook.com", "byjus.com", 
        "adda247.com", "unacademy.com", "jagranjosh.com", "cleartext.com"
    ]
    for domain in edu_domains:
        if domain in url:
            score += 20
            break
            
    return score

def run_optimized_search(topic: str, client) -> list:
    """
    Executes multiple search strategies, merges results, removes duplicates, 
    and reranks them based on relevance.
    """
    strategies = [
        f"{topic} previous year questions PYQ filetype:pdf",
        f"{topic} RPSC previous year questions pdf",
        f"{topic} REET previous year questions",
        f"{topic} SSC previous year questions",
        f"{topic} RSSB past papers",
        f"{topic} SI Teacher exams PYQ coaching compilations"
    ]
    
    all_results = []
    
    def _execute_query(query):
        try:
            # Using basic search for faster response when running multiple queries
            resp = client.search(query=query, search_depth="basic", max_results=3, include_images=False)
            return resp.get("results", [])
        except Exception as e:
            logger.error(f"Error executing strategy '{query}': {e}")
            return []

    # Run queries concurrently to keep API fast
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_query = {executor.submit(_execute_query, q): q for q in strategies}
        for future in concurrent.futures.as_completed(future_to_query):
            res = future.result()
            all_results.extend(res)
            
    # Deduplicate by URL
    unique_results = {}
    for r in all_results:
        url = r.get("url")
        if url and url not in unique_results:
            unique_results[url] = r
            
    # Score and rerank
    scored_results = []
    for url, data in unique_results.items():
        score = _score_result(data)
        data["relevance_score"] = score
        scored_results.append(data)
        
    # Sort by descending score
    scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Return top 8 best structured results to keep response clean
    return scored_results[:8]
