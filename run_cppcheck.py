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

# cppcheck 2.18.0
# https://github.com/danmar/cppcheck/tree/2.18.x

import os
import sys
import subprocess
import argparse
import tempfile
import json
from typing import List, Optional


# Reference: https://google.github.io/styleguide/cppguide.html#Naming
NAMING_CONFIG_JSON = r"""
{
  "RE_FILE": ["[a-z][a-z0-9_]*\\.(cpp|cc|cxx|c|h|hpp|hxx)\\Z"],
  "RE_NAMESPACE": ["[a-z][a-z0-9_]*\\Z"],
  "RE_VARNAME": ["[a-z][a-z0-9_]*\\Z"],
  "RE_PRIVATE_MEMBER_VARIABLE": ["[a-z][a-z0-9_]*_\\Z"],
  "RE_PUBLIC_MEMBER_VARIABLE": ["[a-z][a-z0-9_]*\\Z"],
  "RE_GLOBAL_VARNAME": ["[a-z][a-z0-9_]*\\Z"],
  "RE_FUNCTIONNAME": ["[A-Z][a-zA-Z0-9]*\\Z"],
  "RE_CLASS_NAME": ["[A-Z][a-zA-Z0-9]*\\Z"],
  "include_guard": {},
  "var_prefixes": {},
  "function_prefixes": {},
  "skip_one_char_variables": false
}
"""


def _create_temp_naming_config_json() -> str:
    """Create a temporary naming configuration JSON file.

    Returns:
        Path to the temporary configuration file.
    """
    fd, config_path = tempfile.mkstemp(suffix=".json", prefix="namingng_config_")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(NAMING_CONFIG_JSON.strip())
        return config_path
    except Exception as e:
        os.close(fd)
        if os.path.exists(config_path):
            os.unlink(config_path)
        raise RuntimeError(f"Failed to create temporary config file: {e}") from e


def _validate_addon_path(addon_path: str) -> str:
    """Validate and normalize the addon path.

    Arguments:
        addon_path: Path to the namingng.py addon.

    Returns:
        Absolute path to the addon.

    Raises:
        RuntimeError: If the addon file does not exist or is invalid.
    """
    abs_path = os.path.abspath(addon_path)
    if not os.path.exists(abs_path):
        raise RuntimeError(f"Addon file not found: {addon_path}")
    if not os.path.isfile(abs_path):
        raise RuntimeError(f"Addon path is not a file: {addon_path}")
    if not abs_path.endswith(".py"):
        raise RuntimeError(f"Addon file must be a Python file: {addon_path}")
    return abs_path


def _build_cppcheck_command(
    cppcheck_path: str,
    source_paths: List[str],
    addon_path: str,
    enable: str,
    jobs: Optional[int],
    suppress: List[str],
    include_paths: List[str],
    defines: List[str],
    undefines: List[str],
    platform: Optional[str],
    std: Optional[str],
    output_format: str,
    quiet: bool,
    force: bool,
    inline_suppr: bool,
    verbose: bool,
) -> List[str]:
    """Build cppcheck command line arguments.

    Arguments:
        cppcheck_path: Path to cppcheck source directory.
        source_paths: List of source files or directories to check.
        addon_path: Path to namingng.py addon JSON configuration file.
        enable: Enable checks, e.g., "all", "style", "warning".
        jobs: Number of parallel jobs, None for auto.
        suppress: List of suppressions.
        include_paths: List of include directories.
        defines: List of preprocessor definitions.
        undefines: List of preprocessor undefines.
        platform: Platform configuration file.
        std: C++ standard, e.g., "c++11", "c++17".
        output_format: Output format, e.g., "gcc", "vs7", "checkstyle".
        quiet: Suppress progress output.
        force: Force checking all configurations.
        inline_suppr: Enable inline suppressions.

    Returns:
        List of command line arguments for cppcheck.
    """
    cmd = [os.path.join(cppcheck_path, "cppcheck")]

    if enable:
        cmd.append(f"--enable={enable}")

    if jobs is not None:
        cmd.extend(["-j", str(jobs)])

    for sup in suppress:
        cmd.append(f"--suppress={sup}")

    for inc in include_paths:
        cmd.extend(["-I", inc])

    for define in defines:
        cmd.append(f"-D{define}")

    for undef in undefines:
        cmd.append(f"-U{undef}")

    if platform:
        cmd.append(f"--platform={platform}")

    if std:
        cmd.append(f"--std={std}")
        if std.startswith("c++"):
            cmd.append("--language=c++")

    if output_format:
        cmd.append(f"--template={output_format}")

    if force:
        cmd.append("--force")

    if inline_suppr:
        cmd.append("--inline-suppr")

    if quiet:
        cmd.append("--quiet")

    # Exit with error code 1 if any errors are found
    cmd.append("--error-exitcode=1")

    cmd.append(f"--addon={addon_path}")

    cmd.extend(source_paths)

    if verbose:
        cmd.extend(["--verbose"])
        print(f"cppcheck command: {' '.join(cmd)}", file=sys.stderr)

    return cmd


