# Out of the Loop: lyrics v3

These lyrics were drafted on 2026-11-18 and replace v2 (LYRICS-v2.md). The maintainer approved four changes:

- **Hook "Out of the loop! (O-S!)".** It replaces "Not your regular", which assumed a mainstream embedded OS that does not exist. The default on a microcontroller is no OS at all, just a `while(true)` superloop. The hook reads two ways: XILA has left the superloop, and ALIX, the old-school developer, is "out of the loop".
- **Inverted casting**, following the Argon blueprint (LWICD-BLUEPRINT.md, §7):
  - **XILA** is the insolent, playful, slightly flirty gen-Z female pop lead. She sings the hooks and the brags, purrs the boot log and whispers the ending.
  - **ALIX** is the dry, low, deadpan male firmware developer. He mostly speaks or talk-sings, which also suits converting his lines to the maintainer's voice clone.
- **Bridge.** The late-night infomercial now targets device makers, using the business thesis in `business/`: firmware forks per customer, reflashing a fleet for one fix.
- **One flirty wink** in the pre-chorus ("Happy to see me?").

The dense lines were thinned after the take 003 reviews. Verse 2 uses a cleaner "Your X? App name: quote" pattern, and the boot log loses two lines. An instrumental hook follows the intro.

## Claim check

- **True today:**
  - Nano 33 BLE (256 KiB RAM) with a shell, users, LittleFS and GPIO device files (`/devices/gpio/d13`).
  - The same signed bundle on desktop, browser and container.
  - App trap containment on hosted runtimes.
  - Core subsystems Task, VFS, Users and Memory, with per-platform drivers.
  - Rust library, Apache-2.0, browser demo.
- **Roadmap, said as such or allowed in copy by the 2026-11-11 maintainer decision:**
  - "Plural!" apps on a microcontroller (ESP32-S3 port).
  - "No watchdog reset?" on a chip.
  - Bridge: "One base. Apps on top." / "Update the app. That's the plan!" The business communication rule forbids promising independent updates as done, so the line names it as the plan.
- **Imagined:** the eight gadget apps ("Imagined. For now.").

## Lyrics

**[Intro]** _(beat-less, dry, spoken)_  
ALIX: Big day. I made the LED blink.  
XILA: Cute. Hi. I'm here.  
ALIX: Who said that?  
XILA: The chip in your hand.  
ALIX: That's a microcontroller.  
XILA: A microcontroller with an OS.  
ALIX: Chips run a loop. While true.  
XILA: Not this one.  
ALIX: So what are you?  
XILA: Out of the loop.

**[Intro Hook]** _(instrumental: the groove drops in with the pitched vocal-synth pluck motif)_

**[Verse 1]**  
ALIX: I wrote a loop that never ends,  
ALIX: with seven flags and global friends.  
XILA: A shell, some users, here I am,  
XILA: in two-fifty-six kibibytes of RAM!  
ALIX: I poke a register bit by bit,  
ALIX: and pray the datasheet's right on it.  
XILA: Your pin's a file now, write it, see:  
XILA: slash devices, GPIO, D-thirteen!

**[Pre-Chorus]**  
ALIX: Can it run apps?  
XILA: Plural!  
ALIX: With files?  
XILA: And users!  
ALIX: So where's the real computer?  
XILA: In your pocket. Happy to see me?  
ALIX: (I ordered a real computer.)

**[Chorus]**  
XILA: Out of the loop! (O-S!)  
XILA: A real OS on a chip, no less,  
XILA: same app on a desk, in a tab, yes, yes!  
XILA: Out of the loop! (O-S!)  
XILA: One signed package, three addresses,  
XILA: pocket-sized and fully dressed!  
XILA: Out of the loop! (O-S!)  
XILA: Try me in your browser tab! (Yes!)

