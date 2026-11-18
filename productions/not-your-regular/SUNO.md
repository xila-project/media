# Out of the Loop: Suno version

> **En bref (FR)**
>
> - **Le contenu.** C'est le même morceau que le brouillon de la prise 006 ([takes/006-draft](takes/006-draft/NOTES.md)), mis au format Suno : un champ Style, un champ « Exclude styles » et les paroles avec des balises.
> - **Le but.** Comparer Suno à ElevenLabs à paroles et arrangement identiques. LWICD a été fait avec Suno.
> - **Ce que tu fais.** Tu génères 2 à 4 prises, tu régénères seulement les sections ratées avec « Replace Section », puis tu exportes en WAV, stems compris si possible.
> - **Où déposer les fichiers.** Dans `output/not-your-regular/listen/`. Je les analyse ensuite avec la même méthode que LWICD.
> - **Avant toute publication.** Il faut un abonnement payant pour un usage commercial. Les conditions ont changé après les accords avec les maisons de disques, vérifie-les avant de publier.

## Style field

Paste this into Suno's **Style** box (about 470 characters):

```
electropop, nu-disco, 130 bpm, A minor, euphoric, playful, cheeky, simple four-on-the-floor kick, dry claps on 2 and 4, straight 8th hi-hats, sparse bass that sits out in verses, big bass drop, hard stop-time breaks, chopped pitched vocal motif, young female gen-Z lead, insolent, flirty, verses chanted on one note with hard robotic autotune, glossy stacked hook, deep dry male spoken voice, intimate spoken dialogue in silences, clean bright mix, wide dynamics
```

## Exclude styles field

```
rap, hip hop, trap, talk-rap, shouting, belting, rock, metal, festival EDM, dubstep, rolling 16th bassline, reverb on spoken voice, male singing
```

## Lyrics field

Suno reads the bracketed tags as directions and sings the rest. Lines in parentheses are usually treated as backing vocals or speech, so each spoken line also gets a voice tag. The field is about 3,900 characters. Recent models accept about 5,000, while older ones cut off at about 3,000, so use the newest model.

