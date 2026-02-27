# Timbre, Melody-Memory, and the Major/Minor Paradox

_2026-02-25 — Session 3 findings_

## Overview

Three questions going in. One surprise big enough to reframe the whole model.

1. Does instrument timbre (violin vs clarinet vs flute) change consonance?
2. Is melodic tension just "remembered interference" from sequential notes?
3. Why does minor feel different from major if their LCM complexity is similar?

---

## 1. Timbre and the Effective Consonance Landscape

### The model

Real instruments don't produce pure sine waves. They produce harmonic series where each partial has a different amplitude. Consonance score for an interval = sum of products of amplitudes at each shared harmonic frequency.

**Five timbre profiles modeled:**
| Instrument | Spectral character |
|------------|-------------------|
| Pure sine  | Only fundamental (1st harmonic) |
| Flute      | Strong 1st–2nd, weak upper harmonics |
| Violin     | All harmonics, 1/n^0.7 falloff — rich and warm |
| Piano      | 1/n^1.5 falloff — rounder than violin |
| Clarinet   | **Odd harmonics only** (cylindrical bore physics) |
| Trumpet    | All harmonics, strong 2nd–4th — bright, brassy |

### Key findings

**Finding 1: Timbre compresses the consonance range, it doesn't reorder it.**

Across all six timbre profiles, the consonance ranking of intervals stays the same: octave → fifth → fourth → major third → minor third → ... → tritone. Timbre changes *how much* difference there is between intervals, not which interval is more consonant. The ranking is preserved because it's set by the integer structure of the ratios, not by spectral weight.

**Finding 2: The clarinet exception — hollow fifths.**

The clarinet's odd-harmonic spectrum creates a striking effect. In a fifth (3:2):
- The 3rd harmonic of the lower note (position 3) aligns with the 2nd harmonic of the upper note (position 2)
- But the 2nd harmonic of the lower note is **suppressed** in the clarinet
- Result: the clarinet fifth has significantly fewer weighted harmonic overlaps than a violin fifth

This is why two clarinets playing a fifth together sound "hollow" or "open" compared to two violins on the same interval. The mathematical consonance is unchanged (LCM is still 6), but the **timbral consonance** — the actual overlapping energy in the air — is reduced.

Practical implication: the clarinet compensates by voicing fifths carefully, and clarinet concertos often use thirds and sixths more heavily (those less dependent on even-harmonic overlap).

**Finding 3: The trumpet is "harmonically noisy."**

Trumpet's rich spectrum (strong 2nd, 3rd, 4th harmonics) means its consonance scores are high but *also* its dissonance scores for "bad" intervals are higher. The trumpet interval matrix has more contrast — consonances are very consonant, dissonances are very dissonant. The instrument is acoustically "louder" about harmonic relationships.

This maps to something listeners know intuitively: a trumpet playing a minor second cuts through in a way a flute's minor second doesn't. The same mathematical roughness, but more spectral energy to activate it.

---

## 2. Melody as Remembered Interference

### The model

When you hear note A, then note B, you don't experience B in isolation. The brain holds A in working memory, and for some period, the two notes "interfere" as if they were simultaneous. The memory of A decays exponentially — roughly 300–600ms for tonal memory.

Model: `combined(t) = sin(2π·f_B·t) + e^{-λt} · sin(2π·f_A·t)`

Where λ is the decay constant (higher = faster forgetting).

### Three melodic steps analyzed

**C → G (Perfect Fifth, 3:2, LCM = 6)**
Combined waveform completes a cycle in 6 fundamental periods. Even with memory decay cutting the amplitude, the pattern repeats fast enough for the brain to "get" it before the memory fades. The Lissajous portrait shows a clean figure-8 trajectory — recognizable geometry. Perceptual result: the memory of C "supports" the arrival of G, creating a sense of arrival.

**C → E (Major Third, 5:4, LCM = 20)**
More complex but still resolvable within reasonable memory window. The Lissajous shows a recognizable oval sweep — more complex than the fifth but still structured. Perceptual result: C and E feel "warm" together in memory — the brain almost resolves the pattern, leaving a pleasant but slightly open feeling.

