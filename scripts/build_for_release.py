import os
import shutil
from typing import Optional

# Constants
MILESTONE_INDEX_LINE = 48
DEFAULT_BUILD_TYPE = "auto"

def archive_folder(folder_name: str, output_archive_name: str, build_name: str, build_type: str) -> Optional[str]:
    """
    Archive a folder with specific build information.
    
    Args:
        folder_name: Path to the source folder
        output_archive_name: Name of the output archive without extension
        build_name: Name of the build
        build_type: Type of build ('m' for milestone, 'i' for index)
    
    Returns:
        Error message if operation fails, None if successful
    """
    if not os.path.exists(folder_name):
        return f"Folder '{folder_name}' not found."

    zip_path = f"{output_archive_name}.zip"
    temp_dir = os.path.join(os.path.dirname(output_archive_name), "_temp_archive")

    try:
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print(f"Old archive '{zip_path}' has been removed.")

        os.makedirs(temp_dir, exist_ok=True)
        temp_folder_path = os.path.join(temp_dir, os.path.basename(folder_name))
        shutil.copytree(folder_name, temp_folder_path)

        init_file_path = os.path.join(temp_folder_path, "__init__.py")
        if not os.path.exists(init_file_path):
            return f"File '__init__.py' not found in folder '{folder_name}'."

        with open(init_file_path, "r+") as init_file:
            lines = init_file.readlines()
            if build_type == "m":
                lines.insert(16, f'    "warning": "This is Milestone {build_name}",\n')
                lines.insert(MILESTONE_INDEX_LINE, f'            "Milestone": "{build_name}",\n')
            elif build_type == "i":
                lines.insert(MILESTONE_INDEX_LINE, f'            "Index": "{build_name.capitalize()}",\n')
            else:
                return f"Unknown build_type: {build_type}"
            init_file.seek(0)
            init_file.truncate()
            init_file.writelines(lines)

        shutil.make_archive(output_archive_name, 'zip', temp_dir)
        print(f"Folder '{folder_name}' successfully archived to '{output_archive_name}.zip'.")
        return None

    except Exception as e:
        return f"Error during archiving: {e}"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def is_milestone_name(name: str) -> bool:
    """Check if name contains both letters and numbers."""
    return any(c.isalpha() for c in name) and any(c.isdigit() for c in name)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder_path = os.path.join(current_dir, "MiBlend_Source")
    output_archive_path = os.path.join(current_dir, "MiBlend")

    build_type = input("Is This Milestone or Index ? m/i/auto (auto by default) \n").strip() or DEFAULT_BUILD_TYPE
    
    while True:
        build_name = input("Enter the Name of the Build: \n").strip()
        if build_name:
            break
        print("Build name cannot be empty")

    if build_type == "auto":
        build_type = "m" if is_milestone_name(build_name) else "i"
        while True:
            print(f"Build Type: {build_type}")
            if input("Is This Correct ? (yes by default) \n").strip().lower() in ['', 'y', 'yes']:
                break
            build_name = input("Enter New Build Name: \n").strip()
            if not build_name:
                continue
            build_type = "m" if is_milestone_name(build_name) else "i"

    if result := archive_folder(folder_path, output_archive_path, build_name, build_type):
        input(f"An Error Occurred: {result} \nPress Enter to Exit \n")
