import os
import json
import re

def parse_course_info(course_data):
    """
    Parse course information and extract separate components.
    
    Args:
        course_data (dict): Dictionary containing course title and description
    
    Returns:
        dict: Parsed course information with separated components
    """
    # Extract the full title
    full_title = course_data['title']
    
    # Use regex to separate department, class code, title, and units
    # Regex explanation:
    # - Capture group 1 (\w+): Matches department (letters)
    # - Capture group 2 (\d+): Matches course number
    # - Capture group 3 (.*?): Matches course title (non-greedy)
    # - Capture group 4 (\d+): Matches number of units
    match = re.match(r'([\w\s]+)\s+(\d+)\.\s*(.*?)\.\s*(\d+)\s*Units\.', full_title)
    
    if not match:
        raise ValueError(f"Could not parse course title: {full_title}")
    
    parsed_course = {
        'department': match.group(1).strip(),
        'class_code': f"{match.group(1).strip()} {match.group(2)}",
        'class_title': match.group(3).strip(),
        'units': f"{match.group(4)} Units",
        'description': course_data['desc']
    }
    
    return parsed_course

def parse_allcourses_json(directory_path):
    """
    Parse the allcourse.json file in the specified directory.
    
    Args:
        directory_path (str): Path to the directory containing allcourse.json
    
    Returns:
        list: List of parsed course information
    """
    # Construct the full path to allcourse.json
    file_path = os.path.join(directory_path, 'allcourse.json')
    
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as file:
            courses_data = json.load(file)
        
        # Parse each course
        parsed_courses = []
        for course_data in courses_data:
            try:
                parsed_course = parse_course_info(course_data)
                parsed_courses.append(parsed_course)
            except ValueError as e:
                print(f"Error parsing course: {e}")
        
        # Write parsed courses to a new JSON file
        output_path = os.path.join(directory_path, 'parsed_courses.json')
        with open(output_path, 'w', encoding='utf-8') as outfile:
            json.dump(parsed_courses, outfile, indent=2)
        
        print(f"Parsed courses saved to {output_path}")
        
        return parsed_courses
    
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {file_path}")
        return []

# Specify the directory path
directory_path = '/Users/tsaially/Desktop/Classes/CSDS 393/project/CSDS393-Project/scrape'

# Parse allcourse.json and create parsed_courses.json
parsed_courses = parse_allcourses_json(directory_path)

# Optionally, print parsed courses
for course in parsed_courses:
    print("\nCourse Information:")
    for key, value in course.items():
        print(f"{key.replace('_', ' ').title()}: {value}")