# backend/engine/executor.py
import tempfile
import os
import time
import docker
import logging
from pathlib import Path
import time
from backend.metrics import FUNCTION_EXECUTIONS, FUNCTION_EXECUTION_TIME, REQUEST_COUNT, REQUEST_LATENCY

logger = logging.getLogger(__name__)


class DockerExecutor:
    def __init__(self):
        self.client = docker.from_env()
        # Create base images if they don't exist
        self._ensure_base_images()

    def _ensure_base_images(self, retries=3):
        """Build base images with retry logic"""
        docker_dir = Path(__file__).parent.parent.parent / "docker"
        images = {
            "serverless-python": docker_dir / "python",
            "serverless-javascript": docker_dir / "javascript"
        }

        for image_name, image_path in images.items():
            # Verify requirements.txt exists for Python
            if image_name == "serverless-python":
                req_file = image_path / "requirements.txt"
                if not req_file.exists():
                    logger.warning(f"Creating empty {req_file}")
                    with open(req_file, 'w') as f:
                        f.write("# Auto-generated requirements file\n")

            for attempt in range(retries):
                try:
                    logger.info(f"Building {image_name} image, attempt {attempt + 1}/{retries}...")
                    # Build with network_mode=none to avoid networking issues
                    self.client.images.build(
                        path=str(image_path),
                        tag=f"{image_name}:latest",
                        quiet=False,
                        network_mode="host",
                        nocache=False
                    )
                    logger.info(f"Successfully built {image_name} image")
                    break
                except Exception as e:
                    logger.error(f"Failed to build {image_name} image: {str(e)}")
                    if attempt < retries - 1:
                        logger.info(f"Retrying in 2 seconds...")
                        time.sleep(2)  # Wait before retrying
                    else:
                        raise RuntimeError(f"Failed to build {image_name} after {retries} attempts")

    def execute_function(self, function):
        """Execute a function inside a Docker container"""
        if function.language.lower() == "python":
            return self._run_python_function(function)
        elif function.language.lower() == "javascript":
            return self._run_javascript_function(function)
        else:
            return {"error": f"Unsupported language: {function.language}"}

    def _run_python_function(self, function):
        # Create a temporary directory to mount in the container
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create function code file
            function_path = os.path.join(temp_dir, "function.py")
            with open(function_path, "w") as f:
                f.write(function.code)

            # Create empty requirements file if needed
            reqs_path = os.path.join(temp_dir, "requirements.txt")
            with open(reqs_path, "w") as f:
                f.write("# Function dependencies\n")

            # Execute in container
            return self._run_container(
                image="serverless-python:latest",
                mount_path=temp_dir,
                timeout=function.timeout
            )

    def _run_javascript_function(self, function):
        # Create a temporary directory to mount in the container
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create function code file
            function_path = os.path.join(temp_dir, "function.js")
            with open(function_path, "w") as f:
                f.write(function.code)

            # Execute in container
            return self._run_container(
                image="serverless-javascript:latest",
                mount_path=temp_dir,
                timeout=function.timeout
            )

    def _run_container(self, image, mount_path, timeout):
        """Run a container with the given parameters"""
        start_time = time.time()
        container = None

        try:
            # Try with network_disabled first (most reliable)
            container = self.client.containers.run(
                image=image,
                volumes={mount_path: {'bind': '/app', 'mode': 'ro'}},
                detach=True,
                network_disabled=True,  # Disable networking completely
                mem_limit='128m',  # Memory limit
                cpu_quota=100000,  # CPU limit (100% of 1 CPU)
                read_only=True  # Make filesystem read-only
            )

            # Wait for container with timeout
            try:
                result = container.wait(timeout=timeout)
                logs = container.logs().decode('utf-8')

                if result['StatusCode'] == 0:
                    return {"output": logs.strip()}
                else:
                    return {"error": logs.strip()}

            except Exception as e:
                # Handle timeout by forcibly stopping the container
                container.stop(timeout=1)
                return {"error": f"Execution timed out or failed: {str(e)}"}

        except Exception as e:
            logger.error(f"Docker execution error: {str(e)}")

            # Fallback to host networking if disabling network failed
            try:
                logger.info("Trying with host networking instead...")
                container = self.client.containers.run(
                    image=image,
                    volumes={mount_path: {'bind': '/app', 'mode': 'ro'}},
                    detach=True,
                    network_mode='host',
                    mem_limit='128m',
                    cpu_quota=100000,
                    read_only=True
                )

                result = container.wait(timeout=timeout)
                logs = container.logs().decode('utf-8')

                if result['StatusCode'] == 0:
                    return {"output": logs.strip()}
                else:
                    return {"error": logs.strip()}

            except Exception as fallback_error:
                logger.error(f"Fallback execution also failed: {str(fallback_error)}")
                return {"error": f"Container execution failed: {str(e)}\nFallback also failed: {str(fallback_error)}"}

        finally:
            # Cleanup: remove container
            try:
                if container:
                    container.remove(force=True)
            except Exception as cleanup_error:
                logger.warning(f"Container cleanup failed: {str(cleanup_error)}")

            execution_time = time.time() - start_time
            logger.info(f"Function execution took {execution_time:.2f} seconds")

    def run_container(self, image_name, command, **kwargs):
        # Try with network_disabled first, fallback to host networking
        try:
            return self.client.containers.run(
                image_name,
                command,
                network_disabled=True,
                remove=True,
                **kwargs
            )
        except Exception as e:
            logger.warning(f"Failed to run with network_disabled: {str(e)}")
            # Fallback to host networking
            return self.client.containers.run(
                image_name,
                command,
                network_mode='host',
                remove=True,
                **kwargs
            )


# Export a singleton for app-wide use
docker_executor = DockerExecutor()


def execute_function_engine(function):
    """
    Executes the given function code in a Docker container.

    Args:
        function (object): The function object containing code, language, etc.

    Returns:
        dict: Execution result containing output or error.
    """
    start_time = time.time()

    # Call the original function and store its result
    result = docker_executor.execute_function(function)

    # Calculate execution time
    execution_time = time.time() - start_time

    # Get function name or use default
    function_name = getattr(function, 'name', 'unnamed')

    # Determine execution status
    status = "error" if "error" in result else "success"

    # Record metrics
    FUNCTION_EXECUTIONS.labels(
        language=function.language,
        status=status
    ).inc()

    FUNCTION_EXECUTION_TIME.labels(
        language=function.language,
        function_name=function_name,
        status=status
    ).observe(execution_time)

    # Return the original result unchanged
    return result