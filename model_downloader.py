import os
from pathlib import Path
from huggingface_hub import hf_hub_download

# Define model repository and filename
# Using Gemma 2 2B IT quantized for a balance of speed and quality on Apple Silicon
REPO_ID = "bartowski/gemma-2-2b-it-GGUF"
FILENAME = "gemma-2-2b-it-Q4_K_M.gguf"
MODELS_DIR = Path.home() / ".pdf-edit-app" / "models"

def get_model_path():
    """
    Returns the absolute path to the local model file, downloading it if missing.
    Ensures the directory ~/.pdf-edit-app/models/ exists.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    target_path = MODELS_DIR / FILENAME
    
    if target_path.exists():
        print(f"Model found: {target_path}")
        return str(target_path)
    
    print(f"Model missing. Downloading {FILENAME} from {REPO_ID}...")
    try:
        # We use local_dir to place the model exactly where we want it (~/.pdf-edit-app/models/)
        # rather than letting HF manage it in a hidden cache directory.
        downloaded_path = hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            local_dir=MODELS_DIR
        )
        print(f"Download successful: {downloaded_path}")
        return str(downloaded_path)
    except Exception as e:
        print(f"Error downloading model from HuggingFace: {e}")
        return None

if __name__ == "__main__":
    # Test execution
    path = get_model_path()
    if path:
        print(f"SUCCESS: Model ready at {path}")
    else:
        print("FAILURE: Model could not be downloaded.")
        exit(1)
