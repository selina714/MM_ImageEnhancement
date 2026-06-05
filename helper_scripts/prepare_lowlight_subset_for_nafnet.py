from pathlib import Path
import argparse
import shutil
import random


def make_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_or_link(src: Path, dst: Path, use_symlink: bool) -> None:
    if dst.exists():
        return

    if use_symlink:
        dst.symlink_to(src.resolve())
    else:
        shutil.copy2(src, dst)


def get_pair_id(path: Path) -> str:
    name = path.name
    suffix = "-in.webp"
    if not name.endswith(suffix):
        raise ValueError(f"Unexpected input filename: {name}")
    return name[:-len(suffix)]


def prepare_paired_subset(
    src_dir: Path,
    dst_dir: Path,
    max_pairs: int,
    offset: int,
    seed: int,
    shuffle: bool,
    use_symlink: bool,
) -> None:
    lq_dir = dst_dir / "lq"
    gt_dir = dst_dir / "gt"
    make_dir(lq_dir)
    make_dir(gt_dir)

    input_files = sorted(src_dir.glob("*-in.webp"))

    if shuffle:
        random.seed(seed)
        random.shuffle(input_files)

    selected = input_files[offset: offset + max_pairs]

    if not selected:
        raise RuntimeError(
            f"No files selected. Check offset={offset}, max_pairs={max_pairs}, total={len(input_files)}"
        )

    count = 0

    for in_file in selected:
        pair_id = get_pair_id(in_file)
        gt_file = src_dir / f"{pair_id}-gt.webp"

        if not gt_file.exists():
            raise FileNotFoundError(f"Missing GT file for {in_file.name}")

        copy_or_link(in_file, lq_dir / f"{pair_id}.webp", use_symlink)
        copy_or_link(gt_file, gt_dir / f"{pair_id}.webp", use_symlink)
        count += 1

    print(f"Prepared paired subset from {src_dir}")
    print(f"Total available input files: {len(input_files)}")
    print(f"Offset: {offset}")
    print(f"Max pairs: {max_pairs}")
    print(f"Prepared pairs: {count}")


def prepare_test_subset(src_dir: Path, dst_dir: Path, max_files: int, use_symlink: bool) -> None:
    lq_dir = dst_dir / "lq"
    make_dir(lq_dir)

    input_files = sorted(src_dir.glob("*-in.webp"))

    if max_files > 0:
        input_files = input_files[:max_files]

    count = 0

    for in_file in input_files:
        pair_id = get_pair_id(in_file)
        copy_or_link(in_file, lq_dir / f"{pair_id}.webp", use_symlink)
        count += 1

    print(f"Prepared test files: {count}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True, help="Original low-light dataset root")
    parser.add_argument("--dst", required=True, help="Output NAFNet-style subset root")

    parser.add_argument("--train-pairs", type=int, default=5000)
    parser.add_argument("--val-pairs", type=int, default=1000)
    parser.add_argument("--test-files", type=int, default=0)

    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--shuffle", action="store_true")

    parser.add_argument("--symlink", action="store_true")

    args = parser.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)

    prepare_paired_subset(
        src_dir=src / "train",
        dst_dir=dst / "train",
        max_pairs=args.train_pairs,
        offset=args.offset,
        seed=args.seed,
        shuffle=args.shuffle,
        use_symlink=args.symlink,
    )

    prepare_paired_subset(
        src_dir=src / "val",
        dst_dir=dst / "val",
        max_pairs=args.val_pairs,
        offset=0,
        seed=args.seed,
        shuffle=False,
        use_symlink=args.symlink,
    )

    prepare_test_subset(
        src_dir=src / "test",
        dst_dir=dst / "test",
        max_files=args.test_files,
        use_symlink=args.symlink,
    )

    print("\nDone.")
    print(f"Prepared subset saved at: {dst}")


if __name__ == "__main__":
    main()