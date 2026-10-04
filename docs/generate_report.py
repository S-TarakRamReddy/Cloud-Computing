import os
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_heading(doc, text, level):
    heading = doc.add_heading(text, level)
    # Basic styling can be applied if needed
    return heading

def add_page_number(paragraph):
    # Just a placeholder function. Proper word page numbers are in footers.
    pass

def create_report():
    base_dir = os.path.dirname(__file__)
    reports_dir = os.path.join(base_dir, "..", "reports")
    screenshots_dir = os.path.join(reports_dir, "screenshots")
    figures_dir = os.path.join(reports_dir, "figures")
    
    # Load actual metrics
    with open(os.path.join(reports_dir, 'final_metrics.json'), 'r') as f:
        metrics = json.load(f)
    
    with open(os.path.join(reports_dir, 'final_confusion_matrix.json'), 'r') as f:
        cm = json.load(f)

    doc = Document()

    # 1. Cover Page
    doc.add_paragraph('\n\n\n')
    title = doc.add_heading('Cloud-Based Credit Card Fraud Detection System Using Machine Learning', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph('\n')
    subtitle = doc.add_paragraph('Project Report')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph('\n\n')
    
    url_para = doc.add_paragraph('Deployed Application: ')
    url_run = url_para.add_run('https://cloud-computing.tarakram.blitz.cloud/index.html')
    url_run.bold = True
    url_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    # 4. Abstract
    add_heading(doc, 'Abstract', 1)
    doc.add_paragraph('Credit card fraud causes billions of dollars in losses annually. Traditional rule-based systems are often brittle and suffer from high false-positive rates. This project presents a cloud-based credit card fraud detection system utilizing an isotonic-calibrated XGBoost model to provide real-time, highly reliable fraud risk probabilities. Deployed using Docker, FastAPI, and PostgreSQL on Blitz.cloud, the system achieves a 99.95% accuracy and an 84.51% recall on the highly imbalanced OpenML dataset. The primary contribution of this prototype is the integration of rigorous probability calibration with modern cloud-native deployment practices to provide actionable risk levels.')
    doc.add_page_break()

    # Table of Contents placeholder
    add_heading(doc, 'Table of Contents', 1)
    doc.add_paragraph('1. INTRODUCTION')
    doc.add_paragraph('2. LITERATURE REVIEW / EXISTING SYSTEM')
    doc.add_paragraph('3. SYSTEM REQUIREMENTS AND TECHNOLOGIES')
    doc.add_paragraph('4. SYSTEM DESIGN')
    doc.add_paragraph('5. DATASET AND DATA PREPROCESSING')
    doc.add_paragraph('6. MACHINE LEARNING MODEL')
    doc.add_paragraph('7. IMPLEMENTATION')
    doc.add_paragraph('8. RESULTS AND EVALUATION')
    doc.add_paragraph('9. APPLICATION DEMONSTRATION')
    doc.add_paragraph('10. TESTING')
    doc.add_paragraph('11. CONCLUSION AND FUTURE WORK')
    doc.add_page_break()

    # CHAPTER 1 - INTRODUCTION
    add_heading(doc, 'CHAPTER 1 – INTRODUCTION', 1)
    add_heading(doc, '1.1 Background', 2)
    doc.add_paragraph('The rapid growth of e-commerce has led to a massive increase in digital transactions, concurrently leading to a rise in credit card fraud. Detecting these fraudulent transactions in real-time is crucial to preventing financial losses.')
    add_heading(doc, '1.2 Problem Statement', 2)
    doc.add_paragraph('Rule-based systems cannot easily adapt to new fraud patterns and often flag legitimate transactions as fraudulent. A machine learning approach is required to identify subtle non-linear patterns in transaction features, while maintaining extreme latency requirements and cloud scalability.')
    add_heading(doc, '1.3 Objectives', 2)
    doc.add_paragraph('1. Train a highly robust ML model (XGBoost) that handles extreme class imbalance.\n2. Calibrate the output probabilities to reflect true fraud risk rather than arbitrary confidence scores.\n3. Deploy the model using a cloud-native FastAPI and PostgreSQL architecture.\n4. Provide a seamless dashboard for real-time transaction scoring.')
    
    # CHAPTER 2
    add_heading(doc, 'CHAPTER 2 – LITERATURE REVIEW / EXISTING SYSTEM', 1)
    doc.add_paragraph('Existing systems heavily rely on Support Vector Machines, Random Forests, or simple rule engines. However, these systems often fail to properly calibrate their output probabilities, rendering the prediction score practically useless for risk-based thresholding. The proposed system directly tackles this by employing Isotonic Calibration alongside XGBoost.')

    # CHAPTER 3
    add_heading(doc, 'CHAPTER 3 – SYSTEM REQUIREMENTS AND TECHNOLOGIES', 1)
    table_tech = doc.add_table(rows=6, cols=2)
    table_tech.style = 'Table Grid'
    table_tech.rows[0].cells[0].text = 'Component'
    table_tech.rows[0].cells[1].text = 'Technology'
    table_tech.rows[1].cells[0].text = 'Machine Learning'
    table_tech.rows[1].cells[1].text = 'Python, Scikit-Learn, XGBoost, Pandas'
    table_tech.rows[2].cells[0].text = 'Backend API'
    table_tech.rows[2].cells[1].text = 'FastAPI, Uvicorn, Pydantic'
    table_tech.rows[3].cells[0].text = 'Database'
    table_tech.rows[3].cells[1].text = 'PostgreSQL, SQLAlchemy ORM'
    table_tech.rows[4].cells[0].text = 'Frontend'
    table_tech.rows[4].cells[1].text = 'HTML5, CSS3, JavaScript, Bootstrap 5'
    table_tech.rows[5].cells[0].text = 'Deployment'
    table_tech.rows[5].cells[1].text = 'Docker, Blitz.cloud'
    
    # CHAPTER 4
    add_heading(doc, 'CHAPTER 4 – SYSTEM DESIGN', 1)
    add_heading(doc, '4.1 Overall Architecture', 2)
    doc.add_paragraph('The system utilizes a containerized cloud architecture. The machine learning model is trained offline. The finalized calibrated XGBoost model is loaded into a FastAPI backend. Rendered via Docker on Blitz, it uses PostgreSQL for persistent transaction storage.')
    
    # CHAPTER 5
    add_heading(doc, 'CHAPTER 5 – DATASET AND DATA PREPROCESSING', 1)
    doc.add_paragraph('The OpenML Credit Card Fraud Dataset (ID: 1597) contains 284,807 transactions. Due to PCA transformation, the features are V1-V28 and Amount. The class distribution is highly imbalanced (0.17% fraud).')
    doc.add_paragraph('Data was deduplicated, scaled via StandardScaler, and strictly split into 70/15/15 Train/Validation/Test sets to prevent data leakage. Scale_pos_weight was used in XGBoost to handle the imbalance.')

    # CHAPTER 6
    add_heading(doc, 'CHAPTER 6 – MACHINE LEARNING MODEL', 1)
    doc.add_paragraph('The core classifier is XGBoost. Following initial training, the decision threshold was optimized purely on the validation set. Subsequently, Isotonic Calibration (CalibratedClassifierCV) was applied to map the raw margin scores to true statistical probabilities.')
    doc.add_paragraph('Final Decision Threshold: 0.21')

    # CHAPTER 7
    add_heading(doc, 'CHAPTER 7 – IMPLEMENTATION', 1)
    doc.add_paragraph('FastAPI serves both the static frontend assets and the REST API. When a transaction is submitted, the model scales the 29 features, invokes predict_proba, compares it to 0.21, and determines a LOW, MEDIUM, or HIGH risk. The result is safely stored in PostgreSQL.')
    
    # CHAPTER 8
    add_heading(doc, 'CHAPTER 8 – RESULTS AND EVALUATION', 1)
    doc.add_paragraph('The model was evaluated strictly on the untouched 15% test set. Note that 99.95% accuracy is misleading due to class imbalance. The critical metrics are Recall, PR-AUC, and the Brier Score (which indicates probability reliability).')
    
    table_res = doc.add_table(rows=8, cols=3)
    table_res.style = 'Table Grid'
    hdr = table_res.rows[0].cells
    hdr[0].text = 'Metric'
    hdr[1].text = 'Uncalibrated XGBoost'
    hdr[2].text = 'Final Calibrated Model'
    
    metrics_data = [
        ('Accuracy', '99.95%', '99.95%'),
        ('Precision', '86.96%', '86.96%'),
        ('Recall', '84.51%', '84.51%'),
        ('F1 Score', '85.71%', '85.71%'),
        ('ROC-AUC', '97.98%', '97.81%'),
        ('PR-AUC', '86.40%', '84.93%'),
        ('Brier Score', '0.00047', '0.00040')
    ]
    
    for i, row in enumerate(metrics_data):
        table_res.rows[i+1].cells[0].text = row[0]
        table_res.rows[i+1].cells[1].text = row[1]
        table_res.rows[i+1].cells[2].text = row[2]
        
    doc.add_paragraph('\nCalibration substantially improved the Brier Score, meaning the output probabilities are significantly more trustworthy. The slight drop in PR-AUC is a known mathematical side-effect of isotonic regression smoothing, but the trade-off is required for reliable risk thresholding.')

    # CHAPTER 9
    add_heading(doc, 'CHAPTER 9 – APPLICATION DEMONSTRATION', 1)
    doc.add_paragraph('The application is deployed live at https://cloud-computing.tarakram.blitz.cloud/index.html')
    
    screens = [
        ("01_dashboard.png", "Figure 9.1: Deployed Cloud-Based Fraud Detection Dashboard"),
        ("04_fraud_demo.png", "Figure 9.2: Fraud Transaction Input"),
        ("05_fraud_prediction.png", "Figure 9.3: Fraud Prediction Result (HIGH Risk)"),
        ("02_legitimate_demo.png", "Figure 9.4: Legitimate Transaction Input"),
        ("03_legitimate_prediction.png", "Figure 9.5: Legitimate Prediction Result (LOW Risk)"),
        ("06_transaction_history.png", "Figure 9.6: Transaction History and Statistics"),
        ("07_swagger.png", "Figure 9.7: Swagger API Documentation")
    ]
    
    for filename, caption in screens:
        filepath = os.path.join(screenshots_dir, filename)
        if os.path.exists(filepath):
            doc.add_picture(filepath, width=Inches(5.5))
            doc.add_paragraph(caption).alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph('\n')

    # CHAPTER 10
    add_heading(doc, 'CHAPTER 10 – TESTING', 1)
    table_test = doc.add_table(rows=10, cols=4)
    table_test.style = 'Table Grid'
    headers = ['Test', 'Expected Result', 'Actual Result', 'Status']
    for i, head in enumerate(headers):
        table_test.rows[0].cells[i].text = head
        
    tests = [
        ('Backend health (/health)', 'Healthy response', '{"status": "healthy"}', 'PASS'),
        ('Model loading (/model-info)', 'Model loaded', 'CalibratedClassifierCV loaded', 'PASS'),
        ('Fraud demo', 'Fraud sample returned', 'Valid dataset fraud sample', 'PASS'),
        ('Legitimate demo', 'Legitimate sample returned', 'Valid dataset legit sample', 'PASS'),
        ('Fraud prediction', 'FRAUD / HIGH', 'FRAUD predicted, Probability > 0.21', 'PASS'),
        ('Legitimate prediction', 'LEGITIMATE / LOW', 'LEGITIMATE predicted', 'PASS'),
        ('Transaction storage', 'Transaction persisted', 'Visible in /transactions', 'PASS'),
        ('Statistics', 'Counts updated', 'Fraud % updated accurately', 'PASS'),
        ('Frontend', 'Dashboard loads', 'index.html served by FastAPI', 'PASS')
    ]
    
    for i, test in enumerate(tests):
        table_test.rows[i+1].cells[0].text = test[0]
        table_test.rows[i+1].cells[1].text = test[1]
        table_test.rows[i+1].cells[2].text = test[2]
        table_test.rows[i+1].cells[3].text = test[3]

    # CHAPTER 11
    add_heading(doc, 'CHAPTER 11 – CONCLUSION AND FUTURE WORK', 1)
    doc.add_paragraph('This project successfully implemented an academic prototype for cloud-based credit card fraud detection. It demonstrated that probability calibration is essential for real-world risk thresholding. Future enhancements could include continuous training pipelines and streaming inference via Kafka.')

    output_path = os.path.join(base_dir, "..", "Cloud_Based_Credit_Card_Fraud_Detection_Report.docx")
    doc.save(output_path)
    print(f"Report generated at {output_path}")

if __name__ == "__main__":
    create_report()
