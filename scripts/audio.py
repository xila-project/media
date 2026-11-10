"""Offline startup mastering. The synthetic fixture is a technical test, not approved branding."""
import argparse
import json
import math
from pathlib import Path
import struct
import subprocess
import wave

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "productions/startup/production.json").read_text())


def ffmpeg(arguments):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", *map(str, arguments)], check=True, capture_output=True, text=True)


def measure(path):
    result = ffmpeg(["-i", path, "-af", "loudnorm=I=-20:TP=-2:LRA=7:print_format=json", "-f", "null", "-"])
    start = result.stderr.rfind('{')
    return json.loads(result.stderr[start:result.stderr.rfind('}')+1])


def fixture(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    rate = 48000
    samples = []
    for n in range(rate * 3):
        t = n / rate
        envelope = min(t / .15, 1) * max(0, 1-t/3)**2
        value = envelope * (.18*math.sin(2*math.pi*110*t) + .06*math.sin(2*math.pi*165*t) + .03*math.sin(2*math.pi*220*t))
        samples.append(struct.pack('<h', round(value*32767)))
    with wave.open(str(path), 'w') as audio:
        audio.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        audio.writeframes(b''.join(samples))
    print(f"Synthetic technical fixture: {path}")


def process(source, output, rate):
    source = source.resolve()
    if source == (output / 'master.wav').resolve() or source == (output / 'embedded.wav').resolve():
        raise ValueError('Source must not be an output file')
    info = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(source)]))
    duration = float(info['format']['duration'])
    if not 0.4 <= duration <= CONFIG['maxDuration']:
        raise ValueError('Startup source must be 0.4–5 seconds')
    output.mkdir(parents=True, exist_ok=True)
    # Downmix before measuring so the two passes measure the same signal.
    intermediate = output / 'mix.wav'
    ffmpeg(['-i',source,'-vn','-ac',1,'-ar',48000,'-c:a','pcm_s24le',intermediate])
    measured = measure(intermediate)
    if not math.isfinite(float(measured['input_i'])):
        raise ValueError('Silent or unmeasurable input')
    normalization = ('loudnorm=I=-20:TP=-2:LRA=7:linear=true:'
                     f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
                     f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
                     f"offset={measured['target_offset']}")
    master = output / 'master.wav'
    ffmpeg(['-i',intermediate,'-af',normalization,'-ar',48000,'-ac',1,'-c:a','pcm_s24le',master])
    embedded = output / 'embedded.wav'
    ffmpeg(['-i',master,'-af',f'aresample={rate}:dither_method=triangular','-ar',rate,'-ac',1,'-c:a','pcm_s16le',embedded])
    with wave.open(str(embedded)) as audio:
        assert audio.getparams()[:3] == (1,2,rate)
        samples = struct.unpack('<'+'h'*audio.getnframes(), audio.readframes(audio.getnframes()))
        peak = max(map(abs, samples)) / 32768
    peak_db = 20*math.log10(peak) if peak else -math.inf
    final = measure(embedded)
    assert peak_db <= -1.5, peak_db
    assert abs(float(final['input_i']) - CONFIG['loudnessLUFS']) <= 1.5, final
    assert float(final['input_tp']) <= -1.5, final
    report = {'sampleRate':rate,'channels':1,'codec':'pcm_s16le','peakDBFS':peak_db,'loudness':final,'source':str(source),'bytes':embedded.stat().st_size}
    (output / 'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    intermediate.unlink()
    print(f'Validated PCM16 mono at {rate} Hz; {embedded.stat().st_size} bytes')


def audition(source, output):
    if source.resolve()==output.resolve():
        raise ValueError('Audition must not overwrite source audio')
    profile=CONFIG['dacAudition']
    output.parent.mkdir(parents=True,exist_ok=True)
    filters=(f"highpass=f={profile['highpassHz']},lowpass=f={profile['lowpassHz']},"
             f"aresample={profile['sampleRate']}:dither_method=triangular")
    ffmpeg(['-i',source,'-vn','-af',filters,'-ac',1,'-ar',profile['sampleRate'],'-c:a','pcm_u8',output])
    with wave.open(str(output)) as audio:
        if audio.getparams()[:3]!=(1,1,profile['sampleRate']):
            raise ValueError('Unexpected DAC audition format')
        frames=audio.getnframes()
    report={**profile,'channels':1,'codec':'pcm_u8','durationSeconds':frames/profile['sampleRate'],
            'purpose':'Generic quantization and bandwidth stress test; not a board or speaker emulation',
            'source':str(source)}
    output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"Validated simulated 8-bit mono audition at {profile['sampleRate']} Hz; hardware not validated")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    test = sub.add_parser('fixture'); test.add_argument('output',type=Path)
    export = sub.add_parser('process'); export.add_argument('source',type=Path)
    export.add_argument('--output',type=Path,default=Path('output/startup'))
    export.add_argument('--rate',type=int,choices=[22050,44100,48000],default=22050)
    stress = sub.add_parser('audition'); stress.add_argument('source',type=Path)
    stress.add_argument('--output',type=Path,default=Path('output/startup/dac-8bit.wav'))
    args = parser.parse_args()
    if args.command == 'fixture': fixture(args.output)
    elif args.command == 'audition': audition(args.source,args.output)
    else: process(args.source,args.output,args.rate)
