# Waveform Interference & the Polyrhythm Analog

_2026-02-23 — Session 2 findings_

## The LCM Principle: Consonance in One Formula

The deepest mathematical explanation for why simple ratios sound consonant is this:

> **Two sine waves with frequency ratio p:q create a combined waveform that repeats every lcm(p,q) cycles.**

| Interval         | Ratio  | LCM Period | Interpretation                        |
|------------------|--------|------------|---------------------------------------|
| Unison           | 1/1    | **1**      | Always in phase — perfect lock        |
| Octave           | 2/1    | **2**      | Repeats every 2 cycles of fundamental |
| Perfect Fifth    | 3/2    | **6**      | Needs 6 cycles to complete            |
| Perfect Fourth   | 4/3    | **12**     | Needs 12 cycles                       |
| Major Third      | 5/4    | **20**     | Needs 20 cycles                       |
| Minor Third      | 6/5    | **30**     | Needs 30 cycles                       |
| Major Second     | 9/8    | **72**     | Getting complex                       |
| Minor Second     | 16/15  | **240**    | Very complex                          |
| Tritone          | 45/32  | **1440**   | ~33ms at 440Hz — effectively aperiodic|

The brain tracks recurring patterns. Short LCM period = predictable = "resolved". Long LCM period = unpredictable = "unresolved". This maps exactly onto the perceptual spectrum from consonance to dissonance.

## Three Confirming Mechanisms

All three mechanisms from session 1 now have numerical backing:

### 1. Harmonic Series Overlap
Using 32 harmonics each:
- Octave (2:1): **16 shared harmonics** — every other harmonic of the upper note is a harmonic of the lower
- Perfect Fifth (3:2): **10 shared harmonics** — every 3rd harmonic of the lower aligns with every 2nd of the upper
- Tritone (45:32): **0 shared harmonics** — no overlap at all in the first 32 harmonics

The formula: for ratio p/q in lowest terms, the nth overlap occurs at every lcm(p,q) harmonics of the fundamental.

### 2. Beat Frequencies and Roughness
"Roughness" = pairs of harmonics within 5–35 Hz of each other (audible beating zone):
- Octave, Fifth, Fourth, Major Third, Minor Third: **0 rough pairs** (clean!)
- Minor Second (16/15): **4 rough pairs** (most rough of standard intervals)
- Tritone (45/32): **3 rough pairs**

This explains why thirds and fourths sound "smooth" even though they're not as simple as fifths.

### 3. Waveform Periodicity (Lissajous)
Plotting wave1 vs wave2 in x-y space (Lissajous figure):
- Simple ratios → **simple closed geometric curves** (easily recognizable shapes)
- Complex ratios → **dense, space-filling spirals** (visually chaotic)

The Lissajous figure for 2:1 is a clean parabola. For 3:2: a figure-8. For 45:32: an indistinguishable tangle. The brain has a geometric intuition about these shapes — it tracks curves, not tangles.

## The Polyrhythm Analog — Key Finding

**Question:** Is the 3:2 relationship "consonant" when applied to rhythm the same way it's consonant in pitch?

**Model:** Two pulse trains, one firing every p beats and one every q beats. Consonance = how often they coincide.

| Rhythm     | LCM Period | Coincidence rate |
|------------|------------|------------------|
| 2:1        | 2          | Every 2 beats    |
| **3:2**    | **6**      | Every 6 beats    |
| 4:3        | 12         | Every 12 beats   |
| 5:4        | 20         | Every 20 beats   |
| 7:4        | 28         | Every 28 beats   |
| **7:5**    | **35**     | Every 35 beats   |
| 11:8       | 88         | Every 88 beats   |

**Finding:** Yes — the same LCM principle applies. The 3:2 polyrhythm (common in African and West African music, jazz, Chopin) has a short period of 6 beats — it "resolves" quickly and feels groovy rather than messy. The 7:5 analog of the tritone (LCM=35) would feel disorienting and unresolvable.

**The deep structural connection:** Rhythm and pitch are both pattern-matching problems. The brain asks "when does this repeat?" Simple ratios → short answers → satisfaction.

## Why This Matters for Music

### The octave as identity
The octave (2:1) is so consonant it's practically a unison — 16 of 32 harmonics are shared, and the period is just 2. This is why notes an octave apart have the same name. They're acoustically "the same pitch class" from the harmonic perspective.

### The fifth as the engine of tonality
The perfect fifth (3:2, LCM=6, 10 harmonic overlaps) is close enough to consonant that it feels stable, but not identical. This makes it the ideal "next step" from the tonic — familiar but different. The circle of fifths (stacking 3:2 ratios) generates all 12 pitch classes, which is why it's the backbone of Western harmony.

### The fourth as the mirror fifth
The perfect fourth (4:3) is the inversion of the fifth — if you flip a fifth upside down within an octave, you get a fourth. Same LCM structure (12 vs 6 — double, because it's two steps removed). Slightly more complex, which is why it feels slightly less stable, but still clearly consonant.

### Why equal temperament works despite being "wrong"
All equal-tempered intervals (except the octave) are irrational ratios — they don't have exact integer relationships. But they're *close* to simple fractions:
- ET fifth: 1.4983... ≈ 1.500 (3:2) — close enough for LCM intuition to fire
- ET major third: 1.2599... ≈ 1.25 (5:4) — slightly further, which is why ET thirds sound slightly harsh

The brain rounds to nearby simple fractions. ET is a rounding error that's small enough to be acceptable.

## Questions for Next Session

1. **Timbre effects:** Real instruments produce complex waveforms (not pure sines). A violin has strong odd harmonics; a clarinet emphasizes different ones. Does timbre change the effective "LCM" of consonance?

2. **Melody without harmony:** Single-note sequences don't interfere in real time, but memory creates "virtual" simultaneous tones. When you hear C then G, the brain holds both. Is this "remembered interference" the mechanism behind melodic tension and resolution?

3. **Culture and the minor key:** Minor third (6:5, LCM=30) is "sadder" than major third (5:4, LCM=20) across many cultures. Is this perceptual (the more complex LCM feels more unstable) or cultural (learned association)?

4. **The tritone as dramatic device:** Tritone (45:32, LCM=1440, 0 overlaps) is maximally dissonant. Why do composers reach for it to signal danger or tension? Is there something about maximal disorder that maps to threat?

## New Visualizations (2026-02-23)

- `interference_comparison.png` — 6 intervals, 40ms of combined waveform
- `harmonic_overlap.png` — harmonic series bars with shared harmonics marked
- `lissajous_consonance.png` — phase portraits showing simplicity gradient
- `consonance_scores.png` — 3-panel metrics: period, overlaps, roughness
- `polyrhythm_analysis.png` — pulse train grids with coincidence highlighting

---

**Bottom line:** Consonance is a measure of how quickly a pattern resolves. Everything else is a consequence of that. Octaves resolve instantly. Fifths in 6 cycles. Tritones in 1440. The brain, which is fundamentally a pattern-completion engine, reflects this back as pleasure or discomfort.
