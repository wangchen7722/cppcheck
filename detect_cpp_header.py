# Copyright (c) 2025 vivo Mobile Communication Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Detect if a header file is C or C++ based on code features

import os
import sys
import re
import argparse
from typing import List, Optional, Tuple


# C++ keywords and features that indicate C++ code
CPP_KEYWORDS = {
    "namespace",
    "class",
    "template",
    "using",
    "new",
    "delete",
    "virtual",
    "public",
    "private",
    "protected",
    "constexpr",
    "noexcept",
    "override",
    "final",
    "explicit",
    "operator",
    "friend",
    "mutable",
    "volatile",
    "typename",
    "this",
    "nullptr",
    "static_cast",
    "dynamic_cast",
    "const_cast",
    "reinterpret_cast",
}

# C++ patterns that indicate C++ code
CPP_PATTERNS = [
    r"\bstd::",  # std namespace
    r"::\w+",  # Scope resolution operator
    r"template\s*<",  # Template declaration
    r"class\s+\w+",  # Class declaration
    r"namespace\s+\w+",  # Namespace declaration
    r"using\s+namespace",  # Using namespace
    r"public\s*:",  # Public access modifier
    r"private\s*:",  # Private access modifier
    r"protected\s*:",  # Protected access modifier
    r"virtual\s+\w+",  # Virtual function
    r"operator\s*[+\-*/=<>!&|^%\[\]()]",  # Operator overloading
    r"constexpr\s+",  # Constexpr
    r"noexcept\s*[\(;]",  # Noexcept
    r"override\s*[;]",  # Override
    r"final\s*[;:]",  # Final
    r"->\s*\w+",  # Arrow operator (member access)
    r"std::\w+",  # Standard library types
]


def is_cpp_keyword_in_code(line: str) -> bool:
    """Check if line contains C++ keywords in code context.

    Arguments:
        line: Line of code to check.

    Returns:
        True if C++ keyword is found in code context, False otherwise.
    """
    cleaned_line = remove_comments_and_strings(line)
    
    # Check for C++ keywords
    words = re.findall(r"\b\w+\b", cleaned_line)
    for word in words:
        if word in CPP_KEYWORDS:
            return True
    
    return False


def remove_comments_and_strings(line: str) -> str:
    """Remove comments and string literals from a line.

    Arguments:
        line: Line of code to process.

    Returns:
        Line with comments and string literals replaced with spaces.
    """
    in_string = False
    in_single_comment = False
    in_multi_comment = False
    cleaned = []
    i = 0
    
    while i < len(line):
        if in_multi_comment:
            if i < len(line) - 1 and line[i:i+2] == "*/":
                in_multi_comment = False
                i += 2
                continue
            i += 1
            continue
        
        if in_single_comment:
            i += 1
            continue
        
        if not in_string and i < len(line) - 1 and line[i:i+2] == "//":
            in_single_comment = True
            i += 2
            continue
        
        if not in_string and i < len(line) - 1 and line[i:i+2] == "/*":
            in_multi_comment = True
            i += 2
            continue
        
        if line[i] in ('"', "'"):
            if not in_string:
                in_string = True
            elif i > 0 and line[i-1] != "\\":
                in_string = False
            cleaned.append(" ")
        else:
            cleaned.append(line[i])
        i += 1
    
    return "".join(cleaned)


def matches_cpp_pattern(line: str) -> bool:
    """Check if line matches C++ patterns.

    Arguments:
        line: Line of code to check.

    Returns:
        True if line matches C++ patterns, False otherwise.
    """
    cleaned_line = remove_comments_and_strings(line)
    for pattern in CPP_PATTERNS:
        if re.search(pattern, cleaned_line):
            return True
    return False


def detect_cpp_features(file_path: str) -> Tuple[bool, List[str]]:
    """Detect C++ features in a header file.

    Arguments:
        file_path: Path to the header file.

    Returns:
        Tuple of (is_cpp, evidence_list) where is_cpp indicates if file is C++,
        and evidence_list contains lines that indicate C++ features.
    """
    if not os.path.exists(file_path):
        raise RuntimeError(f"File not found: {file_path}")
    
    if not os.path.isfile(file_path):
        raise RuntimeError(f"Path is not a file: {file_path}")
    
    evidence = []
    cpp_features_found = 0
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                # Check for C++ keywords
                if is_cpp_keyword_in_code(line):
                    evidence.append(f"{file_path}:{line_num}: C++ keyword found: {line.strip()}")
                    cpp_features_found += 1
                
                # Check for C++ patterns
                if matches_cpp_pattern(line):
                    evidence.append(f"{file_path}:{line_num}: C++ pattern found: {line.strip()}")
                    cpp_features_found += 1
    except Exception as e:
        raise RuntimeError(f"Error reading file {file_path}: {e}") from e
    
    is_cpp = cpp_features_found > 0
    
    return is_cpp, evidence


def detect_cpp_headers(
    file_paths: List[str],
    verbose: bool = False,
    show_evidence: bool = False,
) -> Tuple[List[str], List[str]]:
    """Detect C++ headers from a list of header files.

    Arguments:
        file_paths: List of header file paths to check.
        verbose: If True, print detailed information.
        show_evidence: If True, show evidence for each file.

    Returns:
        Tuple of (cpp_files, c_files) containing lists of C++ and C header files.
    """
    cpp_files = []
    c_files = []
    
    for file_path in file_paths:
        try:
            is_cpp, evidence = detect_cpp_features(file_path)
            
            if is_cpp:
                cpp_files.append(file_path)
                if verbose:
                    print(f"C++: {file_path}", file=sys.stderr)
                if show_evidence:
                    for ev in evidence[:3]:  # Show first 3 pieces of evidence
                        print(f"  {ev}", file=sys.stderr)
            else:
                c_files.append(file_path)
                if verbose:
                    print(f"C:   {file_path}", file=sys.stderr)
        except RuntimeError as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
            continue
    
    return cpp_files, c_files


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect if header files are C or C++ based on code features")
    
    parser.add_argument(
        "header_files",
        nargs="+",
        help="Header files to check",
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed information for each file",
    )
    
    parser.add_argument(
        "--show-evidence",
        action="store_true",
        help="Show evidence for C++ detection",
    )
    
    parser.add_argument(
        "--output-cpp",
        help="Output file to write C++ header file paths, one per line",
    )
    
    parser.add_argument(
        "--output-c",
        help="Output file to write C header file paths, one per line",
    )
    
    args = parser.parse_args()
    
    try:
        cpp_files, c_files = detect_cpp_headers(
            args.header_files,
            verbose=args.verbose,
            show_evidence=args.show_evidence,
        )
        
        if args.output_cpp:
            with open(args.output_cpp, "w") as f:
                for file_path in cpp_files:
                    print(file_path, file=f)
        
        if args.output_c:
            with open(args.output_c, "w") as f:
                for file_path in c_files:
                    print(file_path, file=f)
        
        if not args.verbose:
            for file_path in cpp_files:
                print(f"C++: {file_path}")
            for file_path in c_files:
                print(f"C:   {file_path}")
        
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

