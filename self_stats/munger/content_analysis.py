from typing import List, Tuple, Dict, Any
from collections import Counter
import re
from urllib.parse import urlparse
import pandas as pd
import spacy
import tldextract
import numpy as np

def extract_search_queries(data: pd.DataFrame) -> List[str]:
    """
    Extract search queries from the dataframe.
    
    Args:
    data (pd.DataFrame): The dataframe containing the entries.
    
    Returns:
    List[str]: A list of search queries.
    """
    return [s.replace("Searched for ", "", 1) for s in data['Text Title'] if s.startswith("Searched")][:1000]

def extract_visited_sites(data: pd.DataFrame) -> List[str]:    
    """
    Extract visited site entries from the dataframe.
    
    Args:
    data (pd.DataFrame): The dataframe containing the entries.
    
    Returns:
    List[str]: A list of visited site URLs.
    """
    return [s.replace("Visited ", "", 1) for s in data['Text Title'] if s.startswith("Visited")][-100:]

def process_texts(texts: List[str], nlp: Any) -> List[str]:
    """
    Process a list of texts using spaCy to tokenize and clean the text by removing stopwords, punctuation,
    and any empty strings. Assumes that the spaCy model is loaded and available as 'nlp'.
    
    Args:
        texts (List[str]): A list of texts to process.
    
    Returns:
        List[str]: A list of cleaned tokens from all documents.
    
    Note:
        This function requires the spaCy library and a model to be loaded with 'nlp'.
        It disables parser and named entity recognition for efficiency during tokenization.
    """
    tokens = []
    for doc in nlp.pipe(texts, disable=["parser", "ner"]):  # We only need tokenization and stopwords, disable the rest for efficiency
        # Process each document
        doc_tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct and token.text.strip() != '']
        tokens.extend(doc_tokens)
    return tokens

def extract_homepage_main(url):
    """
    Extracts the homepage name from a given URL, keeping the top-level domain but excluding the scheme and 'www.' prefix.
    
    Args:
    url (str): The URL from which to extract the homepage name.

    Returns:
    str: The homepage name including the top-level domain, but without the scheme or 'www.' prefix.
    """
    if is_url(url) is False:
        return extract_homepage_alt_form(url)
    else:
        return extract_homepage_from_url(url) 

def extract_homepage_from_url(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    print("Using urlparse:", netloc)
    
    # Using tldextract to get more accurate domain extraction
    extracted = tldextract.extract(url)
    # Reconstructs the domain from its components
    domain = f"{extracted.domain}.{extracted.suffix}"

    return domain

def is_url(text):
    """
    Checks if the provided string starts with a common web protocol ('http://' or 'https://').

    Args:
    url (str): The string to check.

    Returns:
    bool: True if the string starts with 'http://' or 'https://', False otherwise.
    """
    return text.startswith(('http://', 'https://'))

def extract_homepage_alt_form(text):
    """
    Extracts the relevant part of a string based on delimiters and specific rules.
    
    Args:
    text (str): The input text from which to extract information.

    Returns:
    str or None: The extracted text following the rules, or None if the rules exclude the text.
    """
    # Split the text by " - " or " | " and pick the last element
    parts = re.split(r' \- | \| ', text)
    result = parts[-1].strip()

    # Check if result ends with "..." or starts with any internet protocol
    if result.endswith('...') or is_url(result) or len(parts) == 1:
        return None

    return result

def main(arr_data: Tuple[np.ndarray, ...], mappings: List[str]) -> Tuple[np.ndarray, ...]:
    nlp = spacy.load("en_core_web_sm")

    text_index = 0 if mappings[0] == 'Text Title' else 1
    date_index = 1 if mappings[0] == 'Text Title' else 3
    search = True if mappings[0] == 'Text Title' else False
    text_array = arr_data[text_index]
    date_array = arr_data[date_index]

    table = pd.read_csv('personal_data/output/dash_ready_search_data.csv')
    search_queries = extract_search_queries(table)
    visited_sites = extract_visited_sites(table)
    homepages = [extract_homepage_main(site) for site in visited_sites]
    cleaned_tokens = process_texts(search_queries, nlp)
    counted_tokens = Counter(cleaned_tokens)
    token_frequency = pd.DataFrame(counted_tokens, columns=['token', 'frequency']).value_counts().reset_index(name='frequency')
    token_frequency = token_frequency.sort_values(by='frequency', ascending=False)
    visited_data = pd.DataFrame({'visited': visited_sites, 'homepage': homepages})
    visited_data.to_csv('personal_data/output/visited_homepages.csv')
    token_frequency.to_csv('personal_data/output/search_token_frequency.csv')


    if not search:
        short_flags = flag_short_videos(differences)  # flags for short videos
        imputed_arr = (*arr_data, differences, short_flags)
        metadata = (windows[:, 1], windows[:, 0], window_durations, window_counts, counts_over_duration)
    else:
        imputed_arr = (*arr_data, differences)
        metadata = (windows[:, 1], windows[:, 0], window_durations, window_counts, counts_over_duration)

    return imputed_arr, metadata
