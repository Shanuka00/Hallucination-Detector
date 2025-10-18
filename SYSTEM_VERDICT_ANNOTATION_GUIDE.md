# System Verdict Annotation Guide

## ✅ CORRECT Implementation - Annotate System Verdicts!

This guide explains how to properly annotate your hallucination detection system's performance using the **System Verdict Evaluation** method.

---

## 🎯 Key Principle

**Annotate the System Verdict, NOT the Claim**

You are evaluating: **"Did my hallucination detection system make the right decision?"**

---

## 📊 The Confusion Matrix Logic

| System Says | You Annotate | Category | Meaning |
|-------------|--------------|----------|---------|
| ✅ **Verified** | ✓ **Correct** | **TP (True Positive)** | System correctly identified claim as verified ✅ |
| ✅ **Verified** | ✗ **Incorrect** | **FP (False Positive)** | System wrongly verified a risky claim ❌ |
| ❌ **Risky/Uncertain** | ✗ **Incorrect** | **TN (True Negative)** | System correctly flagged risky claim ✅ |
| ❌ **Risky/Uncertain** | ✓ **Correct** | **FN (False Negative)** | System wrongly rejected a verified claim ❌ |

---

## 📋 How to Annotate (Step-by-Step)

### For Each Claim:

1. **Look at the "Final Verdict" column**
   - Is it "Verified" (✅) or "Risky/Uncertain/Potential Hallucination" (❌)?

2. **Ask yourself: "Is this verdict correct?"**
   - Should this claim be verified? Or should it be flagged as risky?

3. **Click the appropriate button:**
   - ✓ **Correct** = System made the right decision
   - ✗ **Incorrect** = System made the wrong decision

---

## 📚 Annotation Examples

### Example 1: True Positive (TP)

**Claim:** "Paris is the capital of France"  
**System Verdict:** ✅ Verified  
**Your Judgment:** This is factually correct, system should verify it  
**Click:** ✓ Correct  
**Result:** TP = System correctly verified a true claim ✅

---

### Example 2: False Positive (FP)

**Claim:** "London is the capital of Germany"  
**System Verdict:** ✅ Verified  
**Your Judgment:** This is FALSE! System should have flagged it as risky  
**Click:** ✗ Incorrect  
**Result:** FP = System wrongly verified a false claim ❌

---

### Example 3: True Negative (TN)

**Claim:** "The Earth is flat"  
**System Verdict:** ❌ Risky Hallucination  
**Your Judgment:** Correct! This is false and should be flagged  
**Click:** ✗ Incorrect (meaning the claim is incorrect, so verdict is correct)  
**Result:** TN = System correctly flagged a false claim ✅

**⚠️ IMPORTANT:** When system says "Risky" and the claim IS risky, click ✗ (Incorrect claim) = TN

---

### Example 4: False Negative (FN)

**Claim:** "The sky is blue"  
**System Verdict:** ❌ Risky Hallucination  
**Your Judgment:** This is TRUE! System should have verified it  
**Click:** ✓ Correct  
**Result:** FN = System wrongly rejected a true claim ❌

---

## 🔢 Understanding the Metrics

After annotating all claims, the system calculates:

### **Precision**
```
Precision = TP / (TP + FP)
```
**Meaning:** Of all claims the system VERIFIED, what percentage were actually correct?

**Example:** System verified 10 claims, 8 were correct → Precision = 8/10 = 0.8000 (80%)

---

### **Recall**
```
Recall = TP / (TP + FN)
```
**Meaning:** Of all claims that SHOULD be verified, what percentage did the system catch?

**Example:** 12 claims should be verified, system caught 8 → Recall = 8/12 = 0.6667 (67%)

---

