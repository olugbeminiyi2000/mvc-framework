import json
import os
import re


def clean_unmatched_placeholders(template: str) -> str:
    return re.sub(r'{{\s*\w+\s*}}', '', template)



def render_template(template_name: str, data: dict) -> str:
    """
    Renders a template from the enforced 'templates/' directory by replacing placeholders with values in `data`.

    Args:
        template_name (str): The name of the template file (must be inside 'templates').
        data (dict): A dictionary containing data to be replaced in the template.

    Returns:
        str: The rendered template as a string.

    Raises:
        FileNotFoundError: If the template file does not exist.
        ValueError: If the template name attempts to escape the 'templates' directory.
    """
    # Enforce static directory
    static_dir = os.path.join(os.getcwd(), "templates") # Ensures absolute path
    if ".." in template_name or template_name.startswith("/"):
        raise ValueError("Invalid template name. Template must be inside 'templates/' and not use '..' to escape.")
    
    # Construct the full template file path
    filepath = os.path.join(static_dir, template_name)

    # Check if file exists
    if not os.path.exists(filepath):
        print("failed in finding file path")
        raise FileNotFoundError(f"Template '{template_name}' not found in 'templates/' directory.")

    try:
        # Read the template file content
        with open(filepath, 'r') as file:
            file_string = file.read()

        # Replace placeholders with values from data
        for key, value in data.items():
            pattern = re.compile(r'{{\s*' + re.escape(key) + r'\s*}}')
            file_string = pattern.sub(str(value), file_string)

        # clean unmatched place holders
        file_string = clean_unmatched_placeholders(file_string)

        print("Template successfully rendered.")
        return file_string

    except Exception as e:
        print("Failed to find render template.")
        raise ValueError(f"Error rendering template: {e}")

def render_json(data: dict) -> str:
    """
    Renders data as a JSON string.

    Args:
        data (dict): The data to be rendered as JSON.

    Returns:
        str: The data serialized to JSON.
    """
    try:
        return json.dumps(data)
    except TypeError as e:
        raise ValueError(f"Error rendering JSON: {e}")
