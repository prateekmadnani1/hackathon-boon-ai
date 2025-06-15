"""
Enhanced entity matching techniques for improved entity resolution.

This module provides advanced similarity metrics and matching algorithms 
that can be integrated with the existing EntityMapper class.
"""

import re
from typing import List, Dict, Any, Tuple, Set, Optional, Union
from collections import Counter

import numpy as np
from rapidfuzz import fuzz, process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def tokenize(text: str) -> List[str]:
    """
    Tokenize text into words, handling special characters in company names.
    
    Args:
        text: Input text to tokenize
        
    Returns:
        List of tokens
    """
    # Convert to lowercase
    text = text.lower()
    
    # Handle special cases like S&P, AT&T, etc.
    text = re.sub(r'(\w+)&(\w+)', r'\1_and_\2', text)
    
    # Remove punctuation except for meaningful characters in company names
    text = re.sub(r'[^\w\s\.\-]', ' ', text)
    
    # Split by whitespace
    tokens = text.split()
    
    # Filter out very short tokens and common stop words
    stop_words = {'the', 'and', 'a', 'an', 'of', 'to', 'for', 'in', 'on', 'by'}
    return [t for t in tokens if len(t) > 1 and t not in stop_words]


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """
    Calculate Jaccard similarity between two sets.
    
    Args:
        set1: First set of tokens
        set2: Second set of tokens
        
    Returns:
        Jaccard similarity score (0-1)
    """
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0


def token_sort_ratio(s1: str, s2: str) -> float:
    """
    Calculate token sort ratio using RapidFuzz.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Similarity score (0-100)
    """
    return fuzz.token_sort_ratio(s1, s2) / 100.0


def token_set_ratio(s1: str, s2: str) -> float:
    """
    Calculate token set ratio using RapidFuzz.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Similarity score (0-100)
    """
    return fuzz.token_set_ratio(s1, s2) / 100.0


def weighted_similarity(s1: str, s2: str) -> float:
    """
    Calculate weighted similarity using multiple metrics.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Weighted similarity score (0-1)
    """
    # Calculate different similarity metrics
    exact_match = 1.0 if s1.lower() == s2.lower() else 0.0
    ratio = fuzz.ratio(s1.lower(), s2.lower()) / 100.0
    token_sort = token_sort_ratio(s1, s2)
    token_set = token_set_ratio(s1, s2)
    
    # Get token jaccard similarity
    tokens1 = set(tokenize(s1))
    tokens2 = set(tokenize(s2))
    jaccard = jaccard_similarity(tokens1, tokens2)
    
    # Apply weights to different metrics
    weights = {
        'exact_match': 2.0,
        'ratio': 1.0,
        'token_sort': 1.5,
        'token_set': 2.0,
        'jaccard': 1.5
    }
    
    scores = {
        'exact_match': exact_match,
        'ratio': ratio,
        'token_sort': token_sort,
        'token_set': token_set,
        'jaccard': jaccard
    }
    
    # Calculate weighted average
    weighted_sum = sum(weights[k] * scores[k] for k in weights)
    total_weight = sum(weights.values())
    
    return weighted_sum / total_weight


def get_embedding(text: str, model: str = "text-embedding-ada-002") -> List[float]:
    """
    Get OpenAI embedding for a text string.
    
    Args:
        text: Input text to embed
        model: OpenAI embedding model name
        
    Returns:
        Embedding vector as list of floats
    """
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI package is not installed.")
    
    # Ensure text is properly formatted
    text = text.replace("\n", " ")
    
    try:
        response = openai.Embedding.create(
            input=[text],
            model=model
        )
        embedding = response['data'][0]['embedding']
        return embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        # Return empty vector as fallback
        return [0.0] * 1536  # Default dimension for text-embedding-ada-002


def semantic_similarity(s1: str, s2: str, embeddings_cache: Dict[str, List[float]] = None) -> float:
    """
    Calculate semantic similarity using embeddings.
    
    Args:
        s1: First string
        s2: Second string
        embeddings_cache: Optional cache of precomputed embeddings
        
    Returns:
        Similarity score (0-1)
    """
    if not OPENAI_AVAILABLE:
        return 0.0
    
    cache = embeddings_cache or {}
    
    # Get or compute embeddings
    if s1 in cache:
        emb1 = cache[s1]
    else:
        emb1 = get_embedding(s1)
        if cache is not None:
            cache[s1] = emb1
            
    if s2 in cache:
        emb2 = cache[s2]
    else:
        emb2 = get_embedding(s2)
        if cache is not None:
            cache[s2] = emb2
    
    # Calculate cosine similarity
    similarity = cosine_similarity([emb1], [emb2])[0][0]
    return float(similarity)


def tfidf_similarity(strings1: List[str], strings2: List[str]) -> np.ndarray:
    """
    Calculate TF-IDF cosine similarity between two lists of strings.
    
    Args:
        strings1: First list of strings
        strings2: Second list of strings
        
    Returns:
        Similarity matrix
    """
    # Combine all strings
    all_strings = strings1 + strings2
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_strings)
    
    # Get similarity between first set and second set
    similarity_matrix = cosine_similarity(
        tfidf_matrix[:len(strings1)], 
        tfidf_matrix[len(strings1):]
    )
    
    return similarity_matrix


