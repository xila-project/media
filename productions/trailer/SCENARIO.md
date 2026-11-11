# Xila — launch film scenario

**Editorial draft 3 · 120 seconds · English · 1920×1080 · 30 FPS**

Draft 2 listed qualities (“An operating system.”, “Built in Rust.”, “For embedded systems.”) without arguing anything. Draft 3 is built on one thesis, taken from Xila's own mission statement and proven with real behaviour found in the code:

> **One system, from a microcontroller to your browser.**
> “Our mission is to create a versatile operating system that can run on a wide range of hardware platforms, from microcontrollers to desktop computers.” — website `about/index.md`

Three arguments carry it, in order of surprise:

1. **It is small.** Xila runs on an Arduino Nano 33 BLE with 256 KiB of RAM.
2. **Everything is a file.** The same file write lights an LED, runs a neural network and plays a sound.
3. **Applications travel.** One signed WebAssembly package runs on the desktop, in a browser tab and in a container; when an application fails, Xila keeps running.

The film then states where Xila is going and closes on an invitation anyone can act on immediately: Xila runs in a browser, right now.

## The visual idea

The light world from the art-direction study gains a meaning: **every light in this film is a file write.** The film opens and closes on a single point of light — an LED — which is also the centre square of the Xila mark. Routes are the paths of the virtual file system; their endpoints are devices. Real software appears only as proof, cropped tight to what proves the point: a command, a canvas, a result. No full desktop screenshots, no colourful launcher grids.

The shell is the film's second typeface. Genuine commands, set large in Montserrat, are the only “interface” the audience must read. Each command is documented and real; its effect follows on screen.

## Scenario

### 00:00–00:08 — Recognition

Keep the reviewed opening: material close-ups of the official mark, pullback, Core bootsplash ripple at 00:05.3. The camera settles on the **centre square**.

### 00:08–00:20 — Small

The camera pushes into the centre square until it is a single point in black. Pull back: the point is an LED on a very small board, dwarfed by the dark floor around it. One line of shell:

`echo 1 > /devices/gpio/d13`

The LED switches on and its light runs out into the floor as the first route. **“256 KiB of memory.”** then **“A complete operating system.”**

_Proof:_ Platforms `examples/nano_33_ble/README.md` — nRF52840, 256 KiB RAM, 448 KiB firmware region, LEDs as `/devices/gpio/*`; CI builds the firmware. _Capture:_ a real Nano 33 BLE filmed on black, its serial console beside it. Until then, the board is abstract geometry and the command is the documented one.

### 00:20–00:44 — Everything is a file

The route reaches a junction and splits towards three different endpoints, each named only by its real path, engraved in the floor:

| Path                      | What answers                                                                                  | Proof on screen (cropped)                                       |
| ------------------------- | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `/devices/gpio/d13`       | Light: the LED from the previous passage.                                                     | Board footage or the shell line.                                |
| `/devices/nn/…`           | Intelligence: a hand-drawn **3** goes in; the Digits application answers **3**, offline.      | Native capture of the Digits canvas and its top prediction.     |
| `/devices/audio/playback` | Sound: the Synth application plays one held note — the first sound of the score is this note. | Native/browser capture of the key press, real audio in the mix. |

**“Everything is a file.”** lands as the three responses align. Engineers recognise the Unix idea; everyone else sees one gesture produce light, recognition and sound.

_Proof:_ VFS dispatch of devices, pipes and filesystems (Core `subsystems/virtual_file_system`); Digits uses descriptor controls on its neural-network device (Applications `executables/digits`); Synth negotiates `/devices/audio/playback` (`executables/synth/src/device.rs`). Use the device path of the captured revision (local `nn/digits`, upstream `nn/cpu`).

### 00:44–01:04 — Applications travel

The reviewed execution passage: light leaves the inlaid mark along the measured Pixel Painter strokes. A signed package label is engraved in the floor:

`xila.pixel-painter 0.1.0 · sha256 f0c28b1f…`

The strokes arrive at **three surfaces in a row**: the desktop runtime, a browser tab, a container terminal. Each shows the same drawing growing, from a genuine recording. **“One package.”** **“Every Xila.”** Supporting line: **“WebAssembly applications.”**

_Proof:_ Platforms `tools/fs_image/profiles/bundles.lock.json` pins one signed artifact per application; `image:native`, `image:browser` and `Dockerfile.runtime` seed from it. The browser runtime mounts the same Wasmi host. _Capture:_ record the extracted Wasm SHA-256 in each environment; the hash shown must be the one recorded.

