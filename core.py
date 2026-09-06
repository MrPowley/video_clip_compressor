import platform
import re
import subprocess
import sys
from collections.abc import Callable
from datetime import datetime
from math import ceil, floor
from pathlib import Path

from pymediainfo import MediaInfo
from tqdm import tqdm

import threading

IS_WINDOWS = platform.system() == "Windows"
NULL_DEVICE = "NUL" if IS_WINDOWS else "/dev/null"

DEFAULT_TARGET_SIZE: int = 20
AAC_BITRATE: int = 64
OPUS_BITRATE: int = 32
RESOLUTIONS = ((1920, 1080), (1600, 900), (1280, 720), (960, 540), (640, 360))


class Work:
    def __init__(
        self,
        input_path: str,
        output_path: str,
        higher_framerate: bool = False,
        resolution: str = "",
        target_size: int = DEFAULT_TARGET_SIZE,
        compatibility: bool = False,
        callback: Callable = lambda x: None,
    ) -> None:
        self.input: Path = Path(input_path)
        self.output: Path = Path(output_path)
        self.higher_framerate: bool = higher_framerate
        self.resolution: str = resolution
        self.target_size: float = target_size
        self.compatibility = compatibility
        self.callback = callback

        if not self.is_valid():
            print("Invalid parameters")
            return

        self.duration: float = self.get_duration()
        self.framerate: float = self.get_framerate()
        self.bitrate: int = self.calculate_bitrate()
        print(self.bitrate)

        self.ffmpeg_commands = self.make_ffmpeg_commands()
        print(" ".join(self.ffmpeg_commands[0]))
        print(" ".join(self.ffmpeg_commands[1]))

    def is_valid(self) -> bool:
        if not self.input.exists() or not self.input.is_file():
            print("Input doesn't exist or is not a file")
            return False

        if not self.output.parent.exists():
            print("Output directory does not exist")
            return False

        if self.target_size <= 0:
            print("Target size cannot be zero or negative")
            return False

        return True

    def get_duration(self) -> float:
        metadata = MediaInfo.parse(self.input)
        duration: float = metadata.tracks[0].duration // 1000

        return duration

    def get_framerate(self) -> float:
        metadata = MediaInfo.parse(self.input)
        framerate: float = float(metadata.tracks[0].frame_rate)
        assert isinstance(framerate, float)

        return framerate

    def calculate_bitrate(self) -> int:
        audio_bitrate = AAC_BITRATE if self.compatibility else OPUS_BITRATE
        bitrate: int = (
            floor(0.99 * self.target_size * 1024 * 8 / self.duration) - audio_bitrate
        )

        return bitrate

    def make_ffmpeg_commands(self) -> tuple[list[str], list[str]]:
        ffmpeg_command_pass1: list[str] = ["ffmpeg"]

        ffmpeg_command_pass1 += ["-y", "-i", str(self.input), "-c:v"]

        if self.compatibility:
            ffmpeg_command_pass1 += ["libx264", "-preset", "faster"]
        else:
            ffmpeg_command_pass1 += ["libsvtav1", "-preset", "6"]

        ffmpeg_command_pass1 += [
            "-b:v",
            str(self.bitrate) + "k",
            "-passlogfile",
            ".",
        ]

        if self.higher_framerate:
            ffmpeg_command_pass1 += ["-r", str(min(60, self.framerate))]
        else:
            ffmpeg_command_pass1 += ["-r", str(min(30, self.framerate))]

        if self.resolution:
            ffmpeg_command_pass1 += ["-vf", f"scale={self.resolution}"]

        ffmpeg_command_pass2 = ffmpeg_command_pass1 + ["-pass", "2"]

        if self.compatibility:
            ffmpeg_command_pass2 += ["-c:a", "aac", "-b:a", f"{AAC_BITRATE}k"]
        else:
            ffmpeg_command_pass2 += ["-c:a", "libopus", "-b:a", f"{OPUS_BITRATE}k"]

        ffmpeg_command_pass2 += [str(self.output)]

        ffmpeg_command_pass1 += ["-pass", "1", "-an"]
        ffmpeg_command_pass1 += ["-f", "null", NULL_DEVICE]

        return ffmpeg_command_pass1, ffmpeg_command_pass2

    def auto_parameters(
        self,
        duration: int,
        native_resolution: int,
        native_framerate: int,
        resolution_override: int = -1,
        framerate_override: int = -1,
    ): ...

    def run(self):
        total_seconds = 0
        for command in self.ffmpeg_commands:
            previous_seconds = 0
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                )

                for line in process.stdout:
                    # if line.strip():
                    #     print(line)
                    match = re.search(r"\btime=(\d{2}:\d{2}:\d{2}(?:\.\d+)?)", line)
                    if match is not None:
                        h, m, s = match.group(1).split(":")
                        seconds = int(h) * 3600 + int(m) * 60 + float(s)

                        self.callback(ceil(100 * total_seconds / (self.duration * 2)))

                        total_seconds += seconds - previous_seconds

                        previous_seconds = seconds
            except subprocess.CalledProcessError as e:
                print(f"Error processing: {e.output.decode()}")

        self.callback(100)
