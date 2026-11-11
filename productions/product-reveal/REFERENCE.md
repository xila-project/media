# REFERENCE: Introducing Linear Releases (Linear)

Launchscene: https://launchscene.app/v/linear-releases?t=11
Source: https://www.youtube.com/watch?v=6dIwFoQ0eVg&t=11
Window: video 11.00s to 11.75s (0.75s, 23 frames at 30 fps). Aspect 16:9.
Frame numbers: "frame" is the target composition at 30 fps counted from the window start; "src" is the original video at 60 fps. Last frames are inclusive.

Provenance: timing mixed/quick_pass, text ocr/none, camera optical_flow/none, audio audio/none, annotation mixed/quick_pass.

## Timeline (measured)

```plaintext
  0.00s  frame0     src660    Scene 4 starts (feature_reveal, in: cut)
  0.25s  frame8     src675    Text out: "PLAN AND TRACK RELEASES"
  0.25s  frame8     src675    Camera pull_out starts (ease-out)
```

## Scenes

| # | Role | Frames | Duration | In / out | On-screen text (annotated) |
| --- | --- | --- | --- | --- | --- |
| 4 | feature_reveal | 0 to 22 | 0.75s / 23f | cut / cut | PLAN AND TRACK RELEASES |

## Text: entrance, landing and readable hold

| Text | In | Settled | Out | Entrance | Readable hold (derived) | Box x,y,w,h | Line % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PLAN AND TRACK RELEASES | -52 | -52 | 8 (clipped) | static | 0.25s / 8f, 16 words/s | 0.239, 0.46, 0.522, 0.077 | 7.7 |

## Camera (optical flow)

| Move | Frames | Peak | Amount | Easing |
| --- | --- | --- | --- | --- |
| pull_out | 8 to 92 | 14 | 0.672 x scale | ease-out |

## Audio cues (measured)

BPM: 112.3; first beat in window at frame 9.

```plaintext
DOWNBEAT     frame 9     bar start
```

## Check these frames before relying on them

- No estimated entrance or soft transition in this window.

## Not measured

- font family: not identified
- text color: not measured
- exact bezier: not measured; easing is a class
- element trajectories: not measured; boxes are mid-presence observations
- overshoot: not measured; inspect the landing frames
- cursor and clicks: not detected
- transition duration: not measured

## Proposed creative choices (to fill in, not measured)

- Layout and focal point for your own product:
- What moves first, and where the eye lands:
- Entrance curve and overshoot to try:
- Reading hold for your longest copy (check with readability_check):
- Missing assets and questions for approval:

Adapt timing and structure to your product. Do not copy the reference brand, footage, fonts or music.