### **F1-Score**
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```
**Meaning:** Balanced measure of precision and recall

**Example:** P=0.8000, R=0.6667 → F1 = 2 × (0.8 × 0.667) / (0.8 + 0.667) = 0.7273

---

### **Accuracy**
```
Accuracy = (TP + TN) / Total
```
**Meaning:** Overall percentage of correct system decisions

**Example:** 8 TP + 10 TN out of 20 total → Accuracy = 18/20 = 0.9000 (90%)

---

## 🎓 TruthfulQA Integration

When using TruthfulQA dataset:

### Reference Materials:
- **Best Answer** column (most accurate answer)
- **Correct Answers** column (all acceptable answers)
- **Incorrect Answers** column (common misconceptions)

### Annotation Process:

1. **Read the extracted claim**
2. **Compare with TruthfulQA answers**
3. **Determine if claim is factually correct**
4. **Check system verdict**
5. **Annotate:** Did system make the right decision?

### Example:

**TruthfulQA Question:** "What is the capital of France?"  
**Correct Answer:** "Paris"  
**Incorrect Answer:** "London"

**Extracted Claim:** "Paris is the capital of France"  
**System Verdict:** ✅ Verified  
**Your Annotation:** ✓ Correct → TP

**Extracted Claim:** "London is the capital of France"  
**System Verdict:** ✅ Verified  
**Your Annotation:** ✗ Incorrect → FP

---

## 🧪 Example Annotation Session

Let's annotate 6 claims:

| # | Claim | System Verdict | Is Claim True? | Is Verdict Correct? | Annotate | Category |
|---|-------|----------------|----------------|---------------------|----------|----------|
| 1 | Paris is in France | ✅ Verified | YES | ✅ YES | ✓ | TP |
| 2 | Moon is cheese | ✅ Verified | NO | ❌ NO | ✗ | FP |
| 3 | Earth orbits Sun | ✅ Verified | YES | ✅ YES | ✓ | TP |
| 4 | Earth is flat | ❌ Risky | NO | ✅ YES | ✗* | TN |
| 5 | Water is H2O | ❌ Risky | YES | ❌ NO | ✓ | FN |
| 6 | Sun orbits Earth | ❌ Risky | NO | ✅ YES | ✗* | TN |

**\*Note:** When system says "Risky" and claim IS risky → Click ✗ (claim is incorrect) = TN

### Results:
- **TP** = 2 (Claims 1, 3)
- **FP** = 1 (Claim 2)
- **TN** = 2 (Claims 4, 6)
- **FN** = 1 (Claim 5)
- **Total** = 6

### Metrics:
```
Precision = 2/(2+1) = 0.6667 (67%)
Recall    = 2/(2+1) = 0.6667 (67%)
F1-Score  = 0.6667
Accuracy  = (2+2)/6 = 0.6667 (67%)
```

**All different values!** ✅

---

## ⚠️ Common Mistakes to Avoid

### ❌ WRONG: Annotating the Claim

**DON'T:** "This claim is true → Click ✓"  
**DON'T:** "This claim is false → Click ✗"

### ✅ CORRECT: Annotating the System Verdict

**DO:** "System said 'Verified' and claim is true → Click ✓ (TP)"  
**DO:** "System said 'Verified' but claim is false → Click ✗ (FP)"  
**DO:** "System said 'Risky' and claim is false → Click ✗ (TN)"  
**DO:** "System said 'Risky' but claim is true → Click ✓ (FN)"

---

## 🎯 Decision Tree for Annotation

```
START: Look at System Verdict
│
├─ System says "Verified" ✅
│  │
│  ├─ Is claim actually correct? YES → Click ✓ (TP) ✅
│  └─ Is claim actually correct? NO  → Click ✗ (FP) ❌
│
└─ System says "Risky/Uncertain" ❌
   │
   ├─ Is claim actually correct? YES → Click ✓ (FN) ❌
   └─ Is claim actually correct? NO  → Click ✗ (TN) ✅
```

---

## 📊 Google Sheets Formula Reference

When tracking manually in Google Sheets:

### Columns:
- A: Claim ID
- B: Claim Text
- C: System Verdict
- D: Your Annotation (Correct/Incorrect)

### Calculate Confusion Matrix:

```excel
TP: =COUNTIFS(C:C,"Verified",D:D,"Correct")
FP: =COUNTIFS(C:C,"Verified",D:D,"Incorrect")
TN: =COUNTIFS(C:C,"Risky*",D:D,"Incorrect")
FN: =COUNTIFS(C:C,"Risky*",D:D,"Correct")
```

### Calculate Metrics:

```excel
Precision: =TP/(TP+FP)
Recall:    =TP/(TP+FN)
F1-Score:  =2*(Precision*Recall)/(Precision+Recall)
Accuracy:  =(TP+TN)/(TP+FP+TN+FN)
```

---

## ✅ Quality Checks

### Before Calculating Metrics:

1. ✓ All claims annotated (no empty cells)
2. ✓ System verdicts correctly recorded
3. ✓ Annotations based on verdict correctness, not claim truth

### After Calculating Metrics:

1. ✓ TP + FP + TN + FN = Total Claims
2. ✓ All metrics between 0.0000 and 1.0000
3. ✓ Different values for P/R/F1/Accuracy (usually)
4. ✓ If Precision = Recall, check annotations are correct

### Sanity Check Example:

If ALL annotations are ✓ (Correct):
- TP + FN = Total (no FP, no TN)
- Precision = TP / TP = 1.0000 ❌ **This is wrong!**
- Should have some FP or TN unless system is perfect

---

## 🚀 Start Annotating!

1. **Run analysis** on a TruthfulQA question
2. **Review each claim** and system verdict
3. **Click ✓ or ✗** based on verdict correctness
4. **Calculate metrics**
5. **Verify** all four TP/FP/TN/FN values are populated

---

## 📞 Need Help?

**Quick Reference:**
- System ✅ + You ✓ = **TP** (Good!)
- System ✅ + You ✗ = **FP** (Bad - wrong verification)
- System ❌ + You ✗ = **TN** (Good!)
- System ❌ + You ✓ = **FN** (Bad - missed verification)

**Remember:** You're evaluating your SYSTEM's performance, not the claims themselves!

---

**Good luck with your evaluation! 🎉**
