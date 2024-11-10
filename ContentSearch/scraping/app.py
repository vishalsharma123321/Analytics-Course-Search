import gradio as gr
import json
import os

# Ensure you specify the correct path to your scraped JSON data
DATA_PATH = './courses_data.json'

# Load the scraped data into memory
def load_courses():
    with open(DATA_PATH, 'r') as f:
        return json.load(f)

# Modify the search function to search in the loaded data
def search_courses(query):
    courses = load_courses()
    query = query.lower()  # Make the query case-insensitive
    results = []

    # Iterate through all courses and filter by the query keyword
    for course in courses:
        if query in course['title'].lower() or query in course['description'].lower():
            # Check if the course is not already in the results
            if course not in results:
                results.append(course)

    return results

# Function to return course data in the format required by Gradio
def find_courses(query):
    results = search_courses(query)
    formatted_results = []

    if results:  # If results are found
        for result in results:
            formatted_results.append(
                f"<h3>{result['title']}</h3><p>{result['description']}</p><a href='{result['link']}'>Link to Course</a><br>"
            )
    else:
        formatted_results.append("<p>No courses found with that keyword.</p>")

    return "".join(formatted_results)  # Return as HTML

# Modify the output to 'html' in the Gradio interface
interface = gr.Interface(
    fn=find_courses,
    inputs=gr.Textbox(label="Search for Courses"),
    outputs="html",  # Changed to 'html' for a cleaner display
    title="Smart Course Search Tool",
    description="Enter a keyword to find relevant free courses on Analytics Vidhya."
)

if __name__ == "__main__":
    interface.launch()
