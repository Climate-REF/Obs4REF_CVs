from pathlib import Path
import os


def rename_obs4mips_directories(root_path="."):
    """Rename all directories matching obs4MIPs_* to obs4REF_* in the root directory."""
    root = Path(root_path)

    if not root.exists():
        print(f"Error: Path {root_path} does not exist")
        return

    # Find all directories that start with obs4MIPs_
    obs4mips_dirs = [
        d for d in root.iterdir() if d.is_dir() and d.name.startswith("obs4MIPs_")
    ]

    if not obs4mips_dirs:
        print("No directories found with obs4MIPs_ prefix")
        return

    print(f"Found {len(obs4mips_dirs)} directories to rename:")

    for old_dir in obs4mips_dirs:
        # Create new name by replacing obs4MIPs_ with obs4REF_
        new_name = old_dir.name.replace("obs4MIPs_", "obs4REF_", 1)
        new_dir = old_dir.parent / new_name

        if new_dir.exists():
            print(
                f"Warning: Target directory {new_name} already exists, skipping {old_dir.name}"
            )
            continue

        try:
            old_dir.rename(new_dir)
            print(f"✓ Renamed: {old_dir.name} → {new_name}")
        except OSError as e:
            print(f"✗ Failed to rename {old_dir.name}: {e}")


if __name__ == "__main__":
    rename_obs4mips_directories()
