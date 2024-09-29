import re
import os

# Regular expressions to match C++ vector access patterns
vector_access_pattern = r'\b([a-zA-Z_]\w*)\s*\[\s*(\d+)\s*\]'   # matches vec[5]
vector_at_pattern = r'\b([a-zA-Z_]\w*)\.at\s*\(\s*(\d+)\s*\)'    # matches vec.at(5)
vector_empty_check_pattern = r'\b([a-zA-Z_]\w*)\.empty\s*\(\s*\)'  # matches vec.empty()

def check_vector_access(file_lines):
    """
    Check for vector access patterns and warn about potential out-of-range risks
    or missing empty checks.
    """
    issues = []
    
    for line_num, line in enumerate(file_lines, start=1):
        # Find all vector access occurrences using `[]`
        access_matches = re.finditer(vector_access_pattern, line)
        for match in access_matches:
            vector_name = match.group(1)
            index = match.group(2)
            issues.append(f"Warning: Potential out-of-range access using '{vector_name}[{index}]' at line {line_num}")

        # Find all vector access occurrences using `.at()`
        at_matches = re.finditer(vector_at_pattern, line)
        for match in at_matches:
            vector_name = match.group(1)
            index = match.group(2)
            issues.append(f"Info: Safe access found using '{vector_name}.at({index})' at line {line_num}")

    return issues

def check_empty_before_access(file_lines):
    """
    Check if there's access to a vector without a corresponding empty() check.
    """
    issues = []
    vectors_accessed = set()

    # Collect vector accesses with their line numbers
    for line_num, line in enumerate(file_lines, start=1):
        access_matches = re.finditer(vector_access_pattern, line)
        for match in access_matches:
            vector_name = match.group(1)
            vectors_accessed.add((vector_name, line_num))

        at_matches = re.finditer(vector_at_pattern, line)
        for match in at_matches:
            vector_name = match.group(1)
            vectors_accessed.add((vector_name, line_num))

    # Check if empty() checks are present for the vectors
    for vector, line_num in vectors_accessed:
        empty_check_found = any(
            re.search(rf'\b{vector}\.empty\s*\(\s*\)', line)
            for line in file_lines
        )
        if not empty_check_found:
            issues.append(f"Warning: No empty() check found before accessing '{vector}' at line {line_num}")

    return issues

def analyze_cpp_file(file_path):
    """
    Analyze the C++ file for vector access issues.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        file_lines = file.readlines()

    issues = []
    issues += check_vector_access(file_lines)
    issues += check_empty_before_access(file_lines)

    if not issues:
        print(f"No issues found in {file_path}")
    else:
        print(f"Issues found in {file_path}:")
        for issue in issues:
            print(f"  {issue}")

def analyze_cpp_directory(directory_path):
    """
    Analyze all C++ files in the given directory for vector access issues.
    """
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.cpp') or file.endswith('.hpp') or file.endswith('.h'):
                file_path = os.path.join(root, file)
                analyze_cpp_file(file_path)

if __name__ == "__main__":
    directory_to_analyze = "path_to_your_cpp_files"
    analyze_cpp_directory(directory_to_analyze)