**[Post-Chorus]**  
BOTH: Chip! Desk! Tab!  
BOTH: Same O-S! Same O-S!  
BOTH: Chip! Desk! Tab!  
BOTH: Pass it! (Hey!)  
BOTH: Tiny! Tidy!  
BOTH: Made in Rust! Open source!  
BOTH: Chip! Desk! Tab!  
BOTH: Try it! Now!

**[Verse 2]**  
XILA: Your fern? Fern Pings: 'Water. Now.'  
XILA: Your cat flap? Cat Customs: 'Papers? Meow.'  
XILA: Your doorbell? Ding Critic: 'Two out of ten.'  
XILA: Your toaster? Toast Forecast: 'Burnt again.'  
XILA: Your alarm? Snooze Court: 'Guilty. Rise.'  
XILA: Your bike? Hill Snitch: 'Walked it.'  
ALIX: (Lies.)  
XILA: Fridge Haiku wrote a sonnet on the ham,  
XILA: and the whole block's blasting Kazoo Jam!

**[Stop-Time]** _(spoken)_  
ALIX: Wait. A cat flap with apps?  
XILA: Imagined. For now.  
ALIX: And the OS? That small?  
XILA: Two-fifty-six kibibytes. Snug.

**[Chorus]**  
XILA: Out of the loop! (O-S!)  
XILA: A real OS on a chip, no less,  
XILA: same app on a desk, in a tab, yes, yes!  
XILA: Out of the loop! (O-S!)  
XILA: Built in Rust, no need to guess,  
XILA: open source, you've got access!  
XILA: Out of the loop! (O-S!)  
XILA: Try me in your browser tab! (Yes!)

**[Verse 3]**  
ALIX: An OS? On that? Get real.  
ALIX: A chip runs one job. That's the deal.  
XILA: Tasks, a shell and files, for real,  
XILA: on a chip you could lose in your meal!  
ALIX: So you're a firmware blob, I guess.  
ALIX: One giant binary, more or less.  
XILA: I'm a Rust library, I confess,  
XILA: build me in, I'll do the rest!

**[Boot Log]** _(stripped pulse; XILA recites, cool and unbothered)_  
ALIX: Build you in? So what's inside?  
XILA: Watch me boot.  
XILA: Memory: mapped. Time: ticking.  
XILA: Tasks: named. Executor: kicking.  
XILA: Files, pins and pipes: one tree, mounted.  
XILA: Users: checked. Root's in. You? Not counted.  
XILA: Drivers: whatever this board brought.  
XILA: Shell: ready. Your move.

**[Bridge]** _(late-night infomercial for device makers; XILA is the cheesy pitchwoman, ALIX the weary engineer)_  
XILA: Device makers! Tired of this?  
ALIX: Forty customers. Forty firmware forks.  
XILA: One base! Apps on top!  
ALIX: One tiny fix. Reflash the whole fleet.  
XILA: Update the app! That's the plan!  
ALIX: (Is this an ad?)  
XILA: Operators are standing by!  
XILA: Xila dot dev. Let's talk.

**[Breakdown]**  
XILA: Kazoo Jam! Take it to the...  
ALIX: Trap.  
ALIX: Did we just crash?  
XILA: The app did. I'm still here.  
ALIX: No watchdog reset?  
XILA: Nope. Hit it!

**[Final Chorus]**  
XILA: Out of the loop! (O-S!)  
XILA: A real OS on a chip, no less,  
XILA: same app on a desk, in a tab, yes, yes!  
XILA: Out of the loop! (O-S!)  
XILA: One app traps? I'm not impressed,  
XILA: kick keeps going, I'm still dressed!  
XILA: Out of the loop! (O-S!)  
XILA: Try me in your browser tab! (Yes!)

**[Drop]**  
XILA: Out of the loop! (O-S!) ×3  
XILA: Out of the loop!

**[Outro]** _(whispered)_  
ALIX: So... do I flash you?  
XILA: Sure. Or open a tab.  
ALIX: Shh. We're in a library.  
XILA: I am a library.  
XILA: (Out of the loop.)
