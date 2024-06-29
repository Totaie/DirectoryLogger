import os
import re

# Define the log file path
log_file = r'E:\Folders\Coding\Python\Directory Logger\directory_changes.log'

def get_next_version(current_version):
    major, minor, patch = map(int, current_version.split('.'))
    patch += 1
    return f"{major}.{minor}.{patch}"

def update_log_with_versions(log_file):
    with open(log_file, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    entry_lines = []
    inside_entry = False
    current_version = "1.0.0"  # Start with the initial version

    for line in lines:
        if line.startswith("[") and "Changes detected in" in line:
            if inside_entry and entry_lines:
                # At the end of an entry, add the version and insert it above the FPS line
                for i in range(len(entry_lines)):
                    if entry_lines[i].startswith("FPS:"):
                        entry_lines.insert(i, f"Version: {current_version}\n")
                        break
                updated_lines.extend(entry_lines)
                entry_lines = []
                current_version = get_next_version(current_version)  # Increment version
            inside_entry = True
        
        if inside_entry:
            entry_lines.append(line)
        else:
            updated_lines.append(line)
    
    # Append the last entry
    if inside_entry and entry_lines:
        for i in range(len(entry_lines)):
            if entry_lines[i].startswith("FPS:"):
                entry_lines.insert(i, f"Version: {current_version}\n")
                break
        updated_lines.extend(entry_lines)

    with open(log_file, 'w') as f:
        f.writelines(updated_lines)

if __name__ == "__main__":
    if os.path.exists(log_file):
        update_log_with_versions(log_file)
        print(f"Log updated with versions in {log_file}")
    else:
        print(f"Error: {log_file} does not exist.")
