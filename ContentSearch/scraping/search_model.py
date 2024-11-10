# search_model.py
from sentence_transformers import SentenceTransformer, util
import json

# Load pre-trained LLM model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load course data
with open('../data/courses_data.json') as f:
    courses = json.load(f)

# Pre-compute course embeddings
course_embeddings = model.encode([course['title'] + ' ' + course['description'] for course in courses])

def search_courses(query):
    query_embedding = model.encode(query)
    results = util.semantic_search(query_embedding, course_embeddings, top_k=5)[0]
    return [courses[result['corpus_id']] for result in results]
