import argparse
import sys
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.engine.executor import docker_executor

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_function_execution(code, language="python", timeout=10):
    """Simple wrapper to test function execution via CLI"""

    # Creating a simple function object
    class Function:
        pass

    fn = Function()
    fn.code = code
    fn.language = language
    fn.timeout = timeout

    # Use the existing executor
    result = docker_executor.execute_function(fn)
    return result


def main():
    parser = argparse.ArgumentParser(description="Test Docker function execution")
    parser.add_argument("--code", type=str, help="Code to execute")
    parser.add_argument("--file", type=str, help="File containing code to execute")
    parser.add_argument("--language", type=str, default="python",
                        choices=["python", "javascript"], help="Language runtime")
    parser.add_argument("--timeout", type=int, default=10, help="Execution timeout in seconds")

    args = parser.parse_args()

    code = args.code
    if args.file:
        with open(args.file, 'r') as f:
            code = f.read()

    if not code:
        parser.error("Either --code or --file must be provided")

    print(f"Executing {args.language} function with timeout {args.timeout}s...")
    result = test_function_execution(code, args.language, args.timeout)

    if "output" in result:
        print("\n--- OUTPUT ---")
        print(result["output"])
    elif "error" in result:
        print("\n--- ERROR ---")
        print(result["error"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
