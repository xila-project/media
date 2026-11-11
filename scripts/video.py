"""Reusable FFmpeg sequence assembly, overlays, soundtrack muxing and validation."""
import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess
import tempfile


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


def concat(sources, output):
    sources = [Path(s) for s in sources]
    output = Path(output)
    if len(sources) < 2:
        raise ValueError("At least two input clips are required to concatenate")

    resolved_output = output.resolve()
    for s in sources:
        if resolved_output == s.resolve():
            raise ValueError(f"Output must not overwrite source media: {output}")
        if output.exists() and s.exists() and output.samefile(s):
            raise ValueError(f"Output path aliases an input source: {output}")

    reference = None
    for src in sources:
        if not src.is_file():
            raise FileNotFoundError(f"Input clip not found: {src}")
        data = probe(src)
        video_streams = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
        if not video_streams:
            raise ValueError(f"No video stream found in {src}")
        stream = video_streams[0]
        if stream.get("codec_name") != "h264":
            raise ValueError(f"Unsupported codec {stream.get('codec_name')} in {src}; expected h264")

        rate_str = stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/1"
        try:
            num, den = map(int, rate_str.split("/"))
            fps = num / den if den else 0.0
        except (ValueError, ZeroDivisionError):
            fps = 0.0

        if fps <= 0 or not math.isfinite(fps):
            raise ValueError(f"Invalid frame rate in {src}")

        dims = (stream.get("width"), stream.get("height"))
        pix_fmt = stream.get("pix_fmt")
        time_base = Fraction(stream["time_base"])
        if time_base <= 0:
            raise ValueError(f"Invalid time base in {src}")

        if reference is None:
            reference = (dims, pix_fmt, fps, time_base)
        else:
            ref_dims, ref_pix_fmt, ref_fps, ref_time_base = reference
            if dims != ref_dims:
                raise ValueError(f"Incompatible dimensions {dims} in {src}; expected {ref_dims}")
            if pix_fmt != ref_pix_fmt:
                raise ValueError(f"Incompatible pixel format {pix_fmt} in {src}; expected {ref_pix_fmt}")
            if time_base != ref_time_base:
                raise ValueError(f"Incompatible time base {time_base} in {src}; expected {ref_time_base}")
            if abs(fps - ref_fps) >= 0.01:
                raise ValueError(f"Incompatible frame rate {fps} in {src}; expected {ref_fps}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as list_file:
        list_path = Path(list_file.name)
        for s in sources:
            escaped = str(s.resolve()).replace("'", "'\\''")
            list_file.write(f"file '{escaped}'\n")

    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=output.suffix, delete=False) as staged:
        staged_path = Path(staged.name)
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "warning",
                "-nostdin",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_path),
                "-map",
                "0:v:0",
                "-c:v",
                "copy",
                "-an",
                "-movflags",
                "+faststart",
                str(staged_path),
            ],
            check=True,
        )
        staged_path.replace(output)
    finally:
        staged_path.unlink(missing_ok=True)
        list_path.unlink(missing_ok=True)


def soundtrack(source, audio, output, offset=0):
    duration=float(probe(source)['format']['duration'])
    if not math.isfinite(offset) or not 0 <= offset < duration:
        raise ValueError('Soundtrack offset must fall within the video')
    if output.resolve() in [source.resolve(),audio.resolve()]:
        raise ValueError('Output must not overwrite source media')
    output.parent.mkdir(parents=True,exist_ok=True)
    delay=round(offset*1000)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-y',
                    '-i',str(source),'-i',str(audio),'-filter_complex',
                    f'[1:a]aresample=48000,adelay={delay}:all=1,apad[a]',
                    '-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac',
                    '-b:a','192k','-ar','48000','-t',str(duration),
                    '-movflags','+faststart',str(output)],check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    assemble = sub.add_parser("assemble")
    assemble.add_argument("frames", type=Path)
    assemble.add_argument("output", type=Path)
    assemble.add_argument("--fps", type=int, choices=[24, 30, 60], default=30)
    assemble.add_argument("--preset", choices=["fast", "medium", "slow"], default="medium")
    assemble.add_argument("--audio", type=Path)
    concat_cmd = sub.add_parser("concat")
    concat_cmd.add_argument("clips", nargs="+", type=Path)
    concat_cmd.add_argument("-o", "--output", dest="output", type=Path)
    overlay = sub.add_parser("overlay")
    overlay.add_argument("base", type=Path)
    overlay.add_argument("layer", type=Path)
    overlay.add_argument("output", type=Path)
    sound = sub.add_parser("soundtrack")
    sound.add_argument("source",type=Path)
    sound.add_argument("audio",type=Path)
    sound.add_argument("output",type=Path)
    sound.add_argument("--offset",type=float,default=0)
    check = sub.add_parser("validate")
    check.add_argument("input", type=Path)
    for key in ["width", "height", "fps", "duration"]:
        check.add_argument(f"--{key}", type=int, required=True)
    args = parser.parse_args()
    if args.command == "validate":
        validate(args.input, args.width, args.height, args.fps, args.duration)
        return
    if args.command == "soundtrack":
        soundtrack(args.source,args.audio,args.output,args.offset)
        return
    if args.command == "concat":
        if args.output is None:
            if len(args.clips) < 2:
                parser.error("concat requires at least two clips, or inputs and an output path")
            sources = args.clips[:-1]
            output = args.clips[-1]
        else:
            sources = args.clips
            output = args.output
        concat(sources, output)
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
