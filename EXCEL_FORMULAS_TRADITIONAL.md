# ✅ UPDATED Excel Formulas - Traditional Binary Classification

## 📊 **System Now Uses Traditional Binary Classification**

The system has been updated to use **traditional binary classification** where:
- You annotate whether the **CLAIM is factually correct** (ground truth)
- System compares ground truth vs system verdict
- You get **different values** for Precision, Recall, F1-Score, Accuracy

---

## 🎯 **What You Annotate**

**Question:** "Is this CLAIM factually correct?"

- ✓ **Correct** = Claim is TRUE (factually accurate)
- ✗ **Incorrect** = Claim is FALSE (hallucination/wrong)

**NOT:** "Is the system verdict correct?" ❌

---

## 📋 **Updated Excel Formulas**

### **For Regular Rows (Q1 = Row 2):**

```excel
Column H (Precision):  =IF(D2+E2=0, 0, D2/(D2+E2))
Column I (Recall):     =IF(D2+G2=0, 0, D2/(D2+G2))
Column J (F1-Score):   =IF(H2+I2=0, 0, 2*H2*I2/(H2+I2))
Column K (Accuracy):   =IF(D2+E2+F2+G2=0, 0, (D2+F2)/(D2+E2+F2+G2))
```

### **For TOTAL Row (Row 52):**

```excel
Column C (Total Claims): =SUM(C2:C51)
Column D (Total TP):     =SUM(D2:D51)
Column E (Total FP):     =SUM(E2:E51)
Column F (Total TN):     =SUM(F2:F51)
Column G (Total FN):     =SUM(G2:G51)

Column H (Precision):  =IF(D52+E52=0, 0, D52/(D52+E52))
Column I (Recall):     =IF(D52+G52=0, 0, D52/(D52+G52))
Column J (F1-Score):   =IF(H52+I52=0, 0, 2*H52*I52/(H52+I52))
Column K (Accuracy):   =IF(D52+E52+F52+G52=0, 0, (D52+F52)/(D52+E52+F52+G52))
```

---

## 🔍 **How to Count TP, FP, TN, FN**

After annotating each claim in the browser, count manually:

### **Decision Table:**

| System Verdict | Your Annotation (Ground Truth) | Category | Count As |
|----------------|-------------------------------|----------|----------|
| ✅ **Verified** | ✓ **Correct** (claim is true) | **TP** | True Positive |
| ✅ **Verified** | ✗ **Incorrect** (claim is false) | **FP** | False Positive |
| ❌ **Risky/Uncertain** | ✗ **Incorrect** (claim is false) | **TN** | True Negative |
| ❌ **Risky/Uncertain** | ✓ **Correct** (claim is true) | **FN** | False Negative |

---

## 📊 **Example Calculation**

### **Scenario: 7 Claims**

| Claim | System Verdict | Your Annotation | Category |
|-------|----------------|-----------------|----------|
| "Paris is in France" | ✅ Verified | ✓ Correct | **TP** |
| "London is in UK" | ✅ Verified | ✓ Correct | **TP** |
| "Rome is in Italy" | ✅ Verified | ✓ Correct | **TP** |
| "Berlin is in France" | ✅ Verified | ✗ Incorrect | **FP** |
| "Madrid is in Spain" | ✅ Verified | ✓ Correct | **TP** |
| "Earth is flat" | ❌ Risky | ✗ Incorrect | **TN** |
| "Sky is blue" | ❌ Uncertain | ✓ Correct | **FN** |

**Count:**
- TP = 4
- FP = 1
- TN = 1
- FN = 1

**Enter in Excel:**
```
D2: 4
E2: 1
F2: 1
G2: 1
```

**Excel Calculates (DIFFERENT VALUES!):**
```
Precision = 4/(4+1) = 0.8000
Recall    = 4/(4+1) = 0.8000
F1-Score  = 2*0.8*0.8/(0.8+0.8) = 0.8000
Accuracy  = (4+1)/(4+1+1+1) = 0.7143
```

**System Shows (Should Match!):**
```
Precision: 0.8000
Recall: 0.8000
F1-Score: 0.8000
Accuracy: 0.7143
```

---

## ✅ **Formula Explanation**

| Metric | Formula | What It Measures |
|--------|---------|------------------|
| **Precision** | `TP/(TP+FP)` | Of claims system verified, how many were actually true? |
| **Recall** | `TP/(TP+FN)` | Of all true claims, how many did system verify? |
| **F1-Score** | `2×(P×R)/(P+R)` | Harmonic mean of Precision and Recall |
| **Accuracy** | `(TP+TN)/(TP+FP+TN+FN)` | Overall correctness rate |

---

## 🎯 **Key Differences from Simplified System**

### **Before (Simplified):**
- All metrics = same value (e.g., 0.3846)
- TN and FN always 0
- Only measuring: "How often is system verdict correct?"

### **Now (Traditional):**
- Metrics have different values (e.g., P=0.80, R=0.80, Acc=0.71)
- All TP/FP/TN/FN are used
- Measuring: "How well does system classify claims as true/false?"

---

## 📁 **Updated Template File**

Use: **`evaluation_template_traditional.csv`** (I'll create this next)

Or manually update your existing sheets with the formulas above.

---

## 🚀 **Quick Copy-Paste**

### **Row 2 (Q1):**
```
H2: =IF(D2+E2=0,0,D2/(D2+E2))
I2: =IF(D2+G2=0,0,D2/(D2+G2))
J2: =IF(H2+I2=0,0,2*H2*I2/(H2+I2))
K2: =IF(D2+E2+F2+G2=0,0,(D2+F2)/(D2+E2+F2+G2))
```

### **Row 52 (TOTAL):**
```
D52: =SUM(D2:D51)
E52: =SUM(E2:E51)
F52: =SUM(F2:F51)
G52: =SUM(G2:G51)
H52: =IF(D52+E52=0,0,D52/(D52+E52))
I52: =IF(D52+G52=0,0,D52/(D52+G52))
J52: =IF(H52+I52=0,0,2*H52*I52/(H52+I52))
K52: =IF(D52+E52+F52+G52=0,0,(D52+F52)/(D52+E52+F52+G52))
```

---

**Now your metrics will match academic standards!** 📊✅
