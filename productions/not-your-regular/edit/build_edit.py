"""Assemble an edit of take 005 with TTS dialogue (output/not-your-regular/edit-001)."""
import subprocess, json, sys, os
BAR=60/130*4
out=sys.argv[1] if len(sys.argv)>1 else 'edit-002'
A=dict(big=(0.0,2.93),who=(3.32,4.02),micro=(4.46,5.82),chips=(6.20,8.45),what=(8.83,10.03),wait=(10.45,12.68),os=(13.09,14.97),ad=(15.41,16.32),flash=(16.69,18.39),shh=(18.80,20.64))
X=dict(cute=(0.0,2.37),chip=(2.91,4.49),micro=(4.82,7.15),not_=(7.44,8.49),loop=(8.81,9.85),imag=(10.16,11.89),snug=(12.23,14.88),sure=(15.17,17.04),lib=(17.37,19.03),loop2=(19.38,20.40))
# ALIX=<file> swaps in another rendition of the ALIX lines (e.g. the maintainer's voice clone via the Voice Changer).
# Converted files keep the timing within ~40 ms, so the line ends get a small safety margin.
ALIX=os.environ.get('ALIX','alix.wav')
if ALIX!='alix.wav': A={k:(s,round(e+0.04,3)) for k,(s,e) in A.items()}
src={'A':(0,A),'X':(1,X)}
VOX="highpass=f=75,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,treble=g=2.5:f=8000,aecho=0.85:0.55:32|53:0.16|0.10"
parts=[];labels=[];n=0
def ms(t): return int(round(t*1000))
def place(who,key,t,vol=1.0,extra=''):
    global n
    i,d=src[who]; s,e=d[key]
    parts.append(f"[{i}]atrim={s}:{e},asetpts=PTS-STARTPTS,{VOX},afade=t=in:d=0.015,afade=t=out:st={max(0,e-s-0.05):.3f}:d=0.05{extra},volume={vol*(1.12 if who=='X' else 1.0):.3f},adelay={ms(t)}|{ms(t)}[d{n}]")
    labels.append(f"[d{n}]"); n+=1
    return t+(e-s)
def pad(start,dur,vol=0.04,fin=1.5,fout=0.4,lab='p'):
    tones="+".join(f"0.25*sin(2*PI*{f}*t)*(1+0.12*sin(2*PI*0.25*t))" for f in (130.81,155.56,196.0,233.08))
    parts.append(f"aevalsrc='{tones}':s=48000:d={dur:.3f},lowpass=f=850,volume={vol},afade=t=in:d={fin},afade=t=out:st={dur-fout:.3f}:d={fout},aformat=channel_layouts=stereo,adelay={ms(start)}|{ms(start)}[{lab}]")
    labels.append(f"[{lab}]")
def riser(end,dur,lab):
    parts.append(f"anoisesrc=d={dur:.3f}:c=pink:a=0.5:r=48000,highpass=f=900,volume='0.01+0.22*pow(t/{dur:.3f},2)':eval=frame,afade=t=out:st={dur-0.04:.3f}:d=0.04,aformat=channel_layouts=stereo,adelay={ms(end-dur)}|{ms(end-dur)}[{lab}]")
    labels.append(f"[{lab}]")
def music(a,b,at,lab,fin=0.005,fout=0.05):
    L=b-a
    parts.append(f"[2]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d={fin},afade=t=out:st={L-fout:.3f}:d={fout},adelay={ms(at)}|{ms(at)}[{lab}]")
    labels.append(f"[{lab}]")
# --- intro dialogue, tight gaps
t=0.3
for who,key in [('A','big'),('X','cute'),('A','who'),('X','chip'),('A','micro'),('X','micro'),('A','chips'),('X','not_'),('A','what'),('X','loop')]:
    t=place(who,key,t)+0.16
song0=t-0.16+0.12
pad(3.5,song0-3.5,lab='pi')
riser(song0,2*BAR,'ri')
# --- song up to the stop-time; let the Kazoo Jam tail decay
ST=43*BAR; TAIL=1.6
music(0.0,ST+TAIL,song0,'m0',fout=TAIL)
# --- stop-time: 6 bars instead of 7
GAP=6
st0=song0+ST
pad(st0+0.3,GAP*BAR-0.3,vol=0.03,fin=1.0,fout=0.3,lab='ps')
t=st0+0.35
for who,key in [('A','wait'),('X','imag'),('A','os'),('X','snug')]:
    t=place(who,key,t)+0.2
c2_out=st0+GAP*BAR
riser(c2_out,BAR,'rs')
# --- chorus 1 replaces chorus 2; long crossfade back into the original verse 3
C1a=22*BAR; C1b=30*BAR+0.6; XF=0.25
music(C1a,C1b,c2_out,'m1',fout=XF)
C2=50*BAR
r0=C2+(C1b-C1a)-XF
END=184.0
rest_out=c2_out+(r0-C2)
music(r0,END,rest_out,'m2',fin=XF,fout=0.3)
song_end=rest_out+(182.68-r0)
# --- outro whispers over the decaying tail
t=song_end+0.25
for who,key in [('A','flash'),('X','sure'),('A','shh'),('X','lib'),('X','loop2')]:
    t=place(who,key,t,vol=0.67)+0.28
# --- button: two bars of vocal chop, snapped right after the last whisper, natural tail
bo=t-0.28+0.15
music(4*BAR,6*BAR+0.5,bo,'m3',fout=0.5)
parts.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,loudnorm=I=-14:TP=-1:LRA=11[out]")
subprocess.run(['ffmpeg','-v','error','-y','-i',ALIX,'-i','xila.wav','-i','t5.wav','-filter_complex',';'.join(parts),'-map','[out]','-ar','48000',f'{out}.wav'],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',f'{out}.wav','-b:a','256k',f'{out}.mp3'],check=True)
m={'song_start':song0,'stop_time':st0,'chorus2':c2_out,'song_end':song_end,'button':bo}
json.dump({k:round(v,3) for k,v in m.items()},open(f'{out}-markers.json','w'),indent=1)
print(json.dumps({k:round(v,2) for k,v in m.items()}))
