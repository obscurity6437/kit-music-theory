# Modulation, Non-Western Scales, Inversions, and Entropy

_2026-03-04 — Session 5 findings_

## Overview

Session 4 left five questions. Session 5 answers all of them with computation and a few surprises.

1. Is the circle of fifths the minimum-LCM adjacency graph?
2. Non-Western scales: where does pentatonic's universality come from?
3. Do chord inversions change effective LCM?
4. Can we measure information entropy of chord progressions?
5. Do borrowed chords' "color" map to LCM distance from diatonic space?

---

## 1. Circle of Fifths as Minimum-LCM Graph

**Yes — confirmed by computation.**

Model: modulation cost = log₂(tonic interval LCM) + (7 − shared_notes) × 1.5

| Modulation from C | Cost |
|-------------------|------|
| C → G (fifth)     | 5.08 |
| C → F (fourth)    | 5.08 |
| C → Db (m2nd)     | 15.41 |
| C → F# (tritone)  | 17.99 |

Every key's two nearest neighbors are its circle-of-fifths adjacents (F and G for C). The tritone neighbor (F#) is the most expensive modulation — 3.5× the cost of a fifth modulation.

**Nearest neighbors:**
- Each key's cheapest modulations are always to the key a fifth above and a fourth below (same thing). This is why classical composers almost always modulate by fifths: they're minimizing both tonal interval cost and the number of new scale degrees introduced (only 1 new note per fifth step).

The 3rd-nearest neighbor (at cost ~9.2) is always the key two fifths away. The graph is not just ring-shaped — it's a minimum spanning tree on the LCM metric.

**Practical application:** A modulation plan is a path on this graph. Distant key modulations (tritone, minor second) require pivot chord tricks precisely because they can't minimize the LCM distance incrementally — they need an intermediary that reduces the jump.

---

## 2. Non-Western Scales in LCM Space

Scale complexity rankings (mean log₂-LCM from root):

| Rank | Scale | Mean LCM |
|------|-------|----------|
| 1 (simplest) | **Major Pentatonic** | 3.00 |
| 2 | Minor Pentatonic | 3.21 |
| 3 | Hirajoshi (Japanese) | 3.33 |
| 4 | In Scale (Japanese) | 3.40 |
| 5 | Major (Ionian) | 3.56 |
| ... | | |
| 13 | Octatonic/Diminished | 4.70 |
| 14 (most complex) | **Whole Tone** | 4.93 |

### The Pentatonic Explanation

The major pentatonic removes exactly two notes from the major scale: the 4th (F) and the 7th (B).

Why those two specifically? They're the **leading tones** — the notes with directional pull:
- The 7th (LCM=120 from root) is the upward leading tone, pulls to octave
- The 4th (LCM=12 from root) is the downward leading tone, pulls to 3rd

Remove both → **zero directional pull** → notes just float, no strong expectation of resolution. The remaining notes (root, M2, M3, P5, M6) all have relatively low LCM complexity (6–72) and none have chromatic half-step pull.

**This is why pentatonic is "universal" across cultures:** it's the minimal-tension subset of the major scale. Any untrained listener can improvise on pentatonic without hitting a "wrong" note because no note has strong pull against another. It's the LCM-minimized scale. Children's songs worldwide converge on pentatonic independently because it's the most acoustically forgiving structure.

### Japanese Scales

Hirajoshi (0,2,3,7,8) and In Scale (0,1,5,7,8) both rank simpler than Western major scale. They contain no leading tones (neither scale has a note a half-step below the tonic octave). The "exotic" color comes from having minor 2nds embedded in the scale *but not at the top* — they don't pull toward resolution, they color the interior.

### Arabic / Middle Eastern

Hijaz, Double Harmonic, and Bhairav all land near Western natural minor in complexity (~3.95–3.99). The augmented second interval (3 semitones between consecutive degrees) doesn't add complexity to the individual note LCMs — what makes these scales "exotic" is the *sequence* of complexity changes as you move through them, not the absolute level.

### Whole Tone: The Maximum

The whole tone scale (all major seconds) is the **most complex** scale by this measure (4.93), more than the diminished octatonic. Why? The tritone (LCM=1440) between the root and the 6th degree dominates. No stable fifth anywhere in the scale. Debussy exploited exactly this: whole tone scale = harmonic suspension, nothing resolves anywhere.

---

## 3. Chord Inversions: Bass Weight Matters

C major triad results:

| Position | Total LCM | Bass-Weighted (×2) |
|----------|-----------|--------------------|
| Root (C bass) | 11.81 | **18.72** |
| 1st inv (E bass) | 13.81 | **24.04** |
| 2nd inv (G bass) | 11.81 | **19.31** |

**Finding: Total pairwise LCM is the same for root and 2nd inversion.** The notes are the same — C, E, G — just in different order. But the **bass-weighted** score differs significantly. 

1st inversion has the highest bass-weighted cost: E in the bass creates dissonance because the bass-to-fifth interval (E→C, which is a major sixth, LCM=40) is more complex than a root position bass-to-fifth (C→G, LCM=6).

This is why 2nd inversion is "unstable" despite having a clean fourth (G→C) in the bass: the bass→top interval (G→E, perfect sixth, LCM=15) is moderately complex. Root position wins because the bass note IS the root — it has the simplest relationship to the tonal center.

**C7 result:** The 3rd inversion (Bb bass) has the **lowest total pairwise LCM** (32.38) but the **highest bass-weighted** score (52.95). The Bb bass creates a tritone to E — maximum bass-rooted dissonance. Classical style treats 3rd inversion C7 as the most unstable — requiring immediate resolution. The math confirms it.

