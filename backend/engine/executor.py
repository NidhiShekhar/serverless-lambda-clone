# backend/engine/executor.py
import tempfile
import os
import time
import docker
import logging
from pathlib import Path
from backend.metrics import FUNCTION_EXECUTIONS, FUNCTION_EXECUTION_TIME

logger = logging.getLogger(__name__)


class DockerExecutor:
    def __init__(self):
        self.client = docker.from_env()
        self._ensure_base_images()

    def _ensure_base_images(self, retries=3):
        """Build base images with retry logic"""
        docker_dir = Path(__file__).parent.parent.parent / "docker"
        images = {
            "serverless-python": docker_dir / "python",
            "serverless-javascript": docker_dir / "javascript"
        }

        for image_name, image_path in images.items():
            if image_name == "serverless-python":
                req_file = image_path / "requirements.txt"
                if not req_file.exists():
                    logger.warning(f"Creating empty {req_file}")
                    with open(req_file, 'w') as f:
                        f.write("# Auto-generated requirements file\n")

            for attempt in range(retries):
                try:
                    logger.info(f"Building {image_name} image, attempt {attempt + 1}/{retries}...")
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
                        logger.info("Retrying in 2 seconds...")
                        time.sleep(2)
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
        with tempfile.TemporaryDirectory() as temp_dir:
            function_path = os.path.join(temp_dir, "function.py")
            with open(function_path, "w") as f:
                f.write(function.code)
            logger.info(f"Created function.py at {function_path}")

            reqs_path = os.path.join(temp_dir, "requirements.txt")
            with open(reqs_path, "w") as f:
                f.write("# Function dependencies\n")

            logger.info(f"Temporary directory contents: {os.listdir(temp_dir)}")
            return self._run_container(
                image="serverless-python:latest",
                mount_path=temp_dir,
                timeout=function.timeout
            )

    def _run_javascript_function(self, function):
        with tempfile.TemporaryDirectory() as temp_dir:
            function_path = os.path.join(temp_dir, "function.js")
            with open(function_path, "w") as f:
                f.write(function.code)

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
            container = self.client.containers.run(
                image=image,
                volumes={mount_path: {'bind': '/app', 'mode': 'ro'}},
                detach=True,
                network_disabled=True,
                mem_limit='128m',
                cpu_quota=100000,
                read_only=True
            )

            # Wait for the container to finish execution
            result = container.wait(timeout=timeout)
            logs = container.logs().decode('utf-8')

            if result['StatusCode'] == 0:
                # Successful execution
                return {"status": "success", "result": {"output": logs.strip()}}
            else:
                # Error occurred during execution
                return {"status": "error", "result": {"error": logs.strip()}}

        except Exception as e:
            logger.error(f"Docker execution error: {str(e)}")
            return {"status": "error", "result": {"error": f"Container execution failed: {str(e)}"}}

        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception as cleanup_error:
                    logger.warning(f"Container cleanup failed: {str(cleanup_error)}")

            execution_time = time.time() - start_time
            logger.info(f"Function execution took {execution_time:.2f} seconds")

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
    result = docker_executor.execute_function(function)
    execution_time = time.time() - start_time

    function_name = getattr(function, 'name', 'unnamed')
    status = "error" if "error" in result else "success"

    FUNCTION_EXECUTIONS.labels(
        language=function.language,
        status=status
    ).inc()

    FUNCTION_EXECUTION_TIME.labels(
        language=function.language,
        function_name=function_name,
        status=status
    ).observe(execution_time)

    return result