def find_best_match(query: str, candidates: List[str], 
                   threshold: float = 0.7, 
                   method: str = "weighted") -> Optional[Tuple[str, float]]:
    """
    Find best match for a query from a list of candidates.
    
    Args:
        query: String to match
        candidates: List of candidate strings
        threshold: Minimum similarity threshold
        method: Matching method to use ('weighted', 'token_set', 'semantic')
        
    Returns:
        Tuple of (best_match, score) or None if no match above threshold
    """
    if not candidates:
        return None
    
    # Choose similarity function based on method
    if method == "weighted":
        similarity_func = weighted_similarity
    elif method == "token_set":
        similarity_func = token_set_ratio
    elif method == "semantic":
        similarity_func = semantic_similarity
    else:
        similarity_func = weighted_similarity
    
    # Calculate similarity for each candidate
    scores = [(candidate, similarity_func(query, candidate)) for candidate in candidates]
    
    # Get best match
    best_match = max(scores, key=lambda x: x[1])
    
    # Return match if above threshold
    if best_match[1] >= threshold:
        return best_match
    else:
        return None


def detect_name_changes(original_name: str, potential_matches: List[Dict[str, Any]], 
                      name_changes: List[Dict[str, Any]],
                      threshold: float = 0.7) -> Optional[Dict[str, Any]]:
    """
    Detect potential entity name changes.
    
    Args:
        original_name: Original entity name
        potential_matches: List of potential entity matches
        name_changes: List of known name changes
        threshold: Similarity threshold
        
    Returns:
        Dictionary with name change details if detected, None otherwise
    """
    # Check for direct matches in name changes
    for change in name_changes:
        previous = change["previous_name"]
        current = change["current_name"]
        
        # Check if original name matches previous name
        prev_similarity = weighted_similarity(original_name, previous)
        if prev_similarity >= threshold:
            # Find the corresponding entity
            entity_id = change.get("entity_id")
            matched_entity = None
            
            for entity in potential_matches:
                if entity.get("id") == entity_id:
                    matched_entity = entity
                    break
            
            if matched_entity:
                return {
                    "original_name": original_name,
                    "previous_name": previous,
                    "current_name": current,
                    "entity_id": entity_id,
                    "similarity": prev_similarity,
                    "confidence": prev_similarity * 0.9,  # Slightly lower confidence for name changes
                    "matched_entity": matched_entity
                }
    
    # No name change detected
    return None


def multi_stage_entity_matching(query_entity: Dict[str, Any], 
                              candidate_entities: List[Dict[str, Any]],
                              name_changes: List[Dict[str, Any]],
                              threshold: float = 0.7) -> Dict[str, Any]:
    """
    Perform multi-stage entity matching with name change detection.
    
    Args:
        query_entity: Entity to match
        candidate_entities: List of candidate entities from database
        name_changes: List of known name changes
        threshold: Base similarity threshold
        
    Returns:
        Dictionary with matching results
    """
    query_name = query_entity["name"]
    
    # STAGE 1: Check for exact match
    exact_matches = []
    for entity in candidate_entities:
        # Check primary name
        if entity["name"].lower() == query_name.lower():
            exact_matches.append((entity, 1.0))
            continue
            
        # Check aliases
        for alias in entity.get("aliases", []):
            if alias.lower() == query_name.lower():
                exact_matches.append((entity, 1.0))
                break
    
    if exact_matches:
        best_match = exact_matches[0]
        return {
            "matched_entity": best_match[0],
            "confidence": best_match[1],
            "method": "exact_match",
            "name_change_detected": False
        }
    
    # STAGE 2: Check for name changes
    name_change = detect_name_changes(query_name, candidate_entities, name_changes, threshold)
    if name_change:
        return {
            "matched_entity": name_change["matched_entity"],
            "confidence": name_change["confidence"],
            "method": "name_change",
            "name_change_detected": True,
            "name_change_details": {
                "previous_name": name_change["previous_name"],
                "current_name": name_change["current_name"]
            }
        }
    
    # STAGE 3: Fuzzy matching on names
    candidate_names = [entity["name"] for entity in candidate_entities]
    best_match = find_best_match(query_name, candidate_names, threshold, "weighted")
    
    if best_match:
        match_name, score = best_match
        # Find the corresponding entity
        matched_entity = None
        for entity in candidate_entities:
            if entity["name"] == match_name:
                matched_entity = entity
                break
        
        if matched_entity:
            return {
                "matched_entity": matched_entity,
                "confidence": score,
                "method": "fuzzy_match",
                "name_change_detected": False
            }
    
    # STAGE 4: Try semantic matching if available
    if OPENAI_AVAILABLE:
        # Use a slightly lower threshold for semantic matching
        semantic_threshold = threshold - 0.1
        best_match = find_best_match(query_name, candidate_names, semantic_threshold, "semantic")
        
        if best_match:
            match_name, score = best_match
            # Find the corresponding entity
            matched_entity = None
            for entity in candidate_entities:
                if entity["name"] == match_name:
                    matched_entity = entity
                    break
            
            if matched_entity:
                return {
                    "matched_entity": matched_entity,
                    "confidence": score,
                    "method": "semantic_match",
                    "name_change_detected": False
                }
    
    # No match found
    return {
        "matched_entity": None,
        "confidence": 0.0,
        "method": "no_match",
        "name_change_detected": False
    }


# Example usage:
# result = multi_stage_entity_matching(
#     {"name": "Steve's Trucking"},
#     database.entities,
#     database.name_changes,
#     threshold=0.75
# ) 