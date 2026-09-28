"""Text, numeric-fact and embedding metrics used by the GRPO reward."""

from __future__ import annotations

import os
import re
from collections import OrderedDict
from threading import Lock

import numpy as np


_NUMERIC_PATTERN = re.compile(r"(?<!\w)[+−-]?\d+(?:[.,]\d+)*(?:\s*%)?(?!\w)")


def clean_words(text: str) -> list[str]:
    text = _NUMERIC_PATTERN.sub(" ", str(text).lower())
    words = re.findall(r"\b\w+\b", text)
    stopwords = {
        "và", "của", "các", "cho", "trong", "để", "này", "được",
        "với", "như", "một", "những",
    }
    return [word for word in words if word not in stopwords]


_TOKEN_PATTERN = re.compile(r"\b\w+\b", re.UNICODE)
_POSITIVE_DIRECTION_CUES = {
    "tăng", "gia", "cải", "thiện", "tích", "improved", "increase",
    "increased", "grew", "growth", "rose", "higher", "up", "positive", "gain",
}
_NEGATIVE_DIRECTION_CUES = {
    "giảm", "suy", "sụt", "thua", "lỗ", "decline", "declined", "decrease",
    "decreased", "fell", "loss", "lower", "down", "negative", "drop", "dropped",
}
_NUMERIC_CONTEXT_STOPWORDS = {
    "đạt", "là", "có", "và", "của", "cho", "trong", "từ", "với",
    "tỷ", "đồng", "triệu", "nghìn", "thousand", "million", "billion",
    "percent", "was", "were", "the", "of", "in",
}


def _without_numeric_values(text: str) -> str:
    """Mask literal numeric facts so lexical/semantic metrics do not double count them."""
    return _NUMERIC_PATTERN.sub(" ", str(text))

_TEXT_EMBEDDER = None
_TEXT_EMBEDDER_LOCK = Lock()
_SOURCE_CACHE_LOCK = Lock()
_SOURCE_CACHE_MODEL = None
_SOURCE_EMBEDDINGS = OrderedDict()

def set_text_embedder(model) -> None:
    """Share the retriever's SentenceTransformer instead of loading it twice."""
    global _TEXT_EMBEDDER
    _TEXT_EMBEDDER = model


def _get_text_embedder():
    global _TEXT_EMBEDDER
    if _TEXT_EMBEDDER is None:
        with _TEXT_EMBEDDER_LOCK:
            if _TEXT_EMBEDDER is None:
                from sentence_transformers import SentenceTransformer
                from backend import config

                _TEXT_EMBEDDER = SentenceTransformer(
                    config.EMBEDDING_MODEL_NAME,
                    device=config.EMBEDDING_DEVICE,
                    cache_folder=config.EMBEDDING_CACHE_DIR,
                )
    return _TEXT_EMBEDDER

def _canonical_number(value: str) -> str:
    return re.sub(r"\s+", "", value).replace("−", "-")


def _is_structural_list_number(text: str, match: re.Match) -> bool:
    line_start = text.rfind("\n", 0, match.start()) + 1
    prefix = text[line_start:match.start()]
    if not re.fullmatch(r"\s*(?:[-*•]\s*)?", prefix) or not re.fullmatch(r"\d{1,2}", match.group()):
        return False
    return re.match(r"\s*[.)](?:\s+|$)", text[match.end():]) is not None


def _numeric_occurrences(text: str) -> list[tuple[str, set[str]]]:
    """Return each factual number with context from its punctuation-delimited clause."""
    matches = [
        match for match in _NUMERIC_PATTERN.finditer(text)
        if not _is_structural_list_number(text, match)
    ]
    delimiters = [
        (match.start(), match.end())
        for match in re.finditer(r"[.!?;,\n]|\b(?:và|but|while|whereas)\b", text, re.IGNORECASE)
        if not any(number.start() < match.start() < number.end() for number in matches)
    ]
    occurrences = []
    for match in matches:
        left = max((end for _, end in delimiters if end <= match.start()), default=0)
        right = min((start for start, _ in delimiters if start >= match.end()), default=len(text))
        clause = text[left:right]
        local_start, local_end = match.start() - left, match.end() - left
        tokens = list(_TOKEN_PATTERN.finditer(clause))
        before = [token for token in tokens if token.end() <= local_start][-5:]
        after = [token for token in tokens if token.start() >= local_end][:5]
        context = {
            token.group().casefold()
            for token in [*before, *after]
            if not _NUMERIC_PATTERN.fullmatch(token.group())
            and token.group().casefold() not in _NUMERIC_CONTEXT_STOPWORDS
        }
        occurrences.append((_canonical_number(match.group()), context))
    return occurrences


