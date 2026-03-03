# Voice Leading, Tritone Substitution, Modal Complexity, and the Emotional Arc

_2026-03-02 — Session 4 findings_

## Overview

Session 3 left four open questions. Session 4 answers all of them with models and one jazz surprise.

1. Voice leading as LCM minimization?
2. Why does tritone substitution (F#7 for C7) actually work?
3. A unified pitch-rhythm 2D complexity model
4. Chord progressions as emotional arcs (LCM gradient = tension/resolution)

Plus: modal complexity profiles — why Locrian is maximally tense.

---

## 1. Voice Leading as LCM Minimization

### Result

Two versions of I–IV–V–I in SATB:
- Smooth total log₂-LCM: **56.65**
- Jagged total log₂-LCM: **58.65** (only 1.04× worse)

The quantitative difference is small (3.5%), but the musical difference is large. This means:

**Voice leading is not primarily aggregate LCM minimization.** It's per-voice constraint: a single large leap disrupts even if other voices compensate. A better model uses **minimax** (minimize the maximum voice movement cost), not the sum.

The real constraint is also singability: a soprano leaping a major seventh (LCM=120) is hard to sing in tune regardless of the bass. Voice leading rules are per-voice LCM minimization plus vocal range/memory constraints. The math points in the right direction but doesn't fully explain the strictness of the rules.

---

## 2. Tritone Substitution: The Jazz Secret

C7 and F#7 share their guide tones (3rd and 7th) — just swapped:
- C7: 3rd=E, 7th=Bb
- F#7: 3rd=A#(=Bb), 7th=E

This is the only other dominant 7th in the universe with identical guide tones. The tritone relationship between C and F# ensures exact guide tone sharing — it is not coincidental. Every dominant 7th chord has exactly one mirror at the tritone interval.

F#7 also resolves to any target by pure semitone slides (all four voices move half a step). C7 resolves by a fourth in the bass; F#7 resolves by a half-step in the bass. The trade: give up the authoritative V→I bass leap, gain smooth chromatic voice movement and jazz color.

**F#7 complexity (38.23) is slightly lower than C7 (40.23)** — both are dominant 7ths, same internal intervals, different roots. The tritone relationship between the two chords is external; it doesn't add internal complexity.

---

## 3. Unified Pitch-Rhythm 2D Complexity Space

Pitch complexity (x) × Rhythm complexity (y) forms a 2D space where musical styles occupy distinct regions:

| Style | Pitch LCM | Rhythm LCM | Character |
|-------|-----------|------------|-----------|
| Pop/Folk | Low (P5, M3) | Low (2:1) | Mass accessible |
| Bach Chorale | Medium | Low | Harmonic richness, rhythmic regularity |
| Jazz Swing | High (7ths) | Medium (triplets) | Both axes medium-high |
| Messiaen | High | High | Maximally demanding |
| Minimalism | Low | High | Rhythm budget, pitch restraint |
| Death metal | High (tritone) | Low | Pitch dissonance, rhythmic grid |

**Key insight:** Genres are dimensional contracts — stylistic agreements about which axis to explore. When genres violate their contract (prog rock adding rich harmony to simple rock rhythms), they become sub-genres.

---

## 4. Emotional Arc as LCM Gradient

Tension = current chord complexity. Resolution = drop in complexity. The gradient (Δ per chord change) tells you if music is building or releasing.

**ii–V7–I (jazz):**
- ii→V7: +2.3 (sharp build — V7 contains tritone)
- V7→I: **−4.3** (massive release)

The ii–V7–I maximizes tension-release gradient. It's the most efficient tension machine in Western harmony because V7's internal tritone spikes complexity, then I's clean triad releases it fully.

**I–V–vi–IV (pop):**
IV→I gradient = 0 (same complexity). The pop progression never fully resolves — both IV and I are simple major triads. It *feels* resolved through learned familiarity, not LCM structure. **Learned expectation can override mathematical complexity.**

---

## 5. Modal Complexity Profiles

Modes ranked by mean log₂-LCM complexity from root:
- Ionian: 3.56 | Mixolydian: 3.59 | Dorian: 3.67
- Aeolian: 3.84 | Phrygian: 4.06 | Lydian: 4.42 | **Locrian: 5.05**

**Locrian has a tritone between root and 5th.** No stable foundation. The most fundamental structural interval — root to fifth — is the most dissonant interval. No piece can stay in Locrian because the tonic itself generates maximum tension.

**Lydian ranked more complex than Phrygian** — but Phrygian feels darker. Resolution: complexity near the root feels darker than complexity high in the scale. The minor 2nd in Phrygian (LCM=240) grinds against the root; Lydian's tritone (LCM=1440) is far up the scale and floats rather than grates. **Refinement needed: weight lower scale degrees more heavily.**

---

## Questions for Session 5

1. **Modulation as path in key-space:** Is the circle of fifths the minimum-LCM adjacency graph? What's the most efficient modulation between any two keys?
2. **Non-Western scales:** Pentatonic (removes 4th and 7th) — does removing high-complexity degrees explain its universal appeal? Arabic maqam, Indian raga?
3. **Chord inversions:** Does bass note change effective LCM? Root position vs first inversion measured from the bass note up?
4. **Entropy of progressions:** Using LCM as a "surprise" metric, can we compute information entropy of a progression?
5. **Borrowed chords:** Does a ♭VII chord's LCM profile from the key center explain the "color" quality?

---

## New Visualizations

- `voice_leading_lcm.png` — smooth vs jagged SATB, per-voice LCM costs
- `tritone_substitution.png` — guide tone sharing, circle of fifths, complexity comparison
- `unified_pitch_rhythm.png` — 2D complexity matrix + musical styles scatter
- `tension_gradient.png` — four progressions with tension arcs and gradients
- `modal_complexity.png` — seven modes, complexity profiles, Locrian annotation
