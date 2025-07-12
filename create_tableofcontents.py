#!/usr/bin/env python3
"""Direct implementation to create table of contents - bypasses rate limit issues"""

import os
import json

def load_gitignore_patterns():
    """Load patterns from .gitignore file."""
    patterns = []
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def should_ignore(path, patterns):
    """Check if a path should be ignored based on gitignore patterns."""
    for pattern in patterns:
        if pattern.endswith('/'):
            if path.startswith(pattern) or ('/' + pattern) in path:
                return True
        elif pattern in path or path.endswith(pattern):
            return True
        elif '*' in pattern:
            import fnmatch
            if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
    return False

def list_files_recursive(directory="."):
    """Recursively list all files in directory respecting .gitignore."""
    gitignore_patterns = load_gitignore_patterns()
    all_files = []
    
    for root, dirs, files in os.walk(directory):
        # Remove directories that should be ignored
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), gitignore_patterns)]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            
            if not should_ignore(relative_path, gitignore_patterns):
                all_files.append(relative_path)
    
    return all_files

def describe_file(filepath):
    """Generate a description for a file based on its name and extension."""
    name = os.path.basename(filepath)
    ext = os.path.splitext(filepath)[1].lower()
    
    # Special files
    if name.lower() == 'readme.md':
        return "Main project documentation and overview"
    elif name.lower() == 'setup.py':
        return "Python package setup and installation configuration"
    elif name.lower() == 'requirements.txt':
        return "Python package dependencies list"
    elif name.lower() == '.gitignore':
        return "Git ignore patterns for version control"
    elif name.lower() == 'license':
        return "Project license terms and conditions"
    elif name.lower() == 'dockerfile':
        return "Docker container build instructions"
    
    # Python files
    elif ext == '.py':
        if 'test' in name.lower():
            return f"Test file - {name.replace('.py', '').replace('test_', '').replace('_', ' ')}"
        elif name == '__init__.py':
            return "Python package initialization file"
        elif name == 'cli.py':
            return "Command-line interface implementation"
        elif name == 'main.py':
            return "Main application entry point"
        else:
            return f"Python module - {name.replace('.py', '').replace('_', ' ')}"
    
    # Configuration files
    elif ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']:
        return f"Configuration file - {name.replace(ext, '').replace('_', ' ')}"
    
    # Documentation
    elif ext in ['.md', '.rst', '.txt']:
        if 'readme' in name.lower():
            return "Documentation file"
        else:
            return f"Documentation - {name.replace(ext, '').replace('_', ' ')}"
    
    # Web files
    elif ext in ['.html', '.css', '.js']:
        return f"Web asset - {ext[1:].upper()} file"
    
    # Data files
    elif ext in ['.csv', '.json', '.xml', '.sql']:
        return f"Data file - {ext[1:].upper()} format"
    
    # Default
    else:
        return f"File - {name}"

def create_tableofcontents():
    """Create a comprehensive table of contents for the project."""
    print("🚀 Creating table of contents...")
    
    # Get all files
    all_files = list_files_recursive()
    print(f"Found {len(all_files)} files")
    
    # Create table of contents content
    content = []
    content.append("# Grok CLI - Project Table of Contents")
    content.append("")
    content.append("This is an automated table of contents for the Grok CLI project.")
    content.append("")
    content.append("## Project Structure")
    content.append("")
    
    # Group files by directory
    dirs = {}
    for file in sorted(all_files):
        dir_name = os.path.dirname(file) if os.path.dirname(file) else "."
        if dir_name not in dirs:
            dirs[dir_name] = []
        dirs[dir_name].append(file)
    
    # Generate content
    for dir_name in sorted(dirs.keys()):
        if dir_name == ".":
            content.append("### Root Directory")
        else:
            content.append(f"### {dir_name}/")
        content.append("")
        
        for file in sorted(dirs[dir_name]):
            description = describe_file(file)
            content.append(f"- **{os.path.basename(file)}** - {description}")
        content.append("")
    
    # Add summary
    content.append("## Summary")
    content.append("")
    content.append(f"Total files: {len(all_files)}")
    
    # Count by type
    py_files = [f for f in all_files if f.endswith('.py')]
    test_files = [f for f in py_files if 'test' in f.lower()]
    config_files = [f for f in all_files if any(f.endswith(ext) for ext in ['.json', '.yaml', '.yml', '.toml', '.ini'])]
    
    content.append(f"Python files: {len(py_files)}")
    content.append(f"Test files: {len(test_files)}")
    content.append(f"Configuration files: {len(config_files)}")
    content.append("")
    content.append("Generated automatically by the Grok CLI project.")
    
    # Write to file
    with open("tableofcontents.md", "w") as f:
        f.write("\n".join(content))
    
    print("✅ Table of contents created successfully!")
    print("\nContent preview:")
    print("-" * 50)
    print("\n".join(content[:20]))
    if len(content) > 20:
        print("...")
    print("-" * 50)

if __name__ == "__main__":
    create_tableofcontents()
