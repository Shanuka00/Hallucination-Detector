# ✅ CORRECTED Excel Formulas for Simplified Annotation System

## 🔍 The Issue

**Your system uses simplified verdict correctness:**
- You annotate whether the SYSTEM VERDICT is correct
- ✓ = System verdict is CORRECT
- ✗ = System verdict is WRONG

**In this model:**
- TP = Number of correct verdicts (✓)
- FP = Number of wrong verdicts (✗)
- TN = 0 (not used)
- FN = 0 (not used)

**Therefore, ALL metrics are the same:**
- Accuracy = Precision = Recall = F1-Score = **TP / (TP + FP)**

---

## ✅ CORRECT Formulas

### For Regular Rows (Q1 = Row 2):

```excel
Column H (Precision):  =IF(D2+E2=0, 0, D2/(D2+E2))
Column I (Recall):     =IF(D2+E2=0, 0, D2/(D2+E2))
Column J (F1-Score):   =IF(D2+E2=0, 0, D2/(D2+E2))
Column K (Accuracy):   =IF(D2+E2=0, 0, D2/(D2+E2))
```

**All four formulas are IDENTICAL!**

### For TOTAL Row (Row 52):

```excel
Column C (Total Claims): =SUM(C2:C51)
Column D (Total TP):     =SUM(D2:D51)
Column E (Total FP):     =SUM(E2:E51)
Column F (Total TN):     =SUM(F2:F51)
Column G (Total FN):     =SUM(G2:G51)

Column H (Precision):  =IF(D52+E52=0, 0, D52/(D52+E52))
Column I (Recall):     =IF(D52+E52=0, 0, D52/(D52+E52))
Column J (F1-Score):   =IF(D52+E52=0, 0, D52/(D52+E52))
Column K (Accuracy):   =IF(D52+E52=0, 0, D52/(D52+E52))
```

---

## 📊 Verification Example

**Your test case:**
- Total Claims: 7
- TP: 5 (marked as ✓ correct)
- FP: 2 (marked as ✗ wrong)
- TN: 0
- FN: 0

**System calculates:**
```
Precision = Recall = F1 = Accuracy = 5/7 = 0.7143
```

**Excel with CORRECT formulas:**
```
H2: =D2/(D2+E2) = 5/(5+2) = 0.7143 ✅
I2: =D2/(D2+E2) = 5/(5+2) = 0.7143 ✅
J2: =D2/(D2+E2) = 5/(5+2) = 0.7143 ✅
K2: =D2/(D2+E2) = 5/(5+2) = 0.7143 ✅
```

**All match! ✅**

---

## ❌ Old WRONG Formulas (For Reference)

These were based on traditional classification metrics:

```excel
❌ Precision: =IF(E2+F2=0,0,E2/(E2+F2))  [Used column E, F]
❌ Recall:    =IF(E2+H2=0,0,E2/(E2+H2))  [Used column E, H - WRONG!]
❌ F1-Score:  =IF(I2+J2=0,0,2*I2*J2/(I2+J2))  [Calculated from wrong values]
❌ Accuracy:  =IF(E2+F2+G2+H2=0,0,(E2+G2)/(E2+F2+G2+H2))  [Used all 4 columns]
```

**These gave wrong results:**
- Recall = 5/(5+0) = 1.0000 ❌ (Should be 0.7143)
- F1 = 0.8333 ❌ (Should be 0.7143)

---

## 📁 Updated Files

1. **`evaluation_template_corrected.csv`** - Use this one! (All 50 rows corrected)
2. **`evaluation_template.csv`** - Old version with wrong formulas (ignore)

---

## 🚀 How to Use

### Option 1: Import New Template

1. Delete old template imports
2. Import `evaluation_template_corrected.csv` to each model sheet
3. Start entering data

### Option 2: Fix Existing Sheets

If you already started entering data:

1. **For each row (2-51), change formulas to:**
   ```excel
   H column: =IF(D[row]+E[row]=0,0,D[row]/(D[row]+E[row]))
   I column: =IF(D[row]+E[row]=0,0,D[row]/(D[row]+E[row]))
   J column: =IF(D[row]+E[row]=0,0,D[row]/(D[row]+E[row]))
   K column: =IF(D[row]+E[row]=0,0,D[row]/(D[row]+E[row]))
   ```

2. **For TOTAL row (52):**
   ```excel
   H52: =IF(D52+E52=0,0,D52/(D52+E52))
   I52: =IF(D52+E52=0,0,D52/(D52+E52))
   J52: =IF(D52+E52=0,0,D52/(D52+E52))
   K52: =IF(D52+E52=0,0,D52/(D52+E52))
   ```

---

## 💡 Why This is Correct

**Your annotation system:**
- Simple binary outcome: System verdict correct or wrong
- No distinction between different types of errors
- Just measuring overall accuracy

**Traditional classification (what old formulas assumed):**
- Distinguishes between False Positives and False Negatives
- Precision: Avoid false alarms
- Recall: Don't miss true positives
- Different denominators → Different values

**Your simplified system → All metrics collapse to same formula!**

---

## ✅ Final Check

After entering your example data (TP=5, FP=2):

**All four cells (H, I, J, K) should show: 0.7143**

If they do → ✅ Formulas are correct!
If they don't → ❌ Wrong template imported

---

**Use `evaluation_template_corrected.csv` for all your Google Sheets!** 📊
