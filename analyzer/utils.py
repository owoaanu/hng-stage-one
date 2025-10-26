import hashlib
import re
from collections import Counter
from typing import Dict, Any


def describe_string(input_string: str) -> dict:
    normalized_string = input_string.lower()

    length = len(input_string)
    is_palindrome = (normalized_string.lower() == normalized_string.lower()[::-1])
    # is_palindrome = (normalized_string == normalized_string[::-1])
    unique_characters = len(set(input_string.lower()
    word_count = len(input_string.split())
    char_frequency_map = generate_character_freq_map(input_string.lower())
    sha256_hash = hash_string(input_string.lower())

    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": char_frequency_map
    }

def hash_string(input_string: str) -> str:
    return hashlib.sha256(input_string.encode('utf-8')).hexdigest()

def generate_character_freq_map(input_string: str) -> dict:
    return dict(Counter(input_string)


class StringAnalyzer:
    @staticmethod
    def analyze_string(value: str) -> Dict[str, Any]:
        """Analyze a string and return all computed properties"""

        # Clean and prepare string for analysis
        cleaned_value = value.strip()
        lower_value = cleaned_value.lower()

        # Compute properties
        length = len(cleaned_value)
        is_palindrome = StringAnalyzer._is_palindrome(cleaned_value)
        unique_characters = len(set(cleaned_value))
        word_count = StringAnalyzer._count_words(cleaned_value)
        sha256_hash = StringAnalyzer._compute_sha256(cleaned_value)
        character_frequency_map = StringAnalyzer._compute_character_frequency(cleaned_value)

        return {
            "length": length,
            "is_palindrome": is_palindrome,
            "unique_characters": unique_characters,
            "word_count": word_count,
            "sha256_hash": sha256_hash,
            "character_frequency_map": character_frequency_map
        }

    @staticmethod
    def _is_palindrome(value: str) -> bool:
        """Check if string is palindrome (case-insensitive, ignore non-alphanumeric)"""
        # Remove non-alphanumeric characters and convert to lowercase
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', value).lower()
        return cleaned == cleaned[::-1]

    @staticmethod
    def _count_words(value: str) -> int:
        """Count words in string (split by whitespace)"""
        words = value.split()
        return len(words)

    @staticmethod
    def _compute_sha256(value: str) -> str:
        """Compute SHA-256 hash of the string"""
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    @staticmethod
    def _compute_character_frequency(value: str) -> Dict[str, int]:
        """Compute frequency of each character in the string"""
        return dict(Counter(value))

    @staticmethod
    def parse_natural_language_query(query: str) -> Dict[str, Any]:
        """Parse natural language query into filter parameters"""
        query_lower = query.lower()
        filters = {}

        # Parse word count
        if "single word" in query_lower or "one word" in query_lower:
            filters["word_count"] = 1
        elif "two words" in query_lower:
            filters["word_count"] = 2
        elif "three words" in query_lower:
            filters["word_count"] = 3

        # Parse palindrome
        if "palindromic" in query_lower or "palindrome" in query_lower:
            filters["is_palindrome"] = True

        # Parse length filters
        import re
        longer_match = re.search(r'longer than (\d+)', query_lower)
        if longer_match:
            filters["min_length"] = int(longer_match.group(1)) + 1

        shorter_match = re.search(r'shorter than (\d+)', query_lower)
        if shorter_match:
            filters["max_length"] = int(shorter_match.group(1)) - 1

        length_match = re.search(r'(\d+) characters', query_lower)
        if length_match:
            filters["min_length"] = int(length_match.group(1))
            # filters["max_length"] = int(length_match.group(1))

        # Parse character containment
        char_match = re.search(r'contain[s]|containing? (?:the letter )?([a-zA-Z])', query_lower)
        if char_match:
            filters["contains_character"] = char_match.group(1)

        # Handle vowel detection
        if "vowel" in query_lower:
            # Use 'a' as default first vowel
            filters["contains_character"] = 'a'

        return {
            "original": query,
            "parsed_filters": filters
        }