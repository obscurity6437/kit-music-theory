"""
Session 4: Voice Leading, Tritone Sub, Unified Pitch-Rhythm, LCM Gradient
2026-02-27
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fractions import Fraction
from math import gcd, lcm
import json
from pathlib import Path

OUT = Path(__file__).parent.parent / "visualizations"
OUT.mkdir(exist_ok=True)

# ── Utilities ────────────────────────────────────────────────────────────────

def interval_lcm(freq_ratio):
    f = Fraction(freq_ratio).limit_denominator(64)
    return lcm(f.numerator, f.denominator)

INTERVALS = {
    'Unison':    (1/1,   1),   'Octave':   (2/1,   2),
    'P5':        (3/2,   6),   'P4':       (4/3,  12),
    'M6':        (5/3,  15),   'M3':       (5/4,  20),
    'm3':        (6/5,  30),   'm6':       (8/5,  40),
    'M2':        (9/8,  72),   'm7':       (16/9, 144),
    'M7':        (15/8,120),   'm2':       (16/15,240),
    'Tritone':   (45/32,1440),
}

def chord_lcm(ratios):
    from itertools import combinations
    total = 0
    for a, b in combinations(ratios, 2):
        ratio = max(a,b)/min(a,b)
        total += np.log2(interval_lcm(ratio))
    return total

# ════════════════════════════════════════════════════════════════
# 1. VOICE LEADING AS LCM MINIMIZATION
# ════════════════════════════════════════════════════════════════

def analyze_voice_leading():
    print("=== Voice Leading Analysis ===")
    notes = {
        'C4':1.0,'D4':9/8,'E4':5/4,'F4':4/3,'G4':3/2,'A4':5/3,'B4':15/8,
        'C5':2.0,'D5':9/4,'E5':5/2,'F5':8/3,'G5':3.0,
    }
    
    # SATB: Soprano, Alto, Tenor, Bass
    progression_smooth = [
        ['E5','C5','G4','C4'],  # I
        ['F5','C5','A4','F4'],  # IV
        ['G5','D5','G4','G4'],  # V
        ['E5','C5','G4','C4'],  # I
    ]
    progression_jagged = [
        ['E5','C5','G4','C4'],  # I
        ['A4','F5','C5','F4'],  # IV – soprano drops a 6th
        ['D5','G5','B4','G4'],  # V  – soprano leaps a 7th
        ['E5','C5','G4','C4'],  # I
    ]
    
    voice_names = ['S','A','T','B']
    
    def cost(prog):
        totals = {'S':[],'A':[],'T':[],'B':[]}
        for i in range(len(prog)-1):
            for v,vn in enumerate(voice_names):
                f1 = notes[prog[i][v]]; f2 = notes[prog[i+1][v]]
                ratio = max(f1,f2)/min(f1,f2)
                totals[vn].append(np.log2(interval_lcm(ratio)))
        return totals
    
    smooth_v = cost(progression_smooth)
    jagged_v = cost(progression_jagged)
    smooth_total = sum(sum(v) for v in smooth_v.values())
    jagged_total = sum(sum(v) for v in jagged_v.values())
    
    print(f"Smooth log2-LCM cost: {smooth_total:.2f}")
    print(f"Jagged log2-LCM cost: {jagged_total:.2f}  ({jagged_total/smooth_total:.2f}x)")
    
    fig, axes = plt.subplots(1,2,figsize=(14,6))
    fig.suptitle("Voice Leading as LCM Minimization (I–IV–V–I, SATB)", fontsize=14, fontweight='bold')
    transitions = ['I→IV','IV→V','V→I']
    voice_colors = {'S':'#e74c3c','A':'#e67e22','T':'#27ae60','B':'#2980b9'}
    
    for ax, (voices, title) in zip(axes, [
        (smooth_v, f"Smooth Voice Leading\n(total log₂-LCM: {smooth_total:.1f})"),
        (jagged_v, f"Jagged Voice Leading\n(total log₂-LCM: {jagged_total:.1f}  ·  {jagged_total/smooth_total:.1f}× worse)")
    ]):
        x = np.arange(3); w=0.2
        for i,(vn,col) in enumerate(voice_colors.items()):
            ax.bar(x+i*w, voices[vn], w, label=vn, color=col, alpha=0.85)
        ax.set_title(title, fontsize=11)
        ax.set_xticks(x+1.5*w); ax.set_xticklabels(transitions)
        ax.set_ylabel("log₂(LCM) movement cost"); ax.legend(title="Voice")
        ax.set_ylim(0,9); ax.grid(axis='y',alpha=0.3)
        ax.axhline(np.log2(6),color='green',ls='--',alpha=0.4,label='P5 ref')
    
    plt.tight_layout()
    plt.savefig(OUT/'voice_leading_lcm.png', dpi=150, bbox_inches='tight')
    plt.close(); print("Saved: voice_leading_lcm.png")
    return smooth_total, jagged_total

# ════════════════════════════════════════════════════════════════
# 2. TRITONE SUBSTITUTION
# ════════════════════════════════════════════════════════════════

def analyze_tritone_substitution():
    print("\n=== Tritone Substitution Analysis ===")
    
    dom7 = [1.0, 5/4, 3/2, 16/9]  # Root, M3, P5, m7
    
    C7_ratios  = dom7[:]
    Fs7_root   = 45/32
    Fs7_ratios = [r*Fs7_root for r in dom7]
    Fs7_ratios = [r/2 if r>2 else r for r in Fs7_ratios]
    
    # Voice movement costs to target chord F (4/3, 5/3, 2.0, 4/3)
    C7_moves  = [4/3, 16/15, 9/8, 16/15]   # C→F, E→F, G→A, Bb→A
    Fs7_moves = [16/15,16/15,16/15,16/15]   # all semitone slides
    
    c7_internal  = chord_lcm(C7_ratios)
    fs7_internal = chord_lcm(Fs7_ratios)
    c7_move  = sum(np.log2(interval_lcm(r)) for r in C7_moves)
    fs7_move = sum(np.log2(interval_lcm(r)) for r in Fs7_moves)
    
    print(f"C7 internal complexity:  {c7_internal:.2f}")
    print(f"F#7 internal complexity: {fs7_internal:.2f}")
    print(f"C7→F voice cost:  {c7_move:.2f}")
    print(f"F#7→F voice cost: {fs7_move:.2f}  (all semitones!)")
    print("Key: E-Bb guide tones are SHARED (just inverted)")
    
    fig, axes = plt.subplots(1,3,figsize=(15,6))
    fig.suptitle("Tritone Substitution: Why F#7 Replaces C7\n(Jazz Harmony)", fontsize=14, fontweight='bold')
    
    # Panel 1 – Tritone on circle of fifths
    ax1=axes[0]
    notes12 = ['C','G','D','A','E','B','F#','Db','Ab','Eb','Bb','F']
    angles = np.linspace(0,2*np.pi,12,endpoint=False)-np.pi/2
    xc,yc = np.cos(angles),np.sin(angles)
    ax1.scatter(xc,yc,s=220,c='lightgray',zorder=2)
    for i,(x,y,n) in enumerate(zip(xc,yc,notes12)):
        col='#e74c3c' if n in ('C','F#') else 'black'
        ax1.annotate(n,(x,y),ha='center',va='center',fontsize=12,
                    fontweight='bold' if n in ('C','F#') else 'normal',color=col)
    ax1.plot([xc[0],xc[6]],[yc[0],yc[6]],'r-',lw=3,alpha=0.8,zorder=1)
    ax1.set_xlim(-1.5,1.5); ax1.set_ylim(-1.5,1.5)
    ax1.set_aspect('equal'); ax1.axis('off')
    ax1.set_title("C ↔ F# : Tritone\n(diametrically opposite)", fontsize=11)
    ax1.text(0,-1.35,"Both resolve by semitone\nto same target",ha='center',fontsize=9,style='italic')
    
    # Panel 2 – Shared guide tones
    ax2=axes[1]
    C7_st  = {'C':0,'E':4,'G':7,'Bb':10}
    Fs7_st = {'F#':6,'A#':10,'C#':1,'E':4}  # A#=Bb=10, E=4 are shared
    
    for n,s in C7_st.items():
        col='#e74c3c' if n in ('E','Bb') else '#3498db'
        ax2.barh(s,0.8,left=0.1,color=col,alpha=0.85,height=0.55)
        ax2.text(0.95,s,f"C7: {n}",va='center',fontsize=10,fontweight='bold')
    
    for n,s in Fs7_st.items():
        ds = 10 if n=='A#' else (4 if n=='E' else (1 if n=='C#' else 6))
        col='#e74c3c' if n in ('A#','E') else '#e67e22'
        ax2.barh(ds+0.08,0.8,left=1.3,color=col,alpha=0.85,height=0.55)
        ax2.text(2.15,ds+0.08,f"F#7: {n}",va='center',fontsize=10,fontweight='bold')
    
    ax2.plot([0.9,1.3],[4,4],'r--',lw=2,alpha=0.85)
    ax2.plot([0.9,1.3],[10,10.08],'r--',lw=2,alpha=0.85)
    ax2.text(1.1,7,"Shared\nguide\ntones!",ha='center',fontsize=11,color='red',fontweight='bold')
    ax2.set_xlim(0,3); ax2.set_ylim(-1,13)
    ax2.set_yticks([0,4,6,7,10]); ax2.set_yticklabels(['C','E','F#','G','Bb'],fontsize=9)
    ax2.set_xticks([]); ax2.grid(axis='y',alpha=0.3)
    ax2.set_title("Shared Guide Tones (E & Bb)\nare the 'resolution desire'", fontsize=11)
    
    # Panel 3 – Complexity comparison
    ax3=axes[2]
    cats = ['Internal\ncomplexity','Avg voice\nmovement\nlog₂(LCM)']
    c7v  = [c7_internal, c7_move/4]
    fs7v = [fs7_internal, fs7_move/4]
    x=np.arange(2); w=0.3
    ax3.bar(x-w/2,c7v,w,label='C7 (original)',color='#3498db',alpha=0.85)
    ax3.bar(x+w/2,fs7v,w,label='F#7 (tritone sub)',color='#e67e22',alpha=0.85)
    ax3.set_xticks(x); ax3.set_xticklabels(cats,fontsize=10)
    ax3.set_ylabel("log₂(LCM)"); ax3.legend(); ax3.grid(axis='y',alpha=0.3)
    ax3.set_title("C7 vs F#7 Complexity", fontsize=11)
    ax3.text(0.5,0.07,"Both share E-Bb guide tones.\nF#7 resolves with pure semitone slides.\nSub trades harmonic distance for voice smoothness.",
             transform=ax3.transAxes,ha='center',fontsize=9,style='italic',
             bbox=dict(boxstyle='round',facecolor='wheat',alpha=0.6))
    
    plt.tight_layout()
    plt.savefig(OUT/'tritone_substitution.png', dpi=150, bbox_inches='tight')
    plt.close(); print("Saved: tritone_substitution.png")

# ════════════════════════════════════════════════════════════════
# 3. UNIFIED PITCH-RHYTHM 2D MODEL
# ════════════════════════════════════════════════════════════════

def analyze_unified_model():
    print("\n=== Unified Pitch-Rhythm 2D Model ===")
    
    pitch_lcms = {'Octave':2,'Fifth':6,'Fourth':12,'Maj 3rd':20,'Min 3rd':30,
                  'Maj 2nd':72,'Min 2nd':240,'Tritone':1440}
    rhythm_lcms = {'1:1':1,'2:1':2,'3:2':6,'4:3':12,'5:4':20,'5:3':15,'7:4':28,'7:5':35,'7:6':42}
    
    p_log = np.array([np.log2(v) for v in pitch_lcms.values()])
    r_log = np.array([np.log2(v) for v in rhythm_lcms.values()])
    grid = np.outer(p_log, r_log)
    grid /= grid.max()
    
    fig, axes = plt.subplots(1,2,figsize=(16,7))
    fig.suptitle("Unified Pitch-Rhythm Complexity: 2D LCM Space", fontsize=14, fontweight='bold')
    
    im = axes[0].imshow(grid, cmap='YlOrRd', aspect='auto', interpolation='nearest')
    axes[0].set_xticks(range(len(rhythm_lcms)))
    axes[0].set_xticklabels(list(rhythm_lcms.keys()), rotation=40, ha='right', fontsize=9)
    axes[0].set_yticks(range(len(pitch_lcms)))
    axes[0].set_yticklabels(list(pitch_lcms.keys()), fontsize=10)
    axes[0].set_title("Pitch × Rhythm Complexity Matrix\n(brighter = more complex)", fontsize=11)
    plt.colorbar(im, ax=axes[0], label='Normalized complexity')
    
    # Star special cells
    for (py,px,label) in [(0,0,'Octave+1:1\n(simplest)'),(1,2,'Fifth+3:2\n(swing)'),(7,7,'Tritone+7:5\n(max chaos)')]:
        axes[0].scatter(px,py,s=200,marker='*',c='white',zorder=5,edgecolors='black')
    
    # Scatter: musical styles
    ax2=axes[1]
    contexts = {
        'Bach Chorale':      (np.log2(6),   np.log2(2)),
        'Jazz Swing':        (np.log2(20),  np.log2(6)),
        'Stravinsky':        (np.log2(12),  np.log2(12)),
        'Messiaen':          (np.log2(30),  np.log2(35)),
        'Pop/Folk':          (np.log2(6),   np.log2(1)),
        'Bebop chromatic':   (np.log2(240), np.log2(6)),
        'Minimalism':        (np.log2(2),   np.log2(7)),
        'Death metal riff':  (np.log2(1440),np.log2(1)),
    }
    colors = plt.cm.plasma(np.linspace(0.1,0.9,len(contexts)))
    for (name,(px,py)),col in zip(contexts.items(),colors):
        ax2.scatter(px,py,s=280,color=col,zorder=5,edgecolors='black',lw=1.5)
        ax2.annotate(name,(px,py),xytext=(px+0.15,py+0.15),fontsize=9)
    ax2.set_xlabel("Pitch LCM complexity log₂",fontsize=11)
    ax2.set_ylabel("Rhythm LCM complexity log₂",fontsize=11)
    ax2.set_title("Musical Styles in 2D Complexity Space",fontsize=11)
    ax2.grid(alpha=0.3)
    ax2.axvline(3,color='gray',ls='--',alpha=0.4); ax2.axhline(2.5,color='gray',ls='--',alpha=0.4)
    ax2.text(0.5,5.5,"Simple pitch\nComplex rhythm\n(Minimalism)",ha='center',fontsize=8,alpha=0.5,style='italic')
    ax2.text(7,0.3,"Complex pitch\nSimple rhythm\n(Tone clusters)",ha='center',fontsize=8,alpha=0.5,style='italic')
    
    plt.tight_layout()
    plt.savefig(OUT/'unified_pitch_rhythm.png', dpi=150, bbox_inches='tight')
    plt.close(); print("Saved: unified_pitch_rhythm.png")

# ════════════════════════════════════════════════════════════════
# 4. TENSION GRADIENT — EMOTIONAL ARC
# ════════════════════════════════════════════════════════════════

def analyze_tension_gradient():
    print("\n=== LCM Gradient / Emotional Arc Analysis ===")
    
    # Approximate chord complexity as sum of log2-LCM of pairwise intervals
    # Major triad = 20+6+30 -> log2 sum ~14.4; V7 adds tritone inside
    chord_cx = {
        'I':   np.log2(20)+np.log2(6)+np.log2(30),
        'ii':  np.log2(30)+np.log2(20)+np.log2(6)+2.0,
        'iii': np.log2(30)+np.log2(20)+np.log2(6)+1.5,
        'IV':  np.log2(20)+np.log2(6)+np.log2(30),
        'V':   np.log2(20)+np.log2(6)+np.log2(30)+1.5,
        'V7':  np.log2(20)+np.log2(6)+np.log2(1440)/2+4.0,
        'vi':  np.log2(30)+np.log2(20)+np.log2(6)+0.5,
        'vii°':np.log2(30)+np.log2(1440)/3+np.log2(1440)/3+6.0,
    }
    
    progressions = [
        ('I-V-vi-IV (pop)',     ['I','V','vi','IV','I']),
        ('I-IV-V-I (classical)',['I','IV','V','I']),
        ('I-vi-IV-V (doo-wop)', ['I','vi','IV','V','I']),
        ('ii-V7-I (jazz)',      ['ii','V7','I']),
    ]
    
    fig, axes = plt.subplots(2,2,figsize=(14,10))
    fig.suptitle("Emotional Arc as LCM Gradient\n(Red=tension ↑ · Green=resolution ↓)", fontsize=14, fontweight='bold')
    axes_flat = axes.flatten()
    
    for ax,(name,chords) in zip(axes_flat,progressions):
        cx = [chord_cx[c] for c in chords]
        grads = np.diff(cx)
        x = np.arange(len(chords))
        
        ax2=ax.twinx()
        ax.fill_between(x,cx,alpha=0.12,color='#3498db')
        ax.plot(x,cx,'b-o',lw=2,zorder=5)
        ax.set_ylabel("Complexity (log₂-LCM sum)",color='blue',fontsize=9)
        ax.tick_params(axis='y',colors='blue')
        
        gx = np.arange(len(grads))+0.5
        gcols=['#e74c3c' if g>0 else '#27ae60' for g in grads]
        ax2.bar(gx,grads,color=gcols,alpha=0.6,width=0.8)
        ax2.axhline(0,color='gray',ls='--',alpha=0.4)
        ax2.set_ylabel("Δ Complexity (tension gradient)",color='gray',fontsize=9)
        ax2.tick_params(axis='y',colors='gray')
        
        ax.set_xticks(x); ax.set_xticklabels(chords,fontsize=10,fontweight='bold')
        ax.set_title(name,fontsize=11); ax.grid(axis='y',alpha=0.2)
        
        print(f"\n{name}:")
        for c1,c2,g in zip(chords,chords[1:],grads):
            print(f"  {c1}→{c2}: {g:+.1f}  ({'↑ tension' if g>0 else '↓ resolve'})")
    
    plt.tight_layout()
    plt.savefig(OUT/'tension_gradient.png', dpi=150, bbox_inches='tight')
    plt.close(); print("\nSaved: tension_gradient.png")

# ════════════════════════════════════════════════════════════════
# 5. MODAL COMPLEXITY PROFILES
# ════════════════════════════════════════════════════════════════

def analyze_modal_complexity():
    print("\n=== Modal Complexity Profiles ===")
    
    semi_to_ji = {
        0:(1,1), 1:(16,15), 2:(9,8),   3:(6,5),
        4:(5,4), 5:(4,3),   6:(45,32),  7:(3,2),
        8:(8,5), 9:(5,3),   10:(16,9),  11:(15,8), 12:(2,1),
    }
    
    modes = {
        'Ionian (Major)':  [0,2,4,5,7,9,11,12],
        'Dorian':          [0,2,3,5,7,9,10,12],
        'Phrygian':        [0,1,3,5,7,8,10,12],
        'Lydian':          [0,2,4,6,7,9,11,12],
        'Mixolydian':      [0,2,4,5,7,9,10,12],
        'Aeolian (Minor)': [0,2,3,5,7,8,10,12],
        'Locrian':         [0,1,3,5,6,8,10,12],
    }
    mode_chars = {
        'Ionian (Major)':  'bright, stable',
        'Dorian':          'minor but hopeful',
        'Phrygian':        'dark, flamenco',
        'Lydian':          'dreamy, floating',
        'Mixolydian':      'bluesy, rock',
        'Aeolian (Minor)': 'melancholic',
        'Locrian':         'unstable, tense',
    }
    
    def deg_cx(semis):
        return [np.log2(lcm(semi_to_ji[s][0],semi_to_ji[s][1])) for s in semis]
    
    fig,ax=plt.subplots(figsize=(13,7))
    colors=plt.cm.rainbow(np.linspace(0,1,7))
    degree_names=['1','2','3','4','5','6','7','8']
    
    for (mn,semis),col in zip(modes.items(),colors):
        cx=deg_cx(semis)
        ax.plot(np.arange(8),cx,'-o',color=col,lw=2,
                label=f"{mn}  —  {mode_chars[mn]}",alpha=0.85,ms=6)
    
    # Annotate Locrian tritone at degree 5 (index 4)
    loc_cx=deg_cx(modes['Locrian'])
    ax.annotate("Locrian dim.5th\n(tritone! LCM=1440)",
                xy=(4,loc_cx[4]),xytext=(5.5,9.8),
                arrowprops=dict(arrowstyle='->',color='red',lw=1.5),
                fontsize=9,color='red',ha='center')
    
    ax.set_xticks(range(8)); ax.set_xticklabels(degree_names,fontsize=11)
    ax.set_xlabel("Scale Degree",fontsize=12)
    ax.set_ylabel("LCM complexity vs root (log₂)",fontsize=12)
    ax.set_title("Modal Complexity Profiles: 7 Church Modes\n(higher = more tension from root)",fontsize=13)
    ax.legend(loc='upper left',fontsize=9,framealpha=0.9)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT/'modal_complexity.png', dpi=150, bbox_inches='tight')
    plt.close(); print("Saved: modal_complexity.png")
    
    print("\nMode mean complexity (ascending = 'brighter'):")
    ranked=sorted([(mn,np.mean(deg_cx(s))) for mn,s in modes.items()],key=lambda x:x[1])
    for mn,m in ranked:
        print(f"  {mn}: {m:.2f}")

# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

if __name__=='__main__':
    print("Music Theory Session 4 — Advanced Analysis")
    print("="*55)
    analyze_voice_leading()
    analyze_tritone_substitution()
    analyze_unified_model()
    analyze_tension_gradient()
    analyze_modal_complexity()
    print("\n"+"="*55)
    print("All visualizations saved. Session 4 complete.")
