import kagglehub
import shutil
import os

def download_data(dest_dir: str):
    required_files = ["title.basics.tsv", "title.ratings.tsv", "title.episode.tsv"]
    
    os.makedirs(dest_dir, exist_ok=True)
    existing_files = os.listdir(dest_dir)
    
    if all(f in existing_files and os.path.getsize(os.path.join(dest_dir, f)) > 0 for f in required_files):
        print(f"Dataset files already exist in {dest_dir}. Skipping download.")
        return

    print("Downloading dataset via kagglehub...")
    # Download latest version
    path = kagglehub.dataset_download("ashirwadsangwan/imdb-dataset")
    print(f"Dataset downloaded to cache: {path}")
    
    print(f"Copying files to {dest_dir}...")
    if os.path.isfile(path):
        shutil.copy2(path, dest_dir)
        print(f"Copied file {os.path.basename(path)} to {dest_dir}")
    elif os.path.isdir(path):
        for item in os.listdir(path):
            s = os.path.join(path, item)
            d = os.path.join(dest_dir, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
                print(f"Copied {item}")
            elif os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
                print(f"Copied directory {item}")
            
    print(f"Download and copy complete. Files are ready in {dest_dir}")

if __name__ == "__main__":
    dest = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/source"))
    download_data(dest)

