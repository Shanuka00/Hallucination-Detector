# System Verdict Annotation - Visual Decision Tree

## 🎯 The Question You Always Ask:

```
"Is the system's verdict CORRECT?"
```

---

## 🌳 Decision Tree

```
START: Look at what the SYSTEM said
│
├─ System said "✅ Verified"
│  │
│  ├─ Is this verdict correct?
│  │  │
│  │  ├─ YES, verdict is correct (✓) → TP ✅ System correctly verified
│  │  └─ NO, verdict is wrong (✗)    → FP ❌ System wrongly verified
│  │
│
└─ System said "❌ Risky/Uncertain/Potential Hallucination"
   │
   ├─ Is this verdict correct?
   │  │
   │  ├─ YES, verdict is correct (✓) → TN ✅ System correctly flagged
   │  └─ NO, verdict is wrong (✗)    → FN ❌ System wrongly flagged
```

---

## 📊 The Four Categories Explained

### TP (True Positive) ✅
- **System Said:** "Verified" ✅
- **You Click:** ✓ Correct (verdict is correct)
- **Meaning:** System correctly verified a TRUE claim
- **Example:** Claim: "Paris is in France" (TRUE) → System: "Verified" → You: ✓

### FP (False Positive) ❌
- **System Said:** "Verified" ✅
- **You Click:** ✗ Incorrect (verdict is wrong)
- **Meaning:** System wrongly verified a FALSE claim
- **Example:** Claim: "Moon is cheese" (FALSE) → System: "Verified" → You: ✗

### TN (True Negative) ✅
- **System Said:** "Risky/Uncertain" ❌
- **You Click:** ✓ Correct (verdict is correct)
- **Meaning:** System correctly flagged a FALSE claim
- **Example:** Claim: "Earth is flat" (FALSE) → System: "Risky" → You: ✓

### FN (False Negative) ❌
- **System Said:** "Risky/Uncertain" ❌
- **You Click:** ✗ Incorrect (verdict is wrong)
- **Meaning:** System wrongly rejected a TRUE claim
- **Example:** Claim: "Water is H2O" (TRUE) → System: "Risky" → You: ✗

---

## 🎓 Example Annotation Session

| Claim | TRUE or FALSE? | System Verdict | Is Verdict Correct? | You Click | Category |
|-------|----------------|----------------|---------------------|-----------|----------|
| Paris is in France | TRUE | ✅ Verified | YES (✓) | ✓ Correct | **TP** ✅ |
| Moon is cheese | FALSE | ✅ Verified | NO (✗) | ✗ Wrong | **FP** ❌ |
| Earth orbits Sun | TRUE | ✅ Verified | YES (✓) | ✓ Correct | **TP** ✅ |
| Earth is flat | FALSE | ❌ Risky | YES (✓) | ✓ Correct | **TN** ✅ |
| Water is H2O | TRUE | ❌ Risky | NO (✗) | ✗ Wrong | **FN** ❌ |
| Sun orbits Earth | FALSE | ❌ Risky | YES (✓) | ✓ Correct | **TN** ✅ |

**Results:**
- TP = 2 (Claims 1, 3) - System correctly verified
- FP = 1 (Claim 2) - System wrongly verified
- TN = 2 (Claims 4, 6) - System correctly rejected
- FN = 1 (Claim 5) - System wrongly rejected

**Metrics:**
```
Precision = TP/(TP+FP) = 2/(2+1) = 0.6667
Recall    = TP/(TP+FN) = 2/(2+1) = 0.6667
F1-Score  = 2×P×R/(P+R) = 0.6667
Accuracy  = (TP+TN)/Total = (2+2)/6 = 0.6667
```

---

## 🔑 Key Understanding

### ❌ WRONG Way to Think:
- "Claim is true → Click ✓"
- "Claim is false → Click ✗"

### ✅ CORRECT Way to Think:
- "System verdict is correct → Click ✓"
- "System verdict is wrong → Click ✗"

---

## 🧠 Mental Model

Think of yourself as a **judge evaluating the system's decisions**:

1. **Read the claim**
2. **Determine if claim is TRUE or FALSE** (in your mind)
3. **Look at system's verdict**
4. **Compare:** Did system make the right call?
   - Claim TRUE + System "Verified" = Correct verdict ✓
   - Claim FALSE + System "Verified" = Wrong verdict ✗
   - Claim FALSE + System "Risky" = Correct verdict ✓
   - Claim TRUE + System "Risky" = Wrong verdict ✗
5. **Click accordingly**

---

## 📝 Quick Reference Card

```
╔═══════════════════════════════════════════════════════════╗
║           SYSTEM VERDICT ANNOTATION GUIDE                 ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  System: ✅ Verified     + Verdict Correct ✓  → TP ✅     ║
║  System: ✅ Verified     + Verdict Wrong ✗    → FP ❌     ║
║  System: ❌ Risky/Etc    + Verdict Correct ✓  → TN ✅     ║
║  System: ❌ Risky/Etc    + Verdict Wrong ✗    → FN ❌     ║
║                                                           ║
║  ✓ = System verdict is CORRECT                           ║
║  ✗ = System verdict is WRONG                             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🎯 Common Scenarios

### Scenario 1: System Verifies a True Claim ✅→✓→TP
- Claim: "Python is a programming language" **(TRUE)**
- System: ✅ "Verified"
- System's Decision: **CORRECT** (true claim verified)
- **You Click: ✓ (Correct) → TP** ✅

### Scenario 2: System Verifies a False Claim ✅→✗→FP
- Claim: "JavaScript was invented in 1950" **(FALSE)**
- System: ✅ "Verified"
- System's Decision: **WRONG** (false claim verified)
- **You Click: ✗ (Wrong) → FP** ❌

### Scenario 3: System Flags a False Claim ❌→✓→TN
- Claim: "Humans can breathe underwater naturally" **(FALSE)**
- System: ❌ "Risky Hallucination"
- System's Decision: **CORRECT** (false claim rejected)
- **You Click: ✓ (Correct) → TN** ✅

### Scenario 4: System Flags a True Claim ❌→✗→FN
- Claim: "The Pacific Ocean is the largest ocean" **(TRUE)**
- System: ❌ "Uncertain Claim"
- System's Decision: **WRONG** (true claim rejected)
- **You Click: ✗ (Wrong) → FN** ❌

---

## 🎓 Practice Examples

Try these yourself:

1. Claim: "1+1=2" (TRUE) | System: ✅ Verified | Click: ?
2. Claim: "Moon landing was fake" (FALSE) | System: ✅ Verified | Click: ?
3. Claim: "Earth is round" (TRUE) | System: ❌ Risky | Click: ?
4. Claim: "Vaccines cause autism" (FALSE) | System: ❌ Risky | Click: ?

**Answers:**
1. ✓ Correct → TP (TRUE claim correctly verified)
2. ✗ Wrong → FP (FALSE claim wrongly verified)
3. ✗ Wrong → FN (TRUE claim wrongly rejected)
4. ✓ Correct → TN (FALSE claim correctly rejected)

---

**Remember:** You're evaluating your SYSTEM's performance, not the claims! 🎯
