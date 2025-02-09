import json

def find_questions(data, questions_found=None):
    if questions_found is None:
        questions_found = []
    
    if isinstance(data, dict):
        # Check if current dict is a Question section
        if "Question" in data:
            question_data = data["Question"]
            # Extract Title and Instruction if they exist
            if isinstance(question_data, dict):
                title = question_data.get('Title')
                instruction = question_data.get('Instruction')
                if title or instruction:
                    questions_found.append({
                        'Title': title,
                        'Instruction': instruction
                    })
        
        # Recursively search through all dictionary values
        for value in data.values():
            find_questions(value, questions_found)
    
    # If it's a list, search through all items
    elif isinstance(data, list):
        for item in data:
            find_questions(item, questions_found)
            
    return questions_found

def display_questions_info(file_path):
    try:
        # Open and load the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Find all Question sections
        questions = find_questions(data)
        
        # Display the results
        if not questions:
            print("No Question sections found in the JSON file.")
            return
            
        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i}:")
            print(f"Title: {question['Title'] if question['Title'] else 'No title available'}")
            print(f"Instruction: {question['Instruction'] if question['Instruction'] else 'No instruction available'}")
            print("-" * 50)
            
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
file_path = 'sample_evaluation_form.json'
display_questions_info(file_path)