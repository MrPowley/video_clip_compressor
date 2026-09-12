import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path

import tomllib

import core


def get_version():
    version_file = Path(__file__).resolve().parent / "VERSION"
    return version_file.read_text().strip()


__version__ = get_version()


def show_preview(work: core.Work):
    ffmpeg_command1, ffmpeg_command2 = work.make_ffmpeg_commands()

    print(f"{' Preview ':=^50}")
    print("File paths")
    print(f"    Input path           : {work.input}")
    print(f"    Output path          : {work.output}")
    print("Video settings")
    print(f"    Resolution           : {work.resolution}")
    print(f"    Duration             : {work.duration} s")
    print(f"    Framerate            : {work.framerate} fps")
    print(f"    Target size          : {work.target_size} MB")
    print(f"    Enable compatibility : {work.compatibility}")

    print("FFMPEG Commands")
    print("    First pass           :", " ".join(ffmpeg_command1))
    print("    Second pass          :", " ".join(ffmpeg_command2))

    print(f"{'':=^50}")


def main():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--input", help="input video file path", type=str)
    parser.add_argument("-o", "--output", help="output file path", type=str)
    parser.add_argument("-t", "--target", help="target size (MB)", type=int, default=20)
    parser.add_argument(
        "-f",
        "--framerate",
        help="increase output framerate",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-r", "--resolution", help="set output resolution", type=str, default="1280:720"
    )
    parser.add_argument(
        "-c",
        "--compatibility",
        help="enable compatibility",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-p",
        "--preview",
        help="print work info without running",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-y",
        "--overwrite",
        help="overwrite output file is it exists",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-v",
        "--version",
        help="prints version and exit",
        action="version",
        version=f"VCC {__version__}",
    )

    args: Namespace = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    work = core.Work(
        args.input,
        args.output,
        args.framerate,
        args.resolution,
        args.target,
        compatibility=args.compatibility,
    )

    if work.output.exists():
        if args.overwrite:
            print("Output file already exists : Overwriting on user command")
        else:
            print("Output file already exists : Aborting")
            print("Use '-y' to overwrite output file")
            return

    if args.preview:
        show_preview(work)
    else:
        print("Beginning encoding")
        work.run()

    print("Encoding done")


if __name__ == "__main__":
    main()