def _numeric_fact_records(text: str) -> list[dict[str, object]]:
    """Serialize clause-local source facts once during training preparation."""
    return [
        {"value": number, "context": sorted(context)}
        for number, context in _numeric_occurrences(text)
    ]


def _coerce_numeric_fact_records(source: str, records=None) -> list[tuple[str, set[str]]]:
    if records is None:
        return _numeric_occurrences(source)
    if not isinstance(records, (list, tuple)):
        raise ValueError("numeric_facts must be a list of value/context records")
    result = []
    for item in records:
        if not isinstance(item, dict) or not isinstance(item.get("value"), str):
            raise ValueError("Invalid numeric fact record")
        context = item.get("context")
        if not isinstance(context, (list, tuple, set)) or any(
            not isinstance(token, str) for token in context
        ):
            raise ValueError("Invalid numeric fact context")
        result.append((_canonical_number(item["value"]), {token.casefold() for token in context}))
    return result


def _opposite_numeric_direction(source_context: set[str], generated_context: set[str]) -> bool:
    source_positive = source_context & _POSITIVE_DIRECTION_CUES
    source_negative = source_context & _NEGATIVE_DIRECTION_CUES
    generated_positive = generated_context & _POSITIVE_DIRECTION_CUES
    generated_negative = generated_context & _NEGATIVE_DIRECTION_CUES
    return bool(
        (source_positive and generated_negative and not source_negative and not generated_positive)
        or (source_negative and generated_positive and not source_positive and not generated_negative)
    )


def _numeric_context_similarity(source_context: set[str], generated_context: set[str]) -> float:
    if _opposite_numeric_direction(source_context, generated_context):
        return 0.0
    union = source_context | generated_context
    return len(source_context & generated_context) / len(union) if union else 1.0


def _numeric_fact_scores(
    source: str, generated: str, source_facts=None,
) -> list[float | None]:
    """Detect explicit number misattribution; leave ambiguous paraphrases to semantic reward."""
    expected = _coerce_numeric_fact_records(source, source_facts)
    if not expected:
        return []
    remaining = _numeric_occurrences(generated)
    scores = []
    for fact_index, (number, source_context) in enumerate(expected):
        candidates = [(i, item) for i, item in enumerate(remaining) if item[0] == number]
        if not candidates:
            scores.append(None)
            continue
        absolute_index, generated_fact = max(
            candidates,
            key=lambda pair: _numeric_context_similarity(source_context, pair[1][1]),
        )
        generated_context = generated_fact[1]
        own_similarity = _numeric_context_similarity(source_context, generated_context)
        other_similarity = max(
            (
                _numeric_context_similarity(other_context, generated_context)
                for other_index, (other_number, other_context) in enumerate(expected)
                if other_index != fact_index and other_number != number and other_context
            ),
            default=0.0,
        )
        explicit_misattribution = (
            bool(source_context and generated_context)
            and own_similarity < 0.34
            and other_similarity >= 0.67
            and other_similarity - own_similarity >= 0.34
        )
        direction_mismatch = _opposite_numeric_direction(source_context, generated_context)
        scores.append(0.0 if direction_mismatch or explicit_misattribution else 1.0)
        remaining.pop(absolute_index)
    return scores


def _numeric_fact_coverage(source: str, generated: str, source_facts=None) -> float:
    """Average number-to-subject preservation; heuristic, not entailment."""
    scores = _numeric_fact_scores(source, generated, source_facts)
    return float(sum(score or 0.0 for score in scores) / len(scores)) if scores else 1.0


def _lexical_score(source: str, generated: str) -> float:
    source_words = clean_words(source)
    generated_words = clean_words(generated)
    if not source_words:
        return 1.0
    overlap = len(set(source_words).intersection(generated_words)) / len(set(source_words))
    length_ratio = len(generated_words) / max(1, len(source_words))
    return float(max(0.0, min(1.0, overlap * min(1.0, length_ratio / 0.3))))

