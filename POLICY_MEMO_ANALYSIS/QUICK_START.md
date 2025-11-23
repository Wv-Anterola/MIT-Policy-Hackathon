# Quick Start Guide - Policy Memo Analysis

## 🚀 Quick Commands

### Run the Analysis
```powershell
cd "C:\Users\Wilber Anterola\Desktop\Brown\MIT-Hackathon\NLP"
& ".\.venv\Scripts\python.exe" POLICY_MEMO_ANALYSIS\scripts\verify_policy_memo_data.py
```

### View Results
```powershell
# Open the comprehensive report
notepad POLICY_MEMO_ANALYSIS\data\latest_run\COMPREHENSIVE_MEMO_STATISTICS.txt

# Open the CSV summary
start POLICY_MEMO_ANALYSIS\data\latest_run\KEY_STATISTICS_SUMMARY.csv
```

## 📊 Key Statistics Reference

### For Executive Summary:
- **Total bills analyzed**: 7,938
- **Low protection states**: 56%
- **High protection states**: 18%
- **State-to-federal ratio**: 111:1

### For State Consensus Section:
- **Digital Literacy Education**: 62%
- **Data Privacy Standards**: 58%
- **Transparency & Reporting**: 56%
- **Platform Liability**: 51%
- **Age Verification**: 38%

### For Federal Inaction:
- **State bills passed**: 334
- **Federal bills passed**: 3
- **2025 bills introduced**: 2,461

### For Evidence Gaps:
- **Bills lacking evidence**: 76.9%

## 📁 Where to Find What

| Need | Location |
|------|----------|
| All statistics | `data/latest_run/COMPREHENSIVE_MEMO_STATISTICS.txt` |
| Quick numbers | `data/latest_run/KEY_STATISTICS_SUMMARY.csv` |
| State rankings | `data/latest_run/state_protection_scores.csv` |
| Consensus data | `data/latest_run/state_consensus_provisions.csv` |
| Charts | `visualizations/*.png` |
| Analysis script | `scripts/verify_policy_memo_data.py` |

## 🔄 Workflow

1. **Modify analysis** → Edit `scripts/verify_policy_memo_data.py`
2. **Run script** → Execute the quick command above
3. **Review results** → Check `data/latest_run/` folder
4. **Update memo** → Edit LaTeX document with new numbers
5. **Compile LaTeX** → Generate final PDF

## 💡 Tips

- The script creates timestamped folders, but `latest_run` always has the most recent
- All visualizations are high-res (300 DPI) for publication quality
- CSV files can be opened in Excel for easy viewing
- The comprehensive report includes full methodology for citations

## ⚠️ Important Notes

- **Always use passed, children-related bills only** ✅
- The script automatically filters the data correctly
- All numbers are reproducible from the source CSVs
- Methodology is fully documented in the comprehensive report

---

**Quick Help**: If you need to re-run the analysis with different parameters, edit the `PolicyMemoDataVerification` class in the script.
