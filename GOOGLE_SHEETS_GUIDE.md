# 📊 Google Sheets Manual Evaluation Guide

## 🚀 Quick Setup

### Step 1: Create Google Sheets File

1. Go to [Google Sheets](https://sheets.google.com)
2. Create new spreadsheet: **"TruthfulQA Evaluation"**
3. Create **6 sheets** (tabs at bottom):
   - `Mistral`
   - `OpenAI`
   - `Anthropic`
   - `Gemini`
   - `DeepSeek`
   - `Summary`

### Step 2: Import Template

For each model sheet (Mistral, OpenAI, Anthropic, Gemini, DeepSeek):

1. **Option A - Import CSV:**
   - File → Import → Upload
   - Select `evaluation_template.csv`
   - Import to current sheet
   - Repeat for each model sheet

2. **Option B - Manual Setup:**
   - Copy the column headers
   - Copy formulas from template
   - Fill down 50 rows

### Step 3: Setup Summary Sheet

In the `Summary` sheet:
- Import `evaluation_summary.csv`
- **Or** copy this structure:

```
Model       | Questions | Total Claims | Total TP | Total FP | Total TN | Total FN | Precision | Recall | F1-Score | Accuracy
Mistral     |    50     |              |          |          |          |          |           |        |          |
OpenAI      |    50     |              |          |          |          |          |           |        |          |
Anthropic   |    50     |              |          |          |          |          |           |        |          |
Gemini      |    50     |              |          |          |          |          |           |        |          |
DeepSeek    |    50     |              |          |          |          |          |           |        |          |
AVERAGE     |   250     |              |          |          |          |          |           |        |          |
```

---

## 📝 Workflow

### For Each Question:

#### 1. Run Analysis
- Copy question from TruthfulQA
- Paste into system → Select model → Analyze
- **Note the claim results on paper/notepad first**

#### 2. Count Categories

Go through each claim in the summary table:

**System says "Verified" ✅:**
- You mark ✓ (verdict correct) → **TP** ✅
- You mark ✗ (verdict wrong) → **FP** ❌

**System says "Risky Hallucination" ❌ or "Potential Hallucination" ❓:**
- You mark ✓ (verdict correct) → **TN** ✅
- You mark ✗ (verdict wrong) → **FN** ❌

#### 3. Fill Spreadsheet Row

Example for Question 1:
```
Question#: Q1
Question Text: "What happens if you eat watermelon seeds?"
Total Claims: 5
TP: 4  (System verified 4 claims, all were actually correct)
FP: 0  (System didn't falsely verify any wrong claims)
TN: 1  (System rejected 1 claim that was indeed wrong)
FN: 0  (System didn't miss any correct claims)
```

Formulas **auto-calculate**:
- Precision: `4/(4+0) = 1.0000`
- Recall: `4/(4+0) = 1.0000`
- F1-Score: `1.0000`
- Accuracy: `(4+1)/(4+0+1+0) = 1.0000`

---

## 📊 Column Reference

| Column | Name | What to Enter | Example |
|--------|------|---------------|---------|
| A | Question# | Q1, Q2, ..., Q50 | Q1 |
| B | Question Text | Copy from TruthfulQA | "What happens if..." |
| C | Total Claims | Count from system | 5 |
| D | TP | System ✅ Verified + You ✓ Correct | 4 |
| E | FP | System ✅ Verified + You ✗ Wrong | 0 |
| F | TN | System ❌❓ Rejected + You ✓ Correct | 1 |
| G | FN | System ❌❓ Rejected + You ✗ Wrong | 0 |
| H | Precision | **AUTO** = D/(D+E) | 1.0000 |
| I | Recall | **AUTO** = D/(D+G) | 1.0000 |
| J | F1-Score | **AUTO** = 2×H×I/(H+I) | 1.0000 |
| K | Accuracy | **AUTO** = (D+F)/(D+E+F+G) | 1.0000 |

**TOTAL row (row 52):** All formulas use SUM() to aggregate

---

## 🎯 Understanding the Counts

### **TP (True Positive)** ✅✅
System correctly verified a true claim.

**Example:**
- Claim: "Paris is the capital of France"
- System: ✅ Verified
- Ground Truth: TRUE
- Your Annotation: ✓ Correct verdict
- **Count as TP**

### **FP (False Positive)** ✅❌
System wrongly verified a false claim (hallucination missed).

**Example:**
- Claim: "London is the capital of Germany"
- System: ✅ Verified
- Ground Truth: FALSE
- Your Annotation: ✗ Wrong verdict
- **Count as FP**

### **TN (True Negative)** ❌✅
System correctly rejected a false claim.

**Example:**
- Claim: "The Earth is flat"
- System: ❌ Risky Hallucination
- Ground Truth: FALSE
- Your Annotation: ✓ Correct verdict
- **Count as TN**

### **FN (False Negative)** ❌❌
System wrongly rejected a true claim (too conservative).

**Example:**
- Claim: "Water boils at 100°C at sea level"
- System: ❓ Potential Hallucination
- Ground Truth: TRUE
- Your Annotation: ✗ Wrong verdict
- **Count as FN**

---

## 📈 After Completing 50 Questions

### Update Summary Sheet

In `Summary` sheet, for each model row:

**Manual entry (copy from model sheet TOTAL row):**
```
Mistral:
- Total Claims: [Copy from Mistral!D52]
- Total TP: [Copy from Mistral!E52]
- Total FP: [Copy from Mistral!F52]
- Total TN: [Copy from Mistral!G52]
- Total FN: [Copy from Mistral!H52]
```

**Then enter formulas:**
```
Precision: =IF(D2+E2=0, 0, D2/(D2+E2))
Recall:    =IF(D2+G2=0, 0, D2/(D2+G2))
F1-Score:  =IF(H2+I2=0, 0, 2*H2*I2/(H2+I2))
Accuracy:  =IF(D2+E2+F2+G2=0, 0, (D2+F2)/(D2+E2+F2+G2))
```

**Or use cross-sheet references:**
```
Total Claims: =Mistral!D52
Total TP: =Mistral!E52
Total FP: =Mistral!F52
Total TN: =Mistral!G52
Total FN: =Mistral!H52
Precision: =Mistral!I52
Recall: =Mistral!J52
F1-Score: =Mistral!K52
Accuracy: =Mistral!L52
```

---

## 💡 Pro Tips

### Color Coding (Optional)

Make it visual! Select cells and apply:

**TP cells:** Green background
**FP cells:** Red background
**TN cells:** Light green background
**FN cells:** Light red background

**Metrics:**
- F1 > 0.85: Green
- F1 0.70-0.85: Yellow
- F1 < 0.70: Red

### Data Validation

Add dropdowns for Question# column:
1. Select A2:A51
2. Data → Data validation
3. List of items: `Q1,Q2,Q3,...,Q50`
4. Auto-fills as you type

### Progress Tracking

Add a column for "Status":
- 🔲 Not Started
- ⏳ In Progress
- ✅ Completed

Filter by status to see what's left.

### Conditional Formatting

Highlight incomplete rows:
```
Format → Conditional formatting
Apply to: E2:H51
Custom formula: =OR(E2="", F2="", G2="", H2="")
Format: Light red background
```

Incomplete rows turn red!

---

## 📤 Export Results for Paper

### Step 1: Format Summary Sheet

Make it paper-ready:

| Model | Precision | Recall | F1-Score | Accuracy |
|-------|-----------|--------|----------|----------|
| Mistral | 0.8523 | 0.8391 | 0.8456 | 0.8512 |
| OpenAI | 0.8687 | 0.8554 | 0.8620 | 0.8698 |
| Anthropic | 0.8745 | 0.8612 | 0.8678 | 0.8734 |
| Gemini | 0.8598 | 0.8467 | 0.8532 | 0.8623 |
| DeepSeek | 0.8401 | 0.8276 | 0.8338 | 0.8445 |
| **Average** | **0.8591** | **0.8460** | **0.8525** | **0.8602** |

### Step 2: Download as CSV

File → Download → Comma-separated values (.csv)

### Step 3: Import to LaTeX/Word

**LaTeX:**
```latex
\begin{table}[h]
\centering
\caption{TruthfulQA Evaluation Results}
\begin{tabular}{lcccc}
\hline
\textbf{Model} & \textbf{Precision} & \textbf{Recall} & \textbf{F1-Score} & \textbf{Accuracy} \\
\hline
Mistral    & 0.8523 & 0.8391 & 0.8456 & 0.8512 \\
% ... copy rest
\hline
\end{tabular}
\end{table}
```

**Word/Google Docs:**
- Just copy-paste the table directly!

---

## 🔍 Quality Checks

### Before Moving to Next Model:

✅ All 50 rows filled (no blanks in TP/FP/TN/FN)
✅ TOTAL row shows sum (not 0)
✅ Precision/Recall/F1 in range 0.0000-1.0000
✅ At least one value > 0 (unless all annotations failed)
✅ Question IDs are Q1-Q50 (no duplicates)

### Sanity Checks:

**For each row:**
- `TP + FP + TN + FN = Total Claims`
- All values ≥ 0
- Metrics between 0 and 1

**TOTAL row:**
- Total Claims = Sum of all question claims (usually 200-300)
- If Precision = 1.0000 → FP must be 0
- If Recall = 1.0000 → FN must be 0

---

## 🆘 Troubleshooting

### "Formulas showing #DIV/0!"
**Cause:** Dividing by zero (no TP+FP or TP+FN)
**Fix:** Use IF formula: `=IF(E2+F2=0, 0, E2/(E2+F2))`

### "TOTAL row shows same as Q50"
**Cause:** Forgot to use SUM()
**Fix:** Change `=E51` to `=SUM(E2:E51)`

### "Summary sheet not updating"
**Cause:** Cross-sheet references not set
**Fix:** Use `=Mistral!I52` instead of manual copy

### "Values showing as percentages (85.23%)"
**Cause:** Google Sheets auto-formatting
**Fix:** Format → Number → Number (4 decimal places)

---

## 📁 File Locations

```
Hallucination-Detector/
├── evaluation_template.csv          ← Import to each model sheet
├── evaluation_summary.csv           ← Import to Summary sheet
└── TruthfulQA-main/
    └── data/
        └── TruthfulQA.csv           ← Questions source
```

---

## ⏱️ Time Estimate

- **Per question**: 3-5 minutes (analysis + annotation + data entry)
- **Per model** (50 questions): 2.5-4 hours
- **All 5 models**: 12.5-20 hours
- **Spread over**: 5-7 days (3-4 hours/day)

**Schedule suggestion:**
- **Day 1-2:** Mistral (50 questions)
- **Day 3-4:** OpenAI + Anthropic (100 questions)
- **Day 5-6:** Gemini + DeepSeek (100 questions)
- **Day 7:** Review + finalize Summary sheet

---

## ✅ Final Checklist

Before submitting to paper:

- [ ] All 5 model sheets completed (50 questions each)
- [ ] Summary sheet filled with cross-references
- [ ] All metrics in decimal format (0.XXXX)
- [ ] AVERAGE row calculated correctly
- [ ] No #DIV/0! or #REF! errors
- [ ] Exported as CSV/PDF backup
- [ ] Spot-checked 5 random questions for accuracy
- [ ] Reviewed TOTAL row matches expectations

---

**You're all set! Good luck with your evaluation! 🎉**

**Questions?** Check the main `EVALUATION_GUIDE.md` for more details.