def _chunk_semantic_text(
    text: str, tokenizer, max_seq_length: int
) -> tuple[list[str], list[int]]:
    """Split text by model tokens so embedding never truncates slide content."""
    value = str(text).strip() or "."
    if tokenizer is None:
        tokens = value.split()
        chunk_size = max(1, min(96, max_seq_length - 2))
        overlap = min(12, chunk_size // 8)
        chunks, weights = [], []
        start = 0
        while start < len(tokens):
            end = min(len(tokens), start + chunk_size)
            chunks.append(" ".join(tokens[start:end]))
            weights.append(end - start)
            if end == len(tokens):
                break
            start = end - overlap
        return chunks, weights

    token_ids = tokenizer.encode(value, add_special_tokens=False)
    if not token_ids:
        token_ids = tokenizer.encode(".", add_special_tokens=False)
    chunk_size = max(1, max_seq_length - tokenizer.num_special_tokens_to_add(pair=False))
    overlap = min(16, chunk_size // 8)
    chunks, weights = [], []
    start = 0
    while start < len(token_ids):
        end = min(len(token_ids), start + chunk_size)
        chunk = tokenizer.decode(token_ids[start:end], skip_special_tokens=True).strip()
        chunks.append(chunk or ".")
        weights.append(end - start)
        if end == len(token_ids):
            break
        start = end - overlap
    return chunks, weights


def _encode_reward_chunks(chunks, source_chunks, embedder):
    """Deduplicate each batch and retain only bounded, immutable source vectors."""
    global _SOURCE_CACHE_MODEL
    limit = max(0, int(os.getenv("RL_SOURCE_EMBEDDING_CACHE_SIZE", "4096")))
    with _SOURCE_CACHE_LOCK:
        if _SOURCE_CACHE_MODEL is not embedder:
            _SOURCE_EMBEDDINGS.clear()
            _SOURCE_CACHE_MODEL = embedder
        unique = list(dict.fromkeys(chunks))
        vectors = {}
        missing = []
        for chunk in unique:
            if chunk in _SOURCE_EMBEDDINGS:
                vectors[chunk] = _SOURCE_EMBEDDINGS[chunk]
                _SOURCE_EMBEDDINGS.move_to_end(chunk)
            else:
                missing.append(chunk)
        if missing:
            encoded = np.asarray(embedder.encode(
                missing, normalize_embeddings=True, show_progress_bar=False,
            ))
            if len(encoded) != len(missing) or not np.isfinite(encoded).all():
                raise RuntimeError("Text embedder returned invalid reward vectors")
            vectors.update(zip(missing, encoded, strict=True))
        for chunk in unique:
            if limit and chunk in source_chunks:
                _SOURCE_EMBEDDINGS[chunk] = vectors[chunk].copy()
                _SOURCE_EMBEDDINGS.move_to_end(chunk)
        while len(_SOURCE_EMBEDDINGS) > limit:
            _SOURCE_EMBEDDINGS.popitem(last=False)
        return np.stack([vectors[chunk] for chunk in chunks])


def _semantic_reward_scores(
    sources: list[str], generated: list[str], embedder
) -> list[float]:
    tokenizer = getattr(embedder, "tokenizer", None)
    max_seq_length = int(getattr(embedder, "max_seq_length", 128) or 128)
    grouped_chunks = []
    all_chunks = []
    source_chunk_set = set()
    for source, output in zip(sources, generated, strict=True):
        source_chunks, source_weights = _chunk_semantic_text(
            _without_numeric_values(source), tokenizer, max_seq_length
        )
        generated_chunks, generated_weights = _chunk_semantic_text(
            _without_numeric_values(output), tokenizer, max_seq_length
        )
        source_start = len(all_chunks)
        all_chunks.extend(source_chunks)
        source_chunk_set.update(source_chunks)
        generated_start = len(all_chunks)
        all_chunks.extend(generated_chunks)
        grouped_chunks.append(
            (
                source_start,
                len(source_chunks),
                source_weights,
                generated_start,
                len(generated_chunks),
                generated_weights,
            )
        )

    embeddings = _encode_reward_chunks(all_chunks, source_chunk_set, embedder)
    scores = []
    for (
        source_start,
        source_count,
        source_weights,
        generated_start,
        generated_count,
        generated_weights,
    ) in grouped_chunks:
        source_vectors = embeddings[source_start : source_start + source_count]
        generated_vectors = embeddings[generated_start : generated_start + generated_count]
        similarities = np.clip(source_vectors @ generated_vectors.T, 0.0, 1.0)
        source_coverage = np.average(
            similarities.max(axis=1), weights=source_weights
        )
        generated_precision = np.average(
            similarities.max(axis=0), weights=generated_weights
        )
        denominator = source_coverage + generated_precision
        scores.append(
            float(2.0 * source_coverage * generated_precision / denominator)
            if denominator > 0
            else 0.0
        )
    return scores