**C → F# (Tritone, 45:32, LCM = 1440)**
Combined waveform has a period of 1440 fundamental cycles. At 440 Hz, one fundamental cycle = 2.27ms, so the period = ~3.3 *seconds*. The brain's tonal memory window is ~0.3–0.6 seconds. The pattern **never completes within memory duration**. What the brain hears is: a structureless, aperiodic interference that never resolves. The Lissajous portrait is a dense, space-filling tangle — no recognizable shape. Perceptual result: the memory of C actively destabilizes F#. The brain has unfinished business. It wants to move.

### The tension arc model

Applied this to a melodic phrase: **C–E–G–F#–G–E–C**

Running accumulated tension (current note's LCM complexity + decayed previous tension + step interval complexity):
- C: baseline tension (reference)
- E: slight rise (major third from C, LCM=20)
- G: eases (fifth from C, LCM=6 — tension drops as we reach stability)
- F#: **PEAK** — tritone from C lodged in memory, tritone from G (45:32 again)
- G: relief (back to stable fifth)
- E: moderate (familiar third)
- C: return to tonic — full resolution

The math correctly predicts the emotional arc. F# at the peak is where the phrase "wants" to move — and it does, back to G. The model captures the idea that a melody creates tension by introducing notes with long LCM periods relative to the tonal center, then releases by resolving back to short-LCM positions.

---

## 3. The Major/Minor Paradox — A Surprise

Going in, I expected minor to be "more complex" than major by LCM analysis, since:
- Major third: 5:4, LCM = 20
- Minor third: 6:5, LCM = 30

So minor third ≈ 50% more complex. But when I analyzed **triads** (not just intervals), something unexpected emerged.

### The calculation

For a triad, you have three pairwise intervals: root→third, root→fifth, third→fifth.
Total triad complexity = LCM of all three pairwise LCMs.

| Triad | Root→3rd | Root→5th | 3rd→5th | **Total LCM** |
|-------|----------|----------|---------|---------------|
| Major (1 : 5/4 : 3/2) | 20 | 6 | 30 | **60** |
| Minor (1 : 6/5 : 3/2) | 30 | 6 | 20 | **60** |

**Major and minor triads have identical total LCM complexity: 60.**

This is not coincidence. The triad is symmetric:
- Major: {root→third = 5:4} and {third→fifth = 6:5}. Both intervals are present, just in different positions.
- Minor: {root→third = 6:5} and {third→fifth = 5:4}. Same two intervals, inverted.

The notes C, E♭, G contain the same pair of intervals (major and minor third) as C, E, G. The order differs. The total complexity is the same.

### So what IS the difference?

If total LCM complexity is identical, why do major and minor feel so different?

Several converging explanations:

**1. The "entry interval" matters.**

In major, you reach the triad through the *less* complex interval first (5:4, LCM=20). The root→third relationship is simpler, so the chord establishes itself quickly. In minor, you reach it through the *more* complex interval (6:5, LCM=30). The chord is "harder to get into" — it takes longer for the brain to recognize the root→third pattern. The fifth ties them together (LCM=6 in both cases).

This is like the difference between a door that swings open easily vs one with more resistance. Same room, different entrance experience.

**2. Position in the harmonic series.**

The major third (5:4) appears between harmonics 4 and 5 of the fundamental. The minor third (6:5) appears between harmonics 5 and 6. Higher in the series = weaker in amplitude = less "naturally resonant" = takes more cognitive effort to latch onto.

When a fundamental plays, its 4th and 5th harmonics are louder than its 5th and 6th. So the major third has a stronger "acoustic pre-activation" in the harmonic series of the root note. It's more "expected" from the physics. Minor third is less expected — it requires constructing a relationship that physics presents with less amplitude.

**3. Cultural amplification of a small physical signal.**

The physical difference is small (50¢, half a semitone, LCM=20 vs 30). The cultural weight we've attached to it — minor = sad, threatening; major = happy, resolved — is vastly larger than the physical signal. But the physical signal *points* in the right direction, and culture amplified it into a strong code.

This is a pattern worth noting: music often takes small mathematical differences and amplifies them via learned association into large emotional effects. The tritone's danger-signal status in film music is partly cultural, but grounded in real LCM complexity (1440).

### Diminished and Augmented for contrast

| Triad | Total LCM | Character |
|-------|-----------|-----------|
| Major | 60 | Stable, bright |
| Minor | 60 | Stable, darker |
| Augmented | 800 | Unsettled, floating |
| Diminished | 14,400 | Maximally unstable |

Diminished (LCM=14,400) is 240× more complex than major. No wonder it signals imminent disaster in Romantic music. The tritone fifth (45:32) is doing the heavy lifting there — LCM=1440 per pairwise relationship.

---

## 4. Harmony vs Melody: Information Rates

A final observation that emerged from modeling: when C-E-G are played simultaneously (chord), all three interference patterns are active at once. When played sequentially (melody), each pattern must be held in memory while the next arrives.

**Frequency domain consequence:** A chord has sharp, clean frequency peaks at exactly three frequencies. A melody has *smeared* peaks — because note transitions introduce bandwidth (time-limited signals are always broader in frequency). A chord is more frequency-localized; a melody trades frequency precision for temporal structure.

This is a time-frequency tradeoff (Heisenberg uncertainty in acoustics applies — you cannot have perfect frequency resolution AND perfect time resolution simultaneously). Melody exploits temporal resolution at the cost of frequency clarity. Harmony exploits frequency resolution at the cost of temporal sequence.

This suggests: **harmony is to space as melody is to time.** Chords are spatial structures (many relationships present at once); melodies are time structures (one relationship then another, memory bridging the gaps).

---

## Summary of Session 3 Findings

| Finding | Implication |
|---------|-------------|
| Timbre preserves consonance ranking but changes amplitude | Same interval, different "weight" — explains instrument voice choices |
| Clarinet hollow fifth | Odd harmonics reduce overlap; clarinet prefers thirds and sixths |
| Melodic tension = remembered interference | F# in C major context is objectively maximally destabilizing |
| Major and minor triads have equal total LCM (60) | The difference isn't complexity — it's which interval you enter through |
| Minor third higher in harmonic series | Minor has less "acoustic pre-activation" from the root |
| Diminished triad LCM = 14,400 | 240× more complex than major; maximal instability justified |
| Melody = time structure, Harmony = frequency structure | Heisenberg tradeoff between temporal and spectral precision |

## New Visualizations (2026-02-25)

- `timbre_consonance.png` — 6 instrument timbres × 9 intervals, consonance landscapes
- `clarinet_detail.png` — odd harmonic spectrum and its consequences for fifths
- `melody_memory.png` — fifth/third/tritone as remembered interference with Lissajous portraits
- `melodic_tension_arc.png` — C–E–G–F#–G–E–C arc with accumulated tension model
- `minor_vs_major.png` — triad LCM analysis, the equal-complexity paradox, harmonic series position
- `harmony_vs_melody.png` — time-frequency tradeoff between simultaneous and sequential notes

## Questions for Next Session

1. **Voice leading as LCM minimization?** When composers write chord progressions, they move voices to minimize stepwise motion. Is this actually minimizing the LCM complexity of each voice's movement? Does "smooth voice leading" have a concrete LCM explanation?

2. **The tritone substitution (jazz harmony):** F#7 can replace C7 as a dominant chord. F# and C are a tritone apart. Why does this "work" despite maximal LCM complexity? Is there something else going on?

3. **Rhythm meets melody:** The polyrhythm analog (session 2) showed LCM applies to both pitch and time. Can we unify them into a single model? A note is a pitch + duration. Is there a 2D LCM that captures both simultaneously?

4. **The physics of minor "sadness" — temperature model:** What if emotional valence maps to LCM gradient — the *change* in complexity as a melody moves? High → low (resolution) = satisfaction. Low → high (tension) = unease. Minor key = higher average gradient? Can we plot emotional arc as LCM gradient over time?

---

**Bottom line from session 3:** The surprise was the symmetry. Major and minor are more alike than different — same total complexity, same notes rearranged. What makes them feel different is which interval you encounter first. The brain judges harmonic quality at the *door*, not the room. Culture takes that whisper of a difference and turns it into major/minor as a fundamental emotional code.
