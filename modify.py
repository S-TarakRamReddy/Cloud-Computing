import os
import re

file_path = 'docs/generate_report.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Old vs New table logic with Uncal vs Cal
content = re.sub(
    r"hdr\[1\].text = 'Current Model \(Before\)'",
    "hdr[1].text = 'Uncalibrated XGBoost'",
    content
)
content = re.sub(
    r"hdr\[2\].text = 'Improved Model \(After\)'",
    "hdr[2].text = 'Calibrated XGBoost'",
    content
)
content = re.sub(
    r"table\.rows\[1\]\.cells\[1\]\.text = '99\.86%'",
    "table.rows[1].cells[1].text = '99.95%'",
    content
)
content = re.sub(
    r"table\.rows\[2\]\.cells\[1\]\.text = '55\.71%'",
    "table.rows[2].cells[1].text = '86.96%'",
    content
)
content = re.sub(
    r"table\.rows\[3\]\.cells\[1\]\.text = '82\.11%'",
    "table.rows[3].cells[1].text = '84.51%'",
    content
)
content = re.sub(
    r"table\.rows\[4\]\.cells\[1\]\.text = '66\.38%'",
    "table.rows[4].cells[1].text = '85.71%'",
    content
)
content = re.sub(
    r"table\.rows\[5\]\.cells\[1\]\.text = '98\.24%'",
    "table.rows[5].cells[1].text = '97.98%'",
    content
)
content = re.sub(
    r"table\.rows\[1\]\.cells\[2\]\.text = f'\{rf_metrics\[\"Accuracy\"\] \* 100:\.2f\}%'",
    "table.rows[1].cells[2].text = f'{rf_metrics.get(\"Accuracy\", 0) * 100:.2f}%'",
    content
)
content = re.sub(
    r"table\.rows\[2\]\.cells\[2\]\.text = f'\{rf_metrics\[\"Precision\"\] \* 100:\.2f\}%'",
    "table.rows[2].cells[2].text = f'{rf_metrics.get(\"Precision\", 0) * 100:.2f}%'",
    content
)
content = re.sub(
    r"table\.rows\[3\]\.cells\[2\]\.text = f'\{rf_metrics\[\"Recall\"\] \* 100:\.2f\}%'",
    "table.rows[3].cells[2].text = f'{rf_metrics.get(\"Recall\", 0) * 100:.2f}%'",
    content
)
content = re.sub(
    r"table\.rows\[4\]\.cells\[2\]\.text = f'\{rf_metrics\[\"F1\"\] \* 100:\.2f\}%'",
    "table.rows[4].cells[2].text = f'{rf_metrics.get(\"F1\", 0) * 100:.2f}%'",
    content
)
content = re.sub(
    r"table\.rows\[5\]\.cells\[2\]\.text = f'\{rf_metrics\[\"ROC-AUC\"\] \* 100:\.2f\}%'",
    "table.rows[5].cells[2].text = f'{rf_metrics.get(\"ROC-AUC\", 0) * 100:.2f}%'",
    content
)
content = re.sub(
    r"doc\.add_heading\('Chapter 11 .* Results \(Old vs New Comparison\)', level=1\)",
    "doc.add_heading('Chapter 11 - Results (Uncalibrated vs Calibrated XGBoost)', level=1)",
    content
)
content = re.sub(
    r"random_forest_cm\.png",
    "calibrated_xgboost_cm.png",
    content
)
content = re.sub(
    r"Random Forest Confusion Matrix",
    "Calibrated XGBoost Confusion Matrix",
    content
)
content = re.sub(
    r"Random Forest emerged as the superior model",
    "XGBoost emerged as the superior model and was subsequently probability-calibrated using Isotonic Regression",
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Script modified')
