import os
import shutil

def archive_folder(folder_name, output_archive_name, milestone_index):
    if not os.path.exists(folder_name):
        print(f"Folder '{folder_name}' not found.")
        return

    zip_path = f"{output_archive_name}.zip"
    if os.path.exists(zip_path):
        try:
            os.remove(zip_path)
            print(f"Old archive '{zip_path}' has been removed.")
        except Exception as e:
            print(f"Error while deleting old archive: {e}")
            return

    temp_dir = os.path.join(os.path.dirname(output_archive_name), "_temp_archive")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        temp_folder_path = os.path.join(temp_dir, os.path.basename(folder_name))
        shutil.copytree(folder_name, temp_folder_path)

        if milestone_index:
            init_file_path = os.path.join(temp_folder_path, "__init__.py")
            if os.path.exists(init_file_path):
                with open(init_file_path, "r+") as init_file:
                    lines = init_file.readlines()
                    if milestone_index.replace("_", "").isdigit():
                        lines.insert(16, f'    "warning": "This is Milestone {milestone_index}",\n')
                        lines.insert(46, f'        "Milestone": "{milestone_index}",\n')
                    elif isinstance(milestone_index, str):
                        lines.insert(45, f'        "Index": "{milestone_index.capitalize()}",\n')
                    init_file.seek(0)
                    init_file.writelines(lines)
            else:
                print(f"File '__init__.py' not found in folder '{folder_name}'.")


        shutil.make_archive(output_archive_name, 'zip', temp_dir)
        print(f"Folder '{folder_name}' successfully archived to '{output_archive_name}.zip'.")
    except Exception as e:
        print(f"Error during archiving: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    source_folder = "MiBlend_Source"
    archive_name = "MiBlend"

    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    folder_path = os.path.join(current_dir, source_folder)
    output_archive_path = os.path.join(current_dir, archive_name)

    milestone_index = input("Milestone or Index ? \n")

    archive_folder(folder_path, output_archive_path, milestone_index)