### 01:04–01:16 — Isolated

One application's light breaks: in a terminal, a deliberately faulty WebAssembly program traps. The next line still answers:

```
wasm /capture/trap.wasm
… trap: unreachable
echo system-alive
system-alive
```

Around it the rest of the world keeps moving. **“An application can fail.”** **“Xila keeps running.”** Supporting: **“Built in Rust.”**

_Proof:_ Applications `executables/wasm/src/host/execution.rs` (fuel quanta, trap propagation), `tests/runtime.rs` (`unreachable`, host failure, competing-task progress). _Capture:_ Docker runtime with a read-only fixture mount, as documented in `how-to/run-container-guest.md`.

### 01:16–01:28 — Where it is going

The floor extends. New boards and surfaces dock into it along the same routes. A package arrives, is checked and opens. **“More boards.”** **“Signed applications, installed in place.”** Abstract geometry only.

_Roadmap claims_ (approved by the maintainer, 2026-11-11): Espressif ESP32/ESP32-S3 ports, registry-based package installation and upgrades. These are shown as abstract animation, never as staged interface footage.

### 01:28–01:38 — Escalation

Six fast cuts, one from each argument, matched on direction: LED on; the 3 recognised; the note's waveform as light; the three surfaces; the trap and the next prompt; the floor extending. Greatest rhythmic density; peak at 01:38.

### 01:38–01:48 — One light

Everything goes dark route by route, back towards the origin, until a single point remains: the LED. The camera pushes in; the point becomes the mark's centre square. The arms assemble around it.

### 01:48–02:00 — Xila

Official horizontal lockup on black. **“An open-source operating system.”** Then the invitation: **“Runs in your browser. Right now.”** with `platforms.xila.dev`, then `www.xila.dev`. Fade on the final resonance.

## Copy sheet

| Time  | Primary                                                                      | Supporting                        |
| ----- | ---------------------------------------------------------------------------- | --------------------------------- |
| 00:10 | `echo 1 > /devices/gpio/d13` (shell)                                         |                                   |
| 00:13 | 256 KiB of memory.                                                           |                                   |
| 00:16 | A complete operating system.                                                 |                                   |
| 00:22 | `/devices/gpio/d13` · `/devices/nn/…` · `/devices/audio/playback` (engraved) |                                   |
| 00:38 | Everything is a file.                                                        |                                   |
| 00:46 | `xila.pixel-painter 0.1.0 · sha256 f0c28b1f…` (engraved)                     |                                   |
| 00:55 | One package. Every Xila.                                                     | WebAssembly applications.         |
| 01:06 | shell: trap, then `system-alive`                                             |                                   |
| 01:09 | An application can fail. Xila keeps running.                                 | Built in Rust.                    |
| 01:18 | More boards. Signed applications, installed in place.                        |                                   |
| 01:51 | Official lockup                                                              | An open-source operating system.  |
| 01:55 | Runs in your browser. Right now.                                             | platforms.xila.dev · www.xila.dev |

## Claim policy

- **Working today, shown with genuine captures:** native desktop, browser (OPFS) and container runtimes; Nano 33 BLE headless console with GPIO files (CI-built; flashing not CI-validated — film a real board before using its footage); Digits, Synth, Pixel Painter; trap containment; shared release-locked packages.
- **Roadmap, allowed in copy and abstract animation** (maintainer decision 2026-11-11): further boards including ESP32/ESP32-S3, registry install/upgrade, signed in-place installation for ordinary users.
- **Never:** staged or reconstructed interface footage, invented numbers, performance comparisons, or “apps can never crash the OS” as an absolute. Resource figures come only from the Nano 33 BLE memory layout.

## Captures required

| Capture                                    | Where                             | Status                        |
| ------------------------------------------ | --------------------------------- | ----------------------------- |
| Nano 33 BLE: serial command → LED on       | Physical board + camera           | Needs a board                 |
| Digits: draw 3 → prediction                | Native headless                   | To record                     |
| Synth: one note, with audio                | Browser or native audio           | To record + audio             |
| Pixel Painter drawing ×3 hosts + Wasm hash | Native (done), browser, container | Browser + container to record |
| Trap then `system-alive`                   | Docker runtime shell              | To record                     |

Sources were audited on 2026-11-11 at Core `a9b1324a`, Applications `3de40ca`, Platforms `b655fe2`, website `f3517f2`; see the research summaries in [CONTENT-EVIDENCE.md](CONTENT-EVIDENCE.md).
