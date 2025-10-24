import hashlib
from collections import Counter

def describe_string(input_string: str) -> dict:
    normalized_string = input_string.lower()

    length = len(input_string)
    is_palindrome = (normalized_string.lower() == normalized_string.lower()[::-1])
    # is_palindrome = (normalized_string == normalized_string[::-1])
    unique_characters = len(set(input_string.lower().replace(" ", "")))
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
    return dict(Counter(input_string.replace(" ", "")))

