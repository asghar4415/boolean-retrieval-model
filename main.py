import os
import re
import glob
from collections import defaultdict
from nltk.stem import PorterStemmer


class BooleanRetrievalModel:
    def __init__(self, abstracts_folder='Abstracts', stopword_file='Stopword-List.txt'):
        # Load stopwords from file and initialize stemmer
        self.stopwords = self.load_stopwords(stopword_file)
        self.stemmer = PorterStemmer()

        # Initialize inverted index (token → set of doc_ids)
        # Initialize positional index (token → {doc_id: [positions]})
        self.inverted_index = defaultdict(set)
        self.positional_index = defaultdict(lambda: defaultdict(list))

        # Build indexes using the documents in the specified folder
        self.build_indexes(abstracts_folder)

    def load_stopwords(self, filepath):
        # Load stopwords into a set for quick lookup
        stopword_set = set()
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip().lower()
                if line:
                    stopword_set.add(line)
        return stopword_set

    def preprocess_text(self, text):
        # Tokenize text into words and convert to lowercase
        words = re.findall(r'\b\w+\b', text.lower())
        processed_words = []

        for word in words:
            if word not in self.stopwords:
                # Apply stemming to reduce word to root form
                stemmed_word = self.stemmer.stem(word)
                processed_words.append(stemmed_word)

        return processed_words

    def build_indexes(self, folder_path):
        # Find all .txt files in the abstracts folder
        file_paths = glob.glob(f'{folder_path}/*.txt')

        for path in file_paths:
            filename = os.path.basename(path)
            # Extract file name without extension
            doc_id_str = filename.split('.')[0]
            doc_id = int(doc_id_str)  # Convert file name to integer doc_id

            # Read file content with fallback encoding in case of errors
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
            except UnicodeDecodeError:
                with open(path, 'r', encoding='latin1') as file:
                    content = file.read()

            # Preprocess content (remove stopwords, apply stemming)
            tokens = self.preprocess_text(content)

            # Populate inverted and positional indexes
            for pos in range(len(tokens)):
                token = tokens[pos]
                # Add doc_id to inverted index for this token
                self.inverted_index[token].add(doc_id)
                self.positional_index[token][doc_id].append(
                    pos)  # Add position to positional index

    def process_boolean_query(self, query_text):
        # --- Helper to tokenize the Boolean query ---
        def tokenize(query):
            # Extract words and operators/parentheses using regex
            tokens = re.findall(r'\b\w+\b|[()]', query.lower())
            result = []

            for token in tokens:
                if token not in ('and', 'or', 'not', '(', ')'):
                    # Stem non-operator tokens
                    token = self.stemmer.stem(token)
                result.append(token)

            return result

        # --- Convert infix query to postfix using Shunting Yard Algorithm ---
        def to_postfix(tokens):
            precedence = {'not': 3, 'and': 2, 'or': 1}  # Operator precedence
            output = []  # Postfix output list
            stack = []   # Operator stack

            for token in tokens:
                if token not in precedence and token not in ('(', ')'):
                    # Operand → directly append to output
                    output.append(token)
                elif token == '(':
                    stack.append(token)
                elif token == ')':
                    # Pop until '(' is found
                    while stack and stack[-1] != '(':
                        output.append(stack.pop())
                    stack.pop()  # Discard '('
                else:
                    # Pop operators with higher or equal precedence
                    while (stack and stack[-1] in precedence and
                           precedence[token] <= precedence[stack[-1]]):
                        output.append(stack.pop())
                    stack.append(token)

            # Append remaining operators
            while stack:
                output.append(stack.pop())

            return output

        # --- Evaluate postfix Boolean expression ---
        def eval_postfix(postfix):
            all_docs = set(range(1, 449))  # Universe of documents (1 to 448)
            stack = []

            for token in postfix:
                if token not in ('and', 'or', 'not'):
                    # Operand → push corresponding doc_ids from index
                    stack.append(self.inverted_index.get(token, set()))
                elif token == 'not':
                    # NOT → complement of top set
                    operand = stack.pop()
                    stack.append(all_docs.difference(operand))
                else:
                    # AND/OR → apply to top two sets
                    right = stack.pop()
                    left = stack.pop()
                    if token == 'and':
                        stack.append(left.intersection(right))
                    elif token == 'or':
                        stack.append(left.union(right))

            return stack[0] if stack else set()

        # Tokenize → Convert to postfix → Evaluate → Return sorted doc_ids
        tokens = tokenize(query_text)
        postfix = to_postfix(tokens)
        result_docs = eval_postfix(postfix)
        return sorted(result_docs)

    def process_proximity_query(self, query_text):
        # Regex pattern: word1 word2 /k
        pattern = re.compile(r'(\w+)\s+(\w+)\s*/(\d+)')
        match = pattern.match(query_text.lower())
        if not match:
            return []  # Invalid format → return empty result

        word1, word2, distance_str = match.groups()
        word1 = self.stemmer.stem(word1)
        word2 = self.stemmer.stem(word2)
        distance = int(distance_str)

        # Find documents containing both words
        docs_with_word1 = set(self.positional_index.get(word1, {}))
        docs_with_word2 = set(self.positional_index.get(word2, {}))
        common_docs = docs_with_word1.intersection(docs_with_word2)

        matched_docs = []

        for doc_id in common_docs:
            positions1 = self.positional_index[word1][doc_id]
            positions2 = self.positional_index[word2][doc_id]

            # Check if positions are within specified distance k
            found = False
            for p1 in positions1:
                for p2 in positions2:
                    if abs(p1 - p2) <= distance:
                        matched_docs.append(doc_id)
                        found = True
                        break  # Stop after finding first match
                if found:
                    break

        matched_docs.sort()
        return matched_docs
