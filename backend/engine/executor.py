import subprocess
import tempfile
import os

def execute_function_engine(function):
    """
    Executes the given function code in an isolated environment.

    Args:
        function (object): The function object containing code, language, etc.

    Returns:
        dict: Execution result containing output or error.
    """
    if function.language == "Python":
        # Create a temporary file for the Python code
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_file.write(function.code.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            # Execute the Python code using subprocess
            result = subprocess.run(
                ["python3", temp_file_path],
                capture_output=True,
                text=True,
                timeout=function.timeout
            )
            if result.returncode == 0:
                return {"output": result.stdout.strip()}
            else:
                return {"error": result.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {"error": "Execution timed out"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            # Clean up the temporary file
            os.remove(temp_file_path)

    elif function.language == "JavaScript":
        # Create a temporary file for the JavaScript code
        with tempfile.NamedTemporaryFile(suffix=".js", delete=False) as temp_file:
            temp_file.write(function.code.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            # Execute the JavaScript code using Node.js
            result = subprocess.run(
                ["node", temp_file_path],
                capture_output=True,
                text=True,
                timeout=function.timeout
            )
            if result.returncode == 0:
                return {"output": result.stdout.strip()}
            else:
                return {"error": result.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {"error": "Execution timed out"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            # Clean up the temporary file
            os.remove(temp_file_path)

    else:
        return {"error": f"Unsupported language: {function.language}"}