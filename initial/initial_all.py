import subprocess
import sys
from pathlib import Path
from env_set import check_all_api_keys
from render_sql_set import check_database_exist
from house_data_set import create_house_sample

def install_requirements():
    """Install required packages from requirements.txt if not already installed."""
    requirements_path = Path(__file__).resolve().parent.parent / "requirements.txt"
    if requirements_path.exists():
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)])
            print("All requirements installed successfully.")
        except subprocess.CalledProcessError as e:
            raise Exception("Failed to install required packages.") from e
    else:
        print("requirements.txt not found.")

def initial_all_set():
    # Install dependencies
    install_requirements()
    
    # Initialization
    try:
        check_all_api_keys()
        create_house_sample()
        check_database_exist()
        print("Initialization completed successfully.")
    except Exception as e:
        raise Exception("Initialization failed") from e

if __name__ == "__main__":
    initial_all_set()
