from flask import Flask, render_template, request
import json
import re
from collections import OrderedDict

app = Flask(__name__)

# Define the route to render the UI
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle JSON file upload and processing
@app.route('/format-json', methods=['POST'])
def format_json():
    data = request.json.get('json')  # Get the uploaded JSON data

    # Process JSON data using the provided logic
    processed_data = process_json_data(data)

    # Reorder the fields based on the expected order
    reordered_data = reorder_fields(processed_data)

    # Use json.dumps to preserve order
    response_json = json.dumps(reordered_data, indent=2, ensure_ascii=False)
    return app.response_class(response=response_json, mimetype='application/json')

# Function to parse skills
def parse_skills(skills_str):
    if not skills_str or not isinstance(skills_str, str):
        return []
    return [skill.strip() for skill in skills_str.split(",") if skill.strip()]

# Function to parse projects
def parse_projects(projects_string):
    if not projects_string:
        return []

    lines = [line.strip() for line in projects_string.splitlines() if line.strip()]
    pair_regex = re.compile(r"(title|tittle|link)\s*[:\-]+\s*([^|]+?)(?=$|(title|tittle|link))", re.IGNORECASE)
    url_regex = re.compile(r"https?://\S+|[a-zA-Z0-9_.-]+\.[a-zA-Z]{2,}/?\S*")

    results = []
    current_project = {"title": None, "link": None}

    def push_current_if_valid():
        nonlocal current_project, results
        if current_project["title"] or current_project["link"]:
            title = current_project["title"] or f"Project {len(results) + 1}"
            link = current_project["link"] or ""
            results.append(OrderedDict([
                ("title", title),
                ("link", link)
            ]))
        current_project = {"title": None, "link": None}

    for line in lines:
        pairs = list(pair_regex.finditer(line))
        if pairs:
            last_end = 0
            for match in pairs:
                label = match.group(1).lower().strip()
                value = match.group(2).strip()
                if label.startswith("title"):
                    push_current_if_valid()
                    current_project["title"] = value
                elif label.startswith("link"):
                    if current_project["link"]:
                        push_current_if_valid()
                    current_project["link"] = value
                    if current_project["title"]:
                        push_current_if_valid()
                last_end = match.end()
            leftover = line[last_end:].strip()
            if leftover:
                murl = url_regex.search(leftover)
                if murl:
                    url_val = murl.group(0).strip()
                    if current_project["link"]:
                        push_current_if_valid()
                    current_project["link"] = url_val
                    if not current_project["title"]:
                        current_project["title"] = f"Project {len(results) + 1}"
                    push_current_if_valid()
        else:
            murl = url_regex.search(line)
            if murl:
                url_val = murl.group(0).strip()
                if current_project["link"]:
                    push_current_if_valid()
                current_project["link"] = url_val
                if not current_project["title"]:
                    current_project["title"] = f"Project {len(results) + 1}"
                push_current_if_valid()
            else:
                if not current_project["title"]:
                    current_project["title"] = line
                else:
                    if not current_project["link"]:
                        current_project["title"] += " " + line
                    else:
                        push_current_if_valid()
                        current_project["title"] = line
    push_current_if_valid()
    return results

# Function to process the input JSON data
def process_json_data(data):
    processed = []
    for record in data:
        record["skills"] = parse_skills(record.get("skills", ""))
        if "Projects" in record and isinstance(record["Projects"], str):
            record["Projects"] = parse_projects(record["Projects"])
        else:
            record["Projects"] = []

        if "overall_progress" in record and not isinstance(record["overall_progress"], str):
            record["overall_progress"] = str(record["overall_progress"]) + "%"

        if "total_coding_questions_solved" in record:
            record["total_coding_questions_solved"] = int(record["total_coding_questions_solved"])
        if "total_websites_built" in record:
            record["total_websites_built"] = int(record["total_websites_built"])
        if "total_learning_hours" in record:
            record["total_learning_hours"] = float(record["total_learning_hours"])

        if "phone" not in record:
            record["phone"] = None

        processed.append(record)
    return processed

# Function to reorder the fields based on the expected order
def reorder_fields(processed_data):
    field_order = [
        "name", "student_id", "skills", "Projects", "email", "linkedin_profile",
        "github_profile", "total_learning_hours", "total_coding_questions_solved",
        "total_websites_built", "overall_progress"
    ]
    reordered_data = []
    for record in processed_data:
        reordered_record = OrderedDict()
        for field in field_order:
            if field in record:
                reordered_record[field] = record[field]
        reordered_data.append(reordered_record)
    return reordered_data

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