```
[Intro]
[Spoken, no music, deep dry male voice]
Big day. I made the LED blink.
[Spoken, smug young female voice]
Cute. Hi.
[Spoken, male]
Who said that?
[Spoken, female]
The chip in your hand. I have an OS.
[Soft synth pad enters, no drums]
[Spoken, male]
Chips run a loop. While true.
[Spoken, female]
Not this one.
[Spoken, male]
So what are you?
[Spoken, female]
Out of the loop.

[Instrumental]
[Beat drops in, chopped vocal motif, no bass]
(O-S, o-o-S, o-o-S)

[Verse 1]
[Female lead, monotone chant on one note, hard autotune, no bass]
You wrote a loop that never ends,
with seven flags and global friends,
you poke registers bit by bit
and pray the datasheet is right.
A shell, some users: here I am,
in two-fifty-six K of RAM.
Your pin's a file now, write it, see:
slash devices, GPIO, D-thirteen!

[Pre-Chorus]
[Female lead, teasing, autotuned]
Can it run apps? Plural!
With files? And users!

[Stop]
[Silence, spoken, male]
Where's the real computer?
[Spoken, female, purring]
Your pocket. Happy to see me?

[Chorus]
[Female lead, glossy stacked hook, full beat with bass]
Out of the loop!
Out of the loop!
A real OS on a chip, no less,
same app on a desk, in a tab, yes, yes!
Out of the loop!
Out of the loop!
One signed package, three addresses,
pocket-sized and fully dressed!

[Post-Chorus]
[Female chant, stacked]
Chip! Desk! Tab!
Same O-S, same O-S!
Chip! Desk! Tab!
Made in Rust! Try it in a tab!

[Verse 2]
[Female lead, monotone chant on one note, hard autotune, no bass]
Your fern? Fern Pings: 'Water. Now.'
Your cat flap? Cat Customs: 'Papers? Meow.'
Doorbell? Ding Critic: 'Two out of ten.'
Toaster? Toast Forecast: 'Burnt again.'
Your alarm? Snooze Court: 'Guilty. Rise.'
Your bike? Hill Snitch: 'Walked it. Twice.'
Fridge Haiku wrote a sonnet on the ham,
and the whole block's blasting Kazoo Jam!

[Stop]
[Silence, spoken, male]
Wait. A cat flap with apps?
[Spoken, female]
Imagined. For now.
[Spoken, male]
And the OS? That small?
[Spoken, female]
Two-fifty-six K. Snug.

[Chorus]
[Female lead, glossy stacked hook, full beat with bass]
Out of the loop!
Out of the loop!
A real OS on a chip, no less,
same app on a desk, in a tab, yes, yes!
Out of the loop!
Out of the loop!
Built in Rust, no need to guess,
open source, you've got access!

[Verse 3]
[Female lead, monotone chant, hard autotune, no bass]
'An OS? On that? Get real.
A chip runs one job. That's the deal.'
I'm a Rust library, I confess,
build me in, I'll do the rest!

[Break]
[Female lead, cool monotone recitation, kick only]
Watch me boot. Memory: mapped.
Tasks: named. Files, pins and pipes: one tree.
Users: checked. You? Not counted.
Drivers: whatever this board brought. Shell: ready. Your move.

[Bridge]
[No drums, campy TV jingle, electric piano, female lead sings]
Device makers! Tired of this?
[Spoken, male]
Forty customers. Forty firmware forks.
[Female, sung]
One base! Apps on top!
[Spoken, male]
One tiny fix. Reflash the whole fleet.
[Female, sung]
Update the app! That's the plan!
[Spoken, male]
Is this an ad?
[Female, sung]
Operators are standing by!
Xila dot dev. Let's talk.

[Breakdown]
[Lone soft kick only, spoken, female]
Kazoo Jam! Take it to the...
[Spoken, male]
Trap. Did we just crash?
[Spoken, female]
The app did. I'm still here.
[Spoken, male]
No watchdog reset?
[Spoken, female]
Nope. Hit it!

[Final Chorus]
[Female lead, biggest hook, drums but no bass]
Out of the loop!
Out of the loop!
A real OS on a chip, no less,
same app on a desk, in a tab, yes, yes!
Out of the loop!
Out of the loop!
One app traps? I'm not impressed,
kick keeps going, I'm still dressed!

[Drop]
[Loudest part, full bass, chopped vocal motif]
Out of the loop!
(O-S, o-o-S)
Out of the loop!
(O-S, o-o-S)

[Outro]
[Silence, whispered, male]
So... do I flash you?
[Whispered, female]
Sure. Or open a tab.
[Whispered, male]
Shh. We're in a library.
[Whispered, female]
I am a library.
[Instrumental]
[Beat returns for two bars, hard stop]

[End]
```

## Steps for the maintainer

1. **Choose the model.** In Suno's Create panel, choose **Custom** mode and pick the newest model offered: v5 or later at the time of writing.
2. **Fill in the three fields.** Paste the Style, Exclude styles and Lyrics fields above. Turn off Instrumental and leave the weirdness and style sliders at their defaults for the first round.
3. **Generate 2–4 takes and keep the best.** Judge them on these four points:
   - the verses are chanted on one note, not rapped;
   - the stops are real silences;
   - the male voice only speaks;
   - the drop is the loudest part.
4. **Fix broken sections without regenerating the song.** Use **Replace Section** in the song editor for things like a swapped voice or a missing line. Select the bars, keep the same lyrics, and regenerate only that part.
5. **Export the best take.** Download it as **WAV**. If your plan offers stems, also export them (vocals, drums, bass, instruments): they let us rebalance the mix and swap in your voice clone.
6. **Drop the files where the analysis can read them.** Put them in `output/not-your-regular/listen/`, named for example `suno-001.wav` plus `suno-001-stems/`. They are then analysed with the same measurements as LWICD and take 005: tuning, rhythm grid, arrangement map and loudness.

## Licensing caution

Suno grants commercial-use rights only for songs generated while on a paid plan. Free-tier songs stay non-commercial even if you upgrade later. The terms, the available models and the download rules changed after Suno's 2025 agreements with the record labels, and may change again. Before using a Suno take in the published trailer:

- read the current Terms of Service and plan page;
- keep a copy or screenshot of them with the take's provenance;
- record the plan, the model version and the generation date in the take's `provenance.json`, as for the ElevenLabs takes.
