import os

def generate_md_structure(path, indent='', is_last=True, ignored_folders=set()):
    """
    Generate Markdown representation of directory structure recursively.

    Args:
    - path (str): Path to the directory.
    - indent (str): Indentation string.
    - is_last (bool): Whether the current item is the last in its parent directory.
    - ignored_folders (set): Set of folder names to ignore.
    """
    # Get the name of the current directory or file
    base_name = os.path.basename(path)
    
    # Check if the given path is a file
    if os.path.isfile(path):
        # Display file name in Markdown format
        print(indent + ('└── ' if is_last else '├── ') + base_name)
    else:
        # Display directory name in Markdown format
        print(indent + ('└── ' if is_last else '├── ') + '**' + base_name + '**/')
        
        # List all items in the directory
        items = os.listdir(path)
        # Sort the items alphabetically
        items.sort()
        # Loop through each item
        for i, item in enumerate(items):
            # Ignore specified folders
            if item in ignored_folders:
                continue
            # Determine whether the current item is the last in the directory
            is_last_item = i == len(items) - 1
            # Generate Markdown representation recursively for subdirectories and files
            generate_md_structure(os.path.join(path, item), indent + ('    ' if is_last else '│   '), is_last_item, ignored_folders)


# Example usage:
if __name__ == "__main__":
    # Specify the path to the directory
    directory_path = "/home/jayesh/ml/rag-chatbot"
     # Specify the folders to ignore
    ignored_folders = {'.git', '.next', 'Data', '__pycache__', 'node_modules', 'venv'}
    # Generate Markdown representation of the directory structure
    generate_md_structure(directory_path, ignored_folders=ignored_folders)
