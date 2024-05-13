import pandas as pd
import spacy
from spacy.matcher import Matcher

# Load the CSV file
df = pd.read_csv('ctf_writeups.csv')

# Load a spaCy model
nlp = spacy.load("en_core_web_sm")  # or any model you prefer

matcher = Matcher(nlp.vocab)

# Patterns for source code detection
source_code_patterns = [
    {"LOWER": "def"},  # Python functions
    {"LOWER": "function"},  # JS functions
    {"TEXT": "#", "IS_ASCII": True, "OP": "?"}, {"LOWER": "include"},  # C/C++ include
    {"LOWER": "import"},  # Python import
    {"LOWER": "console.log"}  # Console log in JS
]
matcher.add("SOURCE_CODE", [source_code_patterns])

# Patterns for solution keywords
solution_patterns = [
    {"LOWER": {"IN": ["solution", "solve", "answer", "result", "exploit"]}}
]
matcher.add("SOLUTION", [solution_patterns])

def extract_information(text):
    doc = nlp(text)
    matches = matcher(doc)
    source_code_snippets = []
    solution_snippets = []
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
        if string_id == "SOURCE_CODE":
            source_code_snippets.append(span.text)
        elif string_id == "SOLUTION":
            solution_snippets.append(span.text)
    return source_code_snippets, solution_snippets

# Apply the extraction function to each description
df['source_code'], df['solutions'] = zip(*df['description'].apply(extract_information))

# Print entries identified as source code or solutions
print(df[['source_code', 'solutions']])

