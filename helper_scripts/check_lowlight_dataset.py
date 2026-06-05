from pathlib import Path
import argparse


def get_id_from_name(path: Path, role: str) -> str:
    suffix = f"-{role}.webp"
    name = path.name
    if not name.endswith(suffix):
        raise ValueError(f"Unexpected filename format: {name}")
    return name[:-len(suffix)]


def check_paired_split(split_dir: Path, split_name: str) -> None:
    input_files = sorted(split_dir.glob("*-in.webp"))
    gt_files = sorted(split_dir.glob("*-gt.webp"))

    input_ids = {get_id_from_name(p, "in") for p in input_files}
    gt_ids = {get_id_from_name(p, "gt") for p in gt_files}

    missing_gt = input_ids - gt_ids
    missing_input = gt_ids - input_ids

    print(f"\n[{split_name}]")
    print(f"Input files: {len(input_files)}")
    print(f"GT files:    {len(gt_files)}")
    print(f"Pairs:       {len(input_ids & gt_ids)}")

    if missing_gt:
        print(f"Missing GT files: {len(missing_gt)}")
        for item in sorted(list(missing_gt))[:10]:
            print(f"  {item}-gt.webp")

    if missing_input:
        print(f"Missing input files: {len(missing_input)}")
        for item in sorted(list(missing_input))[:10]:
            print(f"  {item}-in.webp")

    if not missing_gt and not missing_input:
        print("Status: OK")


def check_test_split(split_dir: Path) -> None:
    input_files = sorted(split_dir.glob("*-in.webp"))
    gt_files = sorted(split_dir.glob("*-gt.webp"))

    print("\n[test]")
    print(f"Input files: {len(input_files)}")
    print(f"GT files:    {len(gt_files)}")

    if gt_files:
        print("Warning: test split should not contain GT files.")
    else:
        print("Status: OK")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        required=True,
        help="Path to low-light dataset root containing train, val, test"
    )
    args = parser.parse_args()

    root = Path(args.root)

    expected = ["train", "val", "test"]
    for name in expected:
        if not (root / name).exists():
            raise FileNotFoundError(f"Missing folder: {root / name}")

    check_paired_split(root / "train", "train")
    check_paired_split(root / "val", "val")
    check_test_split(root / "test")


if __name__ == "__main__":
    main()