def run_cppcheck(
    source_paths: List[str],
    namingng_path: str,
    cppcheck_path: str,
    enable: str = "all",
    jobs: Optional[int] = None,
    suppress: Optional[List[str]] = None,
    include_paths: Optional[List[str]] = None,
    defines: Optional[List[str]] = None,
    undefines: Optional[List[str]] = None,
    platform: Optional[str] = None,
    std: Optional[str] = None,
    output_format: str = "gcc",
    quiet: bool = False,
    force: bool = False,
    inline_suppr: bool = False,
    verbose: bool = False,
) -> int:
    """Run cppcheck with namingng.py addon.

    Arguments:
        source_paths: List of source files or directories to check.
        namingng_path: Path to namingng.py addon file.
        cppcheck_path: Path to cppcheck source directory.
        enable: Enable checks, default "all".
        jobs: Number of parallel jobs, None for auto.
        suppress: List of suppressions.
        include_paths: List of include directories.
        defines: List of preprocessor definitions.
        undefines: List of preprocessor undefines.
        platform: Platform configuration file.
        std: C++ standard.
        output_format: Output format.
        quiet: Suppress progress output.
        force: Force checking all configurations.
        inline_suppr: Enable inline suppressions.
        verbose: Print command before execution.

    Returns:
        Exit code from cppcheck, 0 for success, non-zero for errors.
    """
    validated_addon_path = _validate_addon_path(namingng_path)

    temp_config = _create_temp_naming_config_json()
    namingng_addon_json = None

    try:
        addon_dir = os.path.dirname(validated_addon_path)
        
        namingng_addon_json = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            prefix="namingng_addon_",
            delete=False,
            dir=addon_dir
        )
        namingng_addon_json_path = namingng_addon_json.name
        namingng_addon_json.close()
        
        addon_config = {
            "script": validated_addon_path,
            "args": [f"--configfile={temp_config}"]
        }
        
        with open(namingng_addon_json_path, "w") as f:
            json.dump(addon_config, f)
        
        cmd = _build_cppcheck_command(
            cppcheck_path=cppcheck_path,
            source_paths=source_paths,
            addon_path=namingng_addon_json_path,
            enable=enable,
            jobs=jobs,
            suppress=suppress or [],
            include_paths=include_paths or [],
            defines=defines or [],
            undefines=undefines or [],
            platform=platform,
            std=std,
            output_format=output_format,
            quiet=quiet,
            force=force,
            inline_suppr=inline_suppr,
            verbose=verbose,
        )

        if verbose:
            print(f"Running: {' '.join(cmd)}", file=sys.stderr)

        result = subprocess.run(cmd, cwd=os.getcwd())

        return result.returncode
    finally:
        if temp_config and os.path.exists(temp_config):
            os.unlink(temp_config)
        if namingng_addon_json_path and os.path.exists(namingng_addon_json_path):
            os.unlink(namingng_addon_json_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run cppcheck with namingng.py addon for code style checking")

    parser.add_argument(
        "source_paths",
        nargs="+",
        help="Source files or directories to check",
    )

    parser.add_argument(
        "--namingng-path",
        required=True,
        help="Path to namingng.py addon file",
    )

    parser.add_argument(
        "--cppcheck-path",
        dest="cppcheck_path",
        required=True,
        help="Path to cppcheck source directory, used to locate cppcheckdata.py module",
    )

    parser.add_argument(
        "--enable",
        default="style",
        help='Enable checks, default "style"',
    )

    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        help="Number of parallel jobs, default auto",
    )

    parser.add_argument(
        "--suppress",
        action="append",
        dest="suppress",
        help="Suppress specific warnings, can be used multiple times",
    )

    parser.add_argument(
        "-I",
        "--include",
        action="append",
        dest="include_paths",
        help="Include directory, can be used multiple times",
    )

    parser.add_argument(
        "-D",
        "--define",
        action="append",
        dest="defines",
        help="Preprocessor definition, can be used multiple times",
    )

    parser.add_argument(
        "-U",
        "--undefine",
        action="append",
        dest="undefines",
        help="Undefine preprocessor macro, can be used multiple times",
    )

    parser.add_argument(
        "--platform",
        help="Platform configuration file",
    )

    parser.add_argument(
        "--std",
        help="Set standard, e.g., c89, c99, c11, c++03, c++11, c++14, c++17, c++20",
    )

    parser.add_argument(
        "--template",
        dest="output_format",
        default="gcc",
        help='Output format template, default "gcc"',
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force checking all configurations",
    )

    parser.add_argument(
        "--inline-suppr",
        action="store_true",
        help="Enable inline suppressions",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print command before execution",
    )

    args = parser.parse_args()

    try:
        return run_cppcheck(
            source_paths=args.source_paths,
            namingng_path=args.namingng_path,
            cppcheck_path=args.cppcheck_path,
            enable=args.enable,
            jobs=args.jobs,
            suppress=args.suppress,
            include_paths=args.include_paths,
            defines=args.defines,
            undefines=args.undefines,
            platform=args.platform,
            std=args.std,
            output_format=args.output_format,
            quiet=args.quiet,
            force=args.force,
            inline_suppr=args.inline_suppr,
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