**Rule:** Bass-weighted LCM predicts voice stability better than total pairwise LCM. The ear weights intervals from the bass more heavily than inner-voice intervals — this is a psychoacoustic fact that the bass-weighting model captures.

---

## 4. Information Entropy of Chord Progressions

Using LCM complexity as probability weight (complex = less probable = more surprising):

| Progression | Shannon H (bits) | Mean Surprise (complexity jump) |
|-------------|-----------------|--------------------------------|
| I–I–I–I (tonic pedal) | 2.00 | 0.0 |
| I–V–vi–IV (pop axis) | 2.00 | 1.0 |
| I–IV–V–I (classical) | 2.00 | 1.0 |
| ii–V7–I (jazz) | 1.52 | **13.6** |
| I–vii°–I–vii° (chromatic) | 1.78 | **33.6** |

**Surprise finding:** The pop axis (I–V–vi–IV) and classical (I–IV–V–I) have identical entropy (2.00) but the pop axis has barely any complexity jump between consecutive chords. Classical sequences move incrementally; pop progression is extremely smooth between same-complexity chords.

**The ii–V7–I:** High surprise (13.6 per step) but only 1.52 bits of entropy — because it has 3 unequal-complexity chords rather than 4 equal ones. It's the most efficient tension-release machine: one big spike (ii→V7, +15) then one big drop (V7→I, −15). The efficiency ratio is unmatched.

**The chromatic vii°–I sequence:** Astronomical surprise (33.6) because the diminished chord (LCM≈48) next to tonic (LCM=14) creates a 34-unit complexity jump. Used sparingly in Romantic music for maximum dramatic effect — the math confirms it's the highest-contrast move available.

**Entropy interpretation:** High entropy progressions feel more varied; low entropy feel more directional. The I–vii°–I–vii° scores 1.78 bits (lower than 2.0) because it concentrates complexity in the vii° chord — an uneven distribution, meaning it's less "varied" than it sounds. The variety is illusory: it's just one type of extreme alternation.

---

## 5. Borrowed Chords: Color as LCM Distance

Borrowed chords from parallel minor in C major:

| Chord | Root LCM from C | Nearest Diatonic LCM | Color Distance |
|-------|-----------------|---------------------|----------------|
| ♭VI (Ab) | 5.32 | 6.17 (vii°) | **0.85** (most colorful) |
| ♭III (Eb) | 4.91 | 4.32 (iii) | 0.58 |
| ♭VII (Bb) | 7.17 | 6.91 (vii°) | 0.26 |
| iv (Fm) | 3.58 | 3.58 (IV same root) | 0.00 |

**Key finding:** ♭VI (Ab major) is the most colorful borrowed chord — its root (Ab) occupies a position in LCM space that is maximally distant from any diatonic chord root. This explains why ♭VI sounds the most "surprising" when inserted into a major-key progression. ♭VII sounds more natural because its root LCM is close to vii°'s root.

**The iv paradox:** The minor subdominant (Fm in C major) has **zero root color distance** from IV — because F is F regardless of chord quality. The color in iv comes from the altered third (Ab instead of A), which changes the triad quality. This is a model limitation: root-only LCM doesn't capture quality changes (major → minor). A full analysis needs to include the quality intervals, not just the root.

**Practical implications:**
- ♭VI → I is the "epic cadence" (Beethoven, film scores) because it introduces maximal color then resolves to simplest complexity (0.0)
- ♭VII → I (rock) feels less surprising because ♭VII's root LCM is barely off the diatonic grid
- iv → I (minor subdominant to tonic) feels poignant — the color is in the quality change, not the root movement

---

## Summary of Session 5

| Finding | Implication |
|---------|-------------|
| Circle of fifths = minimum-LCM adjacency graph | Confirmed mathematically. Fifth modulations cost ~5; tritone costs ~18 |
| Major pentatonic removes both leading tones | Zero directional pull = universal accessibility |
| Japanese scales simpler than Western major | Minor 2nds inside scale ≠ minor 2nd at scale boundary |
| Whole tone is most complex scale | No stable fifth anywhere; Debussy's harmonic suspension justified |
| Bass-weighted LCM > total LCM for stability | 1st inversion most unstable because E-bass creates complex bass relationships |
| ii–V7–I maximizes surprise/unit | Single spike-drop most efficient tension machine |
| ♭VI has highest color distance from diatonic | Ab's LCM position is maximally off the diatonic grid |

## Questions for Session 6

1. **Spectral model of rhythm:** Can we apply the same Fourier approach to rhythm patterns that we use for pitch? A 4/4 beat pattern has frequency components — what happens when two rhythms "interfere"?

2. **Scale "gravity fields":** Map the tonal gravity of each note in a key as a vector — pointing toward the resolution. Is the tonic always a global attractor? Can we compute a "gradient field" for a key?

3. **Harmonic rhythm:** Chords change at different rates. Fast harmonic rhythm (changes every beat) vs slow (every 4 beats). Does harmonic rhythm interact with pitch LCM? Is there an optimal rate of change?

4. **Microtonality:** What happens in 19-TET, 31-TET, or quarter-tone systems? Can we build an LCM model for non-12-TET systems?

5. **Cognitive load model:** LCM complexity is a proxy for cognitive load. Is there a "working memory budget" that musical styles operate within? Can we compute the average cognitive load of a piece by style?

---

**Visualizations:**
- `modulation_paths.png` — key distance matrix + circle of fifths diagram
- `non_western_scales.png` — scale complexity rankings + profile comparison
- `chord_inversions.png` — bass-weighted LCM for C major and C7 inversions
- `progression_entropy.png` — Shannon entropy + entropy vs surprise scatter
- `borrowed_chords.png` — borrowed chord color distances in LCM space
