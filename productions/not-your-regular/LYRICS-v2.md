# Not Your Regular: lyrics v2 (embedded framing)

Draft written on 2026-11-18 after the maintainer's review. The v1 clichés (a forklift, a server room, install discs, a giant box) made Xila sound like a desktop OS. Xila is "an open source OS for the embedded world" (website index). In v2, ALIX plays the old-school firmware developer: an endless loop, poking registers, the datasheet, reflashing, watchdog resets. XILA answers with a real OS on the chip. The structure, the hook, the imagined-app verse and the library twist are unchanged, so the timing and DA tests carry over.

**Proposed hub change:** an electronics bench in a public library's makerspace. It replaces the loading dock, and the outro twist still lands ("Shh! We're in a library!" / "I am a library.").

## Claim check

- **True today:**
  - the 256 KiB RAM Nano 33 BLE with a shell, users, LittleFS files and GPIO device files (`/devices/gpio/d13`);
  - the same signed app bundle on native desktop, in the browser and in a container;
  - app trap containment on hosted runtimes;
  - Rust library, Apache-2.0, browser demo.
- **Roadmap (allowed in copy by the 2026-11-11 maintainer decision; needs the maintainer's OK for these exact lines):**
  - "Can it run apps? / Plural!" right after XILA is identified as the chip. Wasm apps on a microcontroller need the ESP32/ESP32-S3 port; the Nano build has no Wasm runtime, and no ESP32 build is established yet (platforms README).
  - "No watchdog reset? / Nope." on a chip. Trap containment is shown on hosted runtimes; on a microcontroller it depends on the same Wasm runtime port.
- **Boot Log (architecture, true today; replaced the "Band Intro" draft, which the maintainer found too childish):** Core's subsystem managers are Task, VFS, Users, Graphics, Memory, Time, Network and Log (website `explanation/architecture`). Graphics is conditional ("Got a screen?") because the Nano 33 BLE has no display.
  - The Task manager gives each async task (run by Embassy spawners) an identity and metadata.
  - The VFS gives files, devices and pipes one path namespace and applies access policy.
  - Users is the identity and group registry used for permission checks.
  - Graphics hosts LVGL 9.6.
  - Drivers live in Platforms, are linked into each target's final binary and are registered with the VFS, while Core stays portable.
- **Imagined:** the eight gadget apps, disclosed in the song itself ("Imagined. For now.") and in the end card.

## Lyrics

**[Intro]** _(spoken)_  
ALIX: Big day! I made the LED blink!  
XILA: Cute. Hi. I'm here.  
ALIX: Who said that?  
XILA: The chip in your hand.  
ALIX: That's a microcontroller.  
XILA: A microcontroller with an OS.  
ALIX: Chips run a loop. While true.  
XILA: Not this one.  
ALIX: So what are you?  
XILA: Not your regular.

**[Verse 1]**  
ALIX: I wrote a loop that never ends,  
ALIX: with seven flags and global friends!  
XILA: A shell, some users? Yes, ma'am,  
XILA: in two-fifty-six kibibytes of RAM!  
ALIX: I poke a register bit by bit,  
ALIX: and pray the datasheet's right on it!  
XILA: Your pin's a file now, write it, see:  
XILA: slash devices, GPIO, D-thirteen!

**[Pre-Chorus]**  
ALIX: Can it run apps?  
XILA: Plural!  
ALIX: With files?  
XILA: And users!  
ALIX: So where's the real computer?  
XILA: You're holding it.  
ALIX: (I ordered a real computer.)

**[Chorus]**  
BOTH: Not your regular! (O-S!)  
XILA: A real OS on a chip, no less,  
XILA: same app on a desk, in a tab, yes, yes!  
BOTH: Not your regular! (O-S!)  
XILA: One signed package, three addresses,  
XILA: pocket-sized and fully dressed!  
BOTH: Not your regular! (O-S!)  
XILA: Try me in your browser tab! (Yes!)

**[Post-Chorus]**  
BOTH: Chip! Desk! Tab!  
BOTH: Same O-S! Same O-S!  
BOTH: Chip! Desk! Tab!  
BOTH: Pass it! (Hey!)  
BOTH: Tiny! Tidy!  
BOTH: Rusty! Open!  
BOTH: Chip! Desk! Tab!  
BOTH: Try it! Now!

**[Verse 2]**  
ALIX: My fern runs Fern Pings: 'Water. Now.'  
ALIX: My cat flap's Cat Customs: 'Papers? Meow.'  
XILA: Your doorbell's Ding Critic: 'Two out of ten,'  
XILA: your toaster's Toast Forecast: 'Burnt again.'  
ALIX: My alarm runs Snooze Court: 'Guilty! Rise!'  
ALIX: My bike runs Hill Snitch: 'Walked it!' (Lies!)  
XILA: Fridge Haiku wrote a sonnet on the ham,  
XILA: and the whole block's blasting Kazoo Jam!

**[Stop-Time]** _(spoken)_  
ALIX: Wait. A cat flap with apps?  
XILA: Imagined. For now.  
ALIX: And the OS? That small?  
XILA: Two-fifty-six kibibytes. Snug.

**[Chorus]**  
BOTH: Not your regular! (O-S!)  
XILA: A real OS on a chip, no less,  
XILA: same app on a desk, in a tab, yes, yes!  
BOTH: Not your regular! (O-S!)  
XILA: Built in Rust, no need to guess,  
XILA: open source, you've got access!  
BOTH: Not your regular! (O-S!)  
XILA: Try me in your browser tab! (Yes!)

**[Verse 3]**  
ALIX: An OS? On that? Get real,  
ALIX: a chip runs one job, that's the deal!  
XILA: Tasks, a shell and files, for real,  
XILA: on a chip you could lose in your meal!  
ALIX: So you're a firmware blob, I guess?  
ALIX: One giant binary, more or less?  
XILA: I'm a Rust library, I confess,  
XILA: build me in, I'll do the rest!

**[Boot Log]** _(the beat drops to kick, hats and bass; XILA recites its boot log deadpan and in rhythm, like a serial console, with a small synth blip on each status word; ALIX reacts with sung ad-libs)_  
ALIX: Build you in? So what's inside?  
XILA: Watch me boot.  
XILA: Memory: mapped. Time: ticking.  
XILA: Tasks: named. Executor: kicking.  
XILA: Files, pins and pipes: one tree, mounted.  
XILA: Users: checked. Root's in. You? Not counted.  
XILA: Got a screen? Graphics up. No screen? No drama.  
XILA: Drivers: whatever this board brought.  
XILA: Log: writing all of this down.  
XILA: Shell: ready. Your move.

**[Bridge]** _(late-night infomercial)_  
ALIX: Order now! The deluxe dev kit!  
XILA: Or open a tab.  
ALIX: A probe! A scope! Free socks!  
XILA: Or open a tab.  
ALIX: Call now: ninety jumper wires!  
XILA: Or open a tab.  
ALIX: Operators are standing by!  
XILA: Xila dot dev. Open a tab.

**[Breakdown]**  
ALIX: Kazoo Jam! Take it to the...  
XILA: Trap!  
ALIX: Did we just crash?  
XILA: The app did. I'm still here.  
ALIX: No watchdog reset?  
XILA: Nope. Hit it!

**[Final Chorus]**  
BOTH: Not your regular! (O-S!)  
XILA: A real OS on a chip, no less,  
XILA: same app on a desk, in a tab, yes, yes!  
BOTH: Not your regular! (O-S!)  
XILA: One app traps? I'm not impressed,  
XILA: kick keeps going, I'm still dressed!  
BOTH: Not your regular! (O-S!)  
XILA: Try me in your browser tab! (Yes!)

**[Drop]**  
BOTH: Not your regular! (O-S!) ×3  
BOTH: Not your regular!

_(Drop shortened from 8 to 4 hooks to pay for the Boot Log and keep the song near 3:00.)_

**[Outro]** _(whispered)_  
ALIX: So... do I flash you?  
XILA: Sure. Or open a tab.  
ALIX: Shh! We're in a library!  
XILA: I am a library.  
BOTH: (Not your regular.)
