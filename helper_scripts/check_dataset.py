from pathlib import Path
import argparse


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def list_images(folder):
    folder = Path(folder)
    return sorted([
        p for p in folder.rglob("*")
        if p.suffix.lower() in IMAGE_EXTENSIONS
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input/LQ folder")
    parser.add_argument("--target", required=True, help="Path to target/GT folder")
    args = parser.parse_args()

    input_files = list_images(args.input)
    target_files = list_images(args.target)

    print(f"Input folder:  {args.input}")
    print(f"Target folder: {args.target}")
    print(f"Input images:  {len(input_files)}")
    print(f"Target images: {len(target_files)}")

    input_names = {p.name for p in input_files}
    target_names = {p.name for p in target_files}

    missing_targets = input_names - target_names
    missing_inputs = target_names - input_names

    if missing_targets:
        print(f"\nMissing target files: {len(missing_targets)}")
        for name in sorted(list(missing_targets))[:20]:
            print("  ", name)

    if missing_inputs:
        print(f"\nMissing input files: {len(missing_inputs)}")
        for name in sorted(list(missing_inputs))[:20]:
            print("  ", name)

    if not missing_targets and not missing_inputs:
        print("\nDataset check passed: input and target filenames match.")
    else:
        print("\nDataset check failed. Please check folder structure or filenames.")


if __name__ == "__main__":
    main()