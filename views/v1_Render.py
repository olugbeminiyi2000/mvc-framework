import json
import os


def render_template(template_path: str, template_name: str, data: dict) -> str:
    """
    Renders a template by replacing placeholders with the corresponding values in `data`.

    Args:
        template_path (str): The directory path to the template.
        template_name (str): The name of the template file.
        data (dict): A dictionary containing data to be replaced in the template.

    Returns:
        str: The rendered template as a string.
    """
    try:
        # Construct the full template file path
        filepath = os.path.join(template_path, template_name)
        
        # Check if file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Template '{template_name}' not found at {template_path}.")
        
        # Read the template file content
        with open(filepath, 'r') as file:
            file_string = file.read()

        # Replace placeholders with values from data
        for key, value in data.items():
            placeholder = f"{{{{ {key} }}}}"  # Ensure the correct format for placeholders
            file_string = file_string.replace(placeholder, str(value))

        # Clean up any leftover placeholders
        file_string = file_string.replace("{{", "").replace("}}", "")
        
        return file_string
    except Exception as e:
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
