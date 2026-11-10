"""Reusable FFmpeg sequence assembly, overlays, soundtrack muxing and validation."""
import argparse
import json
from pathlib import Path
import subprocess


def probe(path):
    return json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))


def validate(path, width, height, fps, duration):
    data = probe(path)
    stream = next(s for s in data["streams"] if s["codec_type"] == "video")
    numerator, denominator = map(int, stream["avg_frame_rate"].split("/"))
    assert stream["codec_name"] == "h264", stream
    assert (stream["width"], stream["height"]) == (width, height), stream
    assert stream["pix_fmt"] == "yuv420p", stream
    assert abs(numerator / denominator - fps) < 0.01, stream
    assert abs(float(data["format"]["duration"]) - duration) < 1 / fps + 0.01, data
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], check=True)
    print(f"Verified {path}: H.264 {width}x{height} {fps} FPS, {duration}s")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    assemble = sub.add_parser("assemble")
    assemble.add_argument("frames", type=Path)
    assemble.add_argument("output", type=Path)
    assemble.add_argument("--fps", type=int, choices=[24, 30, 60], default=30)
    assemble.add_argument("--preset", choices=["fast", "medium", "slow"], default="medium")
    assemble.add_argument("--audio", type=Path)
    overlay = sub.add_parser("overlay")
    overlay.add_argument("base", type=Path)
    overlay.add_argument("layer", type=Path)
    overlay.add_argument("output", type=Path)
    check = sub.add_parser("validate")
    check.add_argument("input", type=Path)
    for key in ["width", "height", "fps", "duration"]:
        check.add_argument(f"--{key}", type=int, required=True)
    args = parser.parse_args()
    if args.command == "validate":
        validate(args.input, args.width, args.height, args.fps, args.duration)
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-y"]
    if args.command == "assemble":
        command += ["-framerate", str(args.fps), "-i", str(args.frames / "%06d.png")]
        if args.audio:
            command += ["-i", str(args.audio), "-map", "0:v:0", "-map", "1:a:0", "-af", "aresample=48000,apad", "-c:a", "aac", "-shortest"]
        command += ["-preset", args.preset]
    else:
        command += ["-i", str(args.base), "-i", str(args.layer), "-filter_complex", "[0:v][1:v]overlay=shortest=1:format=auto[v]", "-map", "[v]", "-map", "0:a?", "-c:a", "copy"]
    command += ["-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(args.output)]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
