import re
from collections import Counter
import json

def count_word_repeats(text, word_list):
    # 1. Convert text to lowercase and remove punctuation
    cleaned_text = re.sub(r'[^\w\s]', '', text.lower())
    
    # 2. Split text into individual words
    text_words = cleaned_text.split()
    
    # 3. Count all words in the text
    word_counts = Counter(text_words)
    
    # 4. Filter counts based on your list (lowercased for matching)
    results = {word: word_counts[word.lower()] for word in word_list}
    
    # 5. Get the total sum of all target word repetitions
    total_repeats = sum(results.values())
    
    return results, total_repeats


conjunctions = [
    "and", "after", "although", "as long as", "before", "but", "else",
    "if", "in order", "in case", "nor", "or", "otherwise", "once",
    "since", "then", "though", "till", "unless", "until", "when",
    "whenever", "where", "whereas", "wherever", "while", "yet"
]

with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

for nfr in data:
        line = requirement = nfr['description']
        line = line.strip()
        individual_counts, total = count_word_repeats(line, conjunctions)
        nfr['complexity'] = total

with open("data.json", "w") as file:
    json.dump(data, file, indent=4)