import os
import time
import json
import sys
import re

# Set the directory to monitor
directory_to_monitor = r'C:\Users\tatez\AppData\Roaming\com.modrinth.theseus\profiles\Final1.0.0_1.0.0\mods'

# Get the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))

def snapshot_directory(directory):
    snapshot = {}
    for root, dirs, files in os.walk(directory):
        for name in files:
            if not name.endswith('.disabled'):
                filepath = os.path.join(root, name)
                relpath = os.path.relpath(filepath, directory)  # Store relative paths
                snapshot[relpath] = os.path.getmtime(filepath)
    return snapshot

def remove_version_numbers(path):
    base_name = os.path.basename(path)
    cleaned_base_name = re.sub(r'([-+.]*(mc|build|\+|\d+\.\d+|\.\d+)[-+.]*)', '', base_name, flags=re.IGNORECASE)
    cleaned_base_name = re.sub(r'\d+|\.jar$', '', cleaned_base_name)
    return os.path.join(os.path.dirname(path), cleaned_base_name)

def detect_changes(old_snapshot, new_snapshot, base_directory):
    changes = []
    cleaned_old_snapshot = {remove_version_numbers(k): v for k, v in old_snapshot.items()}
    cleaned_new_snapshot = {remove_version_numbers(k): v for k, v in new_snapshot.items()}

    for path, mtime in cleaned_new_snapshot.items():
        if path not in cleaned_old_snapshot:
            changes.append(f"New file: {path}")
        elif cleaned_old_snapshot[path] != mtime:
            changes.append(f"Modified file: {path}")
    for path in cleaned_old_snapshot:
        if path not in cleaned_new_snapshot:
            changes.append(f"Deleted file: {path}")
    return changes

def load_snapshot(snapshot_file):
    if os.path.exists(snapshot_file):
        with open(snapshot_file, 'r') as f:
            return json.load(f)
    return {}

def save_snapshot(snapshot, snapshot_file):
    with open(snapshot_file, 'w') as f:
        json.dump(snapshot, f, indent=4)  # Added indent for better formatting

def get_current_version(version_file):
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            return f.read().strip()
    return "1.0.0"  # Start at 1.0.0 if the version file is missing or empty

def get_next_version(current_version):
    major, minor, patch = map(int, current_version.split('.'))
    patch += 1
    if patch >= 10:
        patch = 0
        minor += 1
    return f"{major}.{minor}.{patch}"

def save_current_version(version_file, version):
    with open(version_file, 'w') as f:
        f.write(version)

def main(directory):
    log_file = os.path.join(script_directory, 'directory_changes.log')
    version_file = os.path.join(script_directory, 'current_version.txt')
    snapshots_dir = os.path.join(script_directory, 'VersionSnapshots')
    
    if not os.path.exists(snapshots_dir):
        os.makedirs(snapshots_dir)

    old_snapshot = load_latest_snapshot(snapshots_dir)
    new_snapshot = snapshot_directory(directory)
    changes = detect_changes(old_snapshot, new_snapshot, directory)

    if changes:
        current_version = get_current_version(version_file)
        next_version = get_next_version(current_version)
        
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        version_snapshots_dir = os.path.join(snapshots_dir, current_version)
        if not os.path.exists(version_snapshots_dir):
            os.makedirs(version_snapshots_dir)
        
        snapshot_filename = os.path.join(version_snapshots_dir, f'directory_snapshot{current_version}.json')
        save_snapshot(new_snapshot, snapshot_filename)
        
        with open(log_file, 'a') as f:
            f.write(f"\n[{timestamp}] Changes detected in {directory}:\n")
            for change in changes:
                f.write(f"{change}\n")
            f.write(f"Version: {current_version}\n")
            fps = input("Avg FPS: ")  # Assuming you collect this during logging
            f.write(f"FPS: {fps}\n")
            note = input("Enter a note for this log: ")  # Assuming you collect this during logging
            f.write(f"Note: {note}\n")
        
        save_current_version(version_file, next_version)

def load_latest_snapshot(snapshots_dir):
    versions = os.listdir(snapshots_dir)
    if not versions:
        return {}
    
    latest_version = max(versions)
    latest_snapshot_file = os.path.join(snapshots_dir, latest_version, f'directory_snapshot{latest_version}.json')
    
    if os.path.exists(latest_snapshot_file):
        with open(latest_snapshot_file, 'r') as f:
            return json.load(f)
    
    return {}

if __name__ == "__main__":
    if not os.path.isdir(directory_to_monitor):
        print(f"Error: {directory_to_monitor} is not a valid directory.")
        sys.exit(1)
    
    main(directory_to_monitor)
