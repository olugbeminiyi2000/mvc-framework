import os

def render_template(template_name: str, data: dict) -> str:
    """
    Renders a template from the enforced 'static/' directory by replacing placeholders with values in `data`.

    Args:
        template_name (str): The name of the template file (must be inside 'static/').
        data (dict): A dictionary containing data to be replaced in the template.

    Returns:
        str: The rendered template as a string.

    Raises:
        FileNotFoundError: If the template file does not exist.
        ValueError: If the template name attempts to escape the 'static/' directory.
    """
    # Enforce static directory
    static_dir = os.path.join(os.getcwd(), "static")  # Ensures absolute path
    if ".." in template_name or template_name.startswith("/"):
        raise ValueError("Invalid template name. Template must be inside 'static/' and not use '..' to escape.")

    # Construct the full template file path
    filepath = os.path.join(static_dir, template_name)
    print(filepath)

    print(f"Looking for template: {filepath}")

    # Check if file exists
    if not os.path.exists(filepath):
        print("failed in finding file path")
        raise FileNotFoundError(f"Template '{template_name}' not found in 'static/' directory.")

    try:
        # Read the template file content
        with open(filepath, 'r') as file:
            file_string = file.read()

        # Replace placeholders with values from data
        for key, value in data.items():
            placeholder = f"{{{{ {key} }}}}"  # Correct format for placeholders
            file_string = file_string.replace(placeholder, str(value))

        print("Template successfully rendered.")
        return file_string

    except Exception as e:
        print("failed")
        raise ValueError(f"Error rendering template: {e}")
