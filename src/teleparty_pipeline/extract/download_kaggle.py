import kagglehub
import shutil
import os

def download_data(dest_dir: str):
    required_files = ["title.basics.tsv", "title.ratings.tsv"]
    
    os.makedirs(dest_dir, exist_ok=True)

    # Ensure title.episode.tsv exists for downstream Spark compatibility
    episode_file = os.path.join(dest_dir, "title.episode.tsv")
    if not os.path.exists(episode_file):
        print("Creating title.episode.tsv stub for downstream Spark compatibility...", flush=True)
        with open(episode_file, "w") as f:
            f.write("tconst\tparentTconst\tseasonNumber\tepisodeNumber\n")

    existing_files = os.listdir(dest_dir)
    
    if all(f in existing_files and os.path.getsize(os.path.join(dest_dir, f)) > 0 for f in required_files):
        print(f"Dataset files already exist in {dest_dir}. Skipping download.", flush=True)
        return

    print("Downloading dataset via kagglehub...", flush=True)
    dataset_handle = "ashirwadsangwan/imdb-dataset"
    cache_dir = os.path.expanduser(f"~/.cache/kagglehub/datasets/{dataset_handle}")
    
    path = None
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            path = kagglehub.dataset_download(dataset_handle)
            break
        except Exception as e:
            print(f"kagglehub download attempt {attempt}/{max_retries} failed: {e}", flush=True)
            if os.path.exists(cache_dir):
                print(f"Cleaning up corrupted kagglehub cache directory: {cache_dir}...", flush=True)
                shutil.rmtree(cache_dir, ignore_errors=True)
            if attempt == max_retries:
                raise
    print(f"Dataset downloaded to cache: {path}", flush=True)
    
    print(f"Copying files to {dest_dir}...", flush=True)
    if os.path.isfile(path):
        shutil.copy2(path, dest_dir)
        print(f"Copied file {os.path.basename(path)} to {dest_dir}", flush=True)
    elif os.path.isdir(path):
        for item in os.listdir(path):
            s = os.path.join(path, item)
            d = os.path.join(dest_dir, item)
            if os.path.isfile(s):
                size_mb = os.path.getsize(s) / (1024 * 1024)
                print(f"Copying {item} ({size_mb:.1f} MB)...", flush=True)
                shutil.copy2(s, d)
                print(f"Copied {item}", flush=True)
            elif os.path.isdir(s):
                print(f"Copying directory {item}...", flush=True)
                shutil.copytree(s, d, dirs_exist_ok=True)
                print(f"Copied directory {item}", flush=True)

            
    # Check if all required files exist in dest_dir
    copied_files = os.listdir(dest_dir)
    missing = [f for f in required_files if f not in copied_files or os.path.getsize(os.path.join(dest_dir, f)) == 0]
    if missing:
        raise FileNotFoundError(
            f"Download/copy completed, but required files are missing in {dest_dir}: {missing}. Pipeline cannot proceed."
        )

    print(f"Download and copy complete. Files are ready in {dest_dir}", flush=True)


if __name__ == "__main__":
    dest = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/source"))
    download_data(dest)


