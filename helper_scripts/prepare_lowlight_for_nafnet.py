from pathlib import Path
import argparse
import shutil


def make_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_or_link(src: Path, dst: Path, use_symlink: bool) -> None:
    if dst.exists():
        return

    if use_symlink:
        dst.symlink_to(src.resolve())
    else:
        shutil.copy2(src, dst)


def prepare_paired_split(src_dir: Path, dst_dir: Path, use_symlink: bool) -> None:
    lq_dir = dst_dir / "lq"
    gt_dir = dst_dir / "gt"
    make_dir(lq_dir)
    make_dir(gt_dir)

    input_files = sorted(src_dir.glob("*-in.webp"))

    count = 0
    for in_file in input_files:
        stem = in_file.name[:-len("-in.webp")]
        gt_file = src_dir / f"{stem}-gt.webp"

        if not gt_file.exists():
            raise FileNotFoundError(f"Missing GT for {in_file.name}")

        copy_or_link(in_file, lq_dir / f"{stem}.webp", use_symlink)
        copy_or_link(gt_file, gt_dir / f"{stem}.webp", use_symlink)
        count += 1

    print(f"Prepared paired split: {src_dir.name}, pairs={count}")


def prepare_test_split(src_dir: Path, dst_dir: Path, use_symlink: bool) -> None:
    lq_dir = dst_dir / "lq"
    make_dir(lq_dir)

    input_files = sorted(src_dir.glob("*-in.webp"))

    count = 0
    for in_file in input_files:
        stem = in_file.name[:-len("-in.webp")]
        copy_or_link(in_file, lq_dir / f"{stem}.webp", use_symlink)
        count += 1

    print(f"Prepared test split: {src_dir.name}, inputs={count}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True, help="Original low-light dataset root")
    parser.add_argument("--dst", required=True, help="Output NAFNet-style dataset root")
    parser.add_argument(
        "--symlink",
        action="store_true",
        help="Use symlinks instead of copying files"
    )
    args = parser.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)

    prepare_paired_split(src / "train", dst / "train", args.symlink)
    prepare_paired_split(src / "val", dst / "val", args.symlink)
    prepare_test_split(src / "test", dst / "test", args.symlink)

    print("\nDone.")
    print(f"Prepared dataset saved at: {dst}")


if __name__ == "__main__":
    main()