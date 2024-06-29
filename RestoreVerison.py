import os
import json

# Set the directory where version snapshots are stored
snapshots_dir = r'VersionSnapshots'
current_directory = r'C:\Users\tatez\AppData\Roaming\com.modrinth.theseus\profiles\Final1.0.0_1.0.0\mods'

def list_versions():
    """
    Lists available version snapshots based on directories in `snapshots_dir`.
    """
    versions = os.listdir(snapshots_dir)
    return sorted(versions)

def select_version():
    """
    Allows the user to select a version to restore.
    """
    versions = list_versions()
    
    if not versions:
        print("No versions found.")
        return None
    
    print("Available Versions:")
    for idx, version in enumerate(versions):
        print(f"{idx}. {version}")
    
    try:
        choice = int(input("Enter the number of the version to restore: "))
        if 0 <= choice < len(versions):
            return versions[choice]
        else:
            print("Invalid choice.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None

def load_snapshot(version):
    """
    Loads the snapshot JSON file for the given version.
    """
    snapshot_file = os.path.join(snapshots_dir, version, f'directory_snapshot{version}.json')
    if os.path.exists(snapshot_file):
        with open(snapshot_file, 'r') as f:
            snapshot = json.load(f)
        
        # Remove the repetitive part of the directory path
        cleaned_snapshot = {}
        for path, mtime in snapshot.items():
            if os.path.splitdrive(path)[0] == os.path.splitdrive(current_directory)[0]:
                cleaned_snapshot[os.path.relpath(path, current_directory)] = mtime
            else:
                cleaned_snapshot[path.replace(current_directory + '\\', '')] = mtime
        
        return cleaned_snapshot
    return {}

def restore_files(current_directory, version):
    """
    Restores files from the specified version snapshot, managing .disabled extensions.
    """
    snapshot = load_snapshot(version)
    current_snapshot = snapshot_directory(current_directory)
    
    # Disable files not in snapshot
    for relpath in current_snapshot:
        if relpath not in snapshot:
            disable_file(os.path.join(current_directory, relpath))
    
    # Restore files from snapshot
    for relpath in snapshot:
        filepath = os.path.join(current_directory, relpath)
        if relpath not in current_snapshot:
            restore_file(filepath, current_directory)
        elif is_disabled(filepath):
            restored_filename = filepath[:-9]  # Remove .disabled suffix
            restore_file(restored_filename, current_directory)
    
    print(f"Files restored to version {version}.")

def snapshot_directory(directory):
    """
    Creates a snapshot dictionary of files in the directory.
    """
    snapshot = {}
    for root, dirs, files in os.walk(directory):
        for name in files:
            filepath = os.path.join(root, name)
            relpath = os.path.relpath(filepath, directory)
            snapshot[relpath] = os.path.getmtime(filepath)
    return snapshot

def disable_file(filepath):
    """
    Disables a file by adding .disabled to its name.
    """
    disabled_path = f"{filepath}.disabled"
    if os.path.exists(filepath) and not is_disabled(filepath):
        os.rename(filepath, disabled_path)
        print(f"Disabled: {filepath}")

def restore_file(filepath, current_directory):
    """
    Restores a disabled file by removing .disabled from its name if it exists.
    """
    restored_filename = os.path.basename(filepath)[:-9] if filepath.endswith('.disabled') else os.path.basename(filepath)
    restored_path = os.path.join(current_directory, restored_filename)
    try:
        os.rename(f"{filepath}.disabled", filepath)
        print(f"Restored: {restored_path}")
    except FileNotFoundError:
        print(f"Error: File '{os.path.basename(filepath)}' not found in '{current_directory}'.")
    except PermissionError as e:
        print(f"PermissionError: {e}")
    except OSError as e:
        print(f"Error renaming file: {e}")

def is_disabled(filepath):
    """
    Checks if a file is disabled (ends with .disabled).
    """
    return filepath.endswith('.disabled')

if __name__ == "__main__":
    versions = list_versions()
    if not versions:
        print("No version snapshots found.")
        exit(1)
    
    selected_version = select_version()
    if selected_version:
        restore_files(current_directory, selected_version)
