# exp.py
import os
import pyperclip

# --- Configuration ---
# Directories to completely ignore. Add any others you need.
EXCLUDED_DIRS = {
    '.expo', 
    '.vscode', 
    'node_modules', 
    '__pycache__', 
    '.git',
    'assets' # Excluding assets folder as it contains binary images/fonts
}

# Specific individual files to ignore
EXCLUDED_FILES = {
    'package-lock.json', 
    '.gitignore',
    'exp.py' # Ignore the script itself
}

# File extensions to ignore (mostly binary or non-essential files)
EXCLUDED_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp',
    '.ttf', '.otf', '.woff', '.woff2',
    '.ico',
    '.zip', '.tar', '.gz'
}
# --- End of Configuration ---

def gather_project_context():
    """
    Traverses the project directory, gathers relevant source file contents,
    and returns a single formatted string.
    """
    output_blocks = []
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("Starting file traversal...")

    for root, dirs, files in os.walk(script_dir, topdown=True):
        # Modify dirs in-place to prevent os.walk from descending into excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for filename in sorted(files):
            # Check against exclusion lists
            if filename in EXCLUDED_FILES:
                continue
            if any(filename.endswith(ext) for ext in EXCLUDED_EXTENSIONS):
                continue

            file_path = os.path.join(root, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Create a clean, relative path for the header
                relative_path = os.path.relpath(file_path, script_dir)
                display_path = relative_path.replace(os.sep, '/')
                
                # Format the block for this file
                block = f"{display_path}\n----\n{content}\n\n______________"
                output_blocks.append(block)
                print(f"  + Added: {display_path}")

            except Exception as e:
                print(f"  - Skipped (error reading): {file_path} | Reason: {e}")

    # Join all the individual file blocks into one large string
    return "\n\n\n".join(output_blocks)

if __name__ == "__main__":
    print("Gathering project context. This may take a moment...")
    
    final_string = gather_project_context()
    
    if final_string:
        try:
            pyperclip.copy(final_string)
            print("\n✅ Success! Project context has been copied to your clipboard.")
        except pyperclip.PyperclipException:
            print("\n❌ Pyperclip Error: Could not access the clipboard.")
            print("This can happen in environments without a GUI (like SSH).")
            print("The script will now save the output to copy.txt for you to copy manually.")
            try:
                with open('copy.txt', 'w', encoding='utf-8') as f:
                    f.write(final_string)
                print("✅ Content saved to copy.txt")
            except Exception as e:
                print(f"❌ Error saving to copy.txt: {e}")
                print("Falling back to printing the output:")
                print("\n--- SCRIPT OUTPUT ---")
                print(final_string)
    else:
        print("\n⚠️ No files were found to copy. Check your EXCLUDED_DIRS and EXCLUDED_FILES configuration.")