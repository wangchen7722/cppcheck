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

# clang-format
# https://clang.llvm.org/docs/ClangFormat.html

import os
import sys
import subprocess
import argparse
import tempfile
from typing import List, Optional, Set
from pathlib import Path


# Reference: https://google.github.io/styleguide/cppguide.html
# Based on Google C++ Style Guide
# Customize options as needed while keeping Google style as base
CLANG_FORMAT_CONFIG_YAML = r"""
BasedOnStyle: Google
# Custom options can be added here, for example:
# IndentWidth: 2
# ColumnLimit: 80
# AccessModifierOffset: -1
"""


# Default file extensions for C/C++ files
DEFAULT_EXTENSIONS = {".cpp", ".cc", ".cxx", ".c", ".h", ".hpp", ".hxx", ".h++", ".c++"}


def _create_temp_clang_format_config() -> str:
    """Create a temporary clang-format configuration file.

    Returns:
        Path to the temporary configuration file.

    Raises:
        RuntimeError: If the configuration file cannot be created.
    """
    fd, config_path = tempfile.mkstemp(suffix=".clang-format", prefix="clang_format_config_")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(CLANG_FORMAT_CONFIG_YAML.strip())
        return config_path
    except Exception as e:
        os.close(fd)
        if os.path.exists(config_path):
            os.unlink(config_path)
        raise RuntimeError(f"Failed to create temporary config file: {e}") from e


def _validate_clang_format_path(clang_format_path: str) -> str:
    """Validate and normalize the clang-format executable path.

    Arguments:
        clang_format_path: Path to clang-format executable or directory.

    Returns:
        Absolute path to the clang-format executable.

    Raises:
        RuntimeError: If the clang-format executable is not found.
    """
    abs_path = os.path.abspath(clang_format_path)
    
    if os.path.isfile(abs_path):
        if not os.access(abs_path, os.X_OK):
            raise RuntimeError(f"clang-format is not executable: {abs_path}")
        return abs_path
    
    if os.path.isdir(abs_path):
        exe_path = os.path.join(abs_path, "clang-format")
        if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
            return exe_path
        raise RuntimeError(f"clang-format executable not found in directory: {abs_path}")
    
    raise RuntimeError(f"clang-format path is not a file or directory: {abs_path}")


def _collect_source_files(
    paths: List[str],
    extensions: Set[str],
    exclude: Optional[List[str]] = None,
) -> List[str]:
    """Collect all source files matching the given extensions.

    Arguments:
        paths: List of files or directories to process.
        extensions: Set of file extensions to include.
        exclude: List of patterns to exclude, None for no exclusions.

    Returns:
        List of absolute paths to source files.
    """
    source_files = []
    exclude_patterns = exclude or []
    
    for path in paths:
        abs_path = os.path.abspath(path)
        
        if os.path.isfile(abs_path):
            if any(abs_path.endswith(ext) for ext in extensions):
                if not _should_exclude(abs_path, exclude_patterns):
                    source_files.append(abs_path)
        elif os.path.isdir(abs_path):
            for root, dirs, files in os.walk(abs_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if any(file_path.endswith(ext) for ext in extensions):
                        if not _should_exclude(file_path, exclude_patterns):
                            source_files.append(file_path)
        else:
            print(f"Warning: Path does not exist: {abs_path}", file=sys.stderr)
    
    return sorted(set(source_files))


def _should_exclude(file_path: str, exclude_patterns: List[str]) -> bool:
    """Check if a file should be excluded based on patterns.

    Arguments:
        file_path: Absolute path to the file.
        exclude_patterns: List of patterns to match against.

    Returns:
        True if the file should be excluded, False otherwise.
    """
    if not exclude_patterns:
        return False
    
    for pattern in exclude_patterns:
        if pattern in file_path:
            return True
    
    return False


def _build_clang_format_command(
    clang_format_path: str,
    source_files: List[str],
    config_path: str,
    dry_run: bool,
    verbose: bool,
) -> List[str]:
    """Build clang-format command line arguments.

    Arguments:
        clang_format_path: Path to clang-format executable.
        source_files: List of source files to format.
        config_path: Path to clang-format configuration file.
        dry_run: If True, only check formatting without modifying files.
        verbose: If True, print verbose output.

    Returns:
        List of command line arguments for clang-format.
    """
    cmd = [clang_format_path]
    
    cmd.append(f"--style=file:{config_path}")
    
    if dry_run:
        cmd.append("--dry-run")
        cmd.append("--Werror")
    else:
        cmd.append("-i")
    
    if verbose:
        cmd.append("--verbose")
    
    cmd.extend(source_files)
    
    return cmd


def run_clang_format(
    source_paths: List[str],
    clang_format_path: str,
    extensions: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> int:
    """Run clang-format on source files.

    Arguments:
        source_paths: List of source files or directories to format.
        clang_format_path: Path to clang-format executable or directory.
        extensions: List of file extensions to process, None for defaults.
        exclude: List of patterns to exclude from processing.
        dry_run: If True, only check formatting without modifying files.
        verbose: If True, print verbose output.

    Returns:
        Exit code from clang-format, 0 for success, non-zero for errors.
    """
    validated_clang_format_path = _validate_clang_format_path(clang_format_path)
    
    file_extensions = set(extensions) if extensions else DEFAULT_EXTENSIONS
    
    source_files = _collect_source_files(source_paths, file_extensions, exclude)
    
    if not source_files:
        print("No source files found to format.", file=sys.stderr)
        return 0
    
    if verbose:
        print(f"Found {len(source_files)} file(s) to format.", file=sys.stderr)
    
    temp_config = None
    
    try:
        temp_config = _create_temp_clang_format_config()
        
        cmd = _build_clang_format_command(
            clang_format_path=validated_clang_format_path,
            source_files=source_files,
            config_path=temp_config,
            dry_run=dry_run,
            verbose=verbose,
        )
        
        if verbose:
            print(f"Running: {' '.join(cmd)}", file=sys.stderr)
        
        result = subprocess.run(cmd, cwd=os.getcwd())
        
        return result.returncode
    finally:
        if temp_config and os.path.exists(temp_config):
            os.unlink(temp_config)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run clang-format with Google C++ Style Guide configuration")
    
    parser.add_argument(
        "source_paths",
        nargs="+",
        help="Source files or directories to format",
    )
    
    parser.add_argument(
        "--clang-format-path",
        dest="clang_format_path",
        required=True,
        help="Path to clang-format executable or directory, e.g., /usr/bin or /usr/bin/clang-format",
    )
    
    parser.add_argument(
        "--extensions",
        action="append",
        help="File extensions to process, can be used multiple times, default: .cpp, .cc, .cxx, .c, .h, .hpp, .hxx",
    )
    
    parser.add_argument(
        "--exclude",
        action="append",
        help="Patterns to exclude from processing, can be used multiple times",
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check formatting without modifying files, exit with error if formatting issues found",
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output",
    )
    
    args = parser.parse_args()
    
    try:
        return run_clang_format(
            source_paths=args.source_paths,
            clang_format_path=args.clang_format_path,
            extensions=args.extensions,
            exclude=args.exclude,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

