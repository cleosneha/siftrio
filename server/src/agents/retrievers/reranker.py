from src.agents.schemas import RetrievedChunk


def rrf_merge(
    vector_chunks: list[RetrievedChunk],
    keyword_chunks: list[RetrievedChunk],
    k: int = 60,
    top_k: int = 10,
) -> list[RetrievedChunk]:
    vector_ranks = {c.chunk_id: i + 1 for i, c in enumerate(vector_chunks)}
    keyword_ranks = {c.chunk_id: i + 1 for i, c in enumerate(keyword_chunks)}

    all_ids = set(vector_ranks.keys()) | set(keyword_ranks.keys())
    max_vector_rank = len(vector_chunks) + 1
    max_keyword_rank = len(keyword_chunks) + 1

    merged: dict[str, RetrievedChunk] = {}
    for c in vector_chunks:
        merged[c.chunk_id] = c
    for c in keyword_chunks:
        if c.chunk_id not in merged:
            merged[c.chunk_id] = c

    scores: list[tuple[str, float]] = []
    for chunk_id in all_ids:
        vr = vector_ranks.get(chunk_id, max_vector_rank)
        kr = keyword_ranks.get(chunk_id, max_keyword_rank)
        rrf = 1.0 / (k + vr) + 1.0 / (k + kr)
        scores.append((chunk_id, rrf))

    scores.sort(key=lambda x: x[1], reverse=True)
    top_ids = set(sid for sid, _ in scores[:top_k])

    for chunk_id, rrf_score in scores:
        if chunk_id in merged:
            merged[chunk_id].score = round(rrf_score, 6)

    reranked = [merged[sid] for sid, _ in scores if sid in top_ids]
    return reranked
