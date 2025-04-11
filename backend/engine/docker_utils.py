# backend/engine/docker_utils.py
import logging
import sys
import docker

logger = logging.getLogger(__name__)

def check_docker_availability():
    """Verify Docker is installed and accessible"""
    try:
        import docker
        client = docker.from_env()
        # Test Docker connection
        client.version()
        logger.info("Docker is available and running")
        return True
    except ImportError:
        logger.error("Docker SDK not installed. Run: pip install docker")
        return False
    except Exception as e:
        logger.error(f"Docker is not available: {str(e)}")
        return False

# Add to backend/engine/docker_utils.py
def check_docker_permissions():
    """Verify Python has permissions to use Docker"""
    try:
        import docker
        client = docker.from_env()
        # Try a simple container as a permissions test
        container = client.containers.run("hello-world", detach =False, remove=True, network='host')
        return True
    except Exception as e:
        logger.error(f"Insufficient Docker permissions: {str(e)}")
        return False

def test_docker_setup():
    """Run all Docker setup tests."""
    logger.info("Testing Docker setup...")
    if not check_docker_availability():
        logger.error("Docker setup failed: Docker is not installed or accessible.")
        return False
    if not check_docker_permissions():
        logger.error("Docker setup failed: Insufficient permissions.")
        return False
    logger.info("Docker setup is working correctly.")
    return True

# In docker_utils.py
def test_container_run():
    try:
        client = docker.from_env()
        container = client.containers.run(
            "hello-world",
            detach=False,
            remove=True,
            network_mode='host'  # Add this line to fix bridge issues
        )
        return True
    except Exception as e:
        logger.error(f"Insufficient Docker permissions: {str(e)}")
        return False


if __name__ == "__main__":
    # This allows the file to be run directly
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    if test_docker_setup():
        print("Docker setup is valid.")
    else:
        print("Docker setup has issues. Check the logs for details.")