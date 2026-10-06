import os
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_heading(doc, text, level=1):
    h = doc.add_heading(text, level)
    for run in h.runs: run.font.name = 'Arial'
    return h

def add_p(doc, text, bold=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.bold = bold
    return p

def add_image(doc, filepath, caption, width_inches=5.5):
    if os.path.exists(filepath):
        doc.add_picture(filepath, width=Inches(width_inches))
        p = doc.add_paragraph(caption)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.italic = True
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
    else:
        print(f"Warning: Image {filepath} not found.")

def create_table(doc, headers, rows_data):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        for paragraph in hdr_cells[i].paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.name = 'Times New Roman'
    for row_data in rows_data:
        row_cells = table.add_row().cells
        for i, val in enumerate(row_data):
            row_cells[i].text = str(val)
            for paragraph in row_cells[i].paragraphs:
                for run in paragraph.runs: run.font.name = 'Times New Roman'
    doc.add_paragraph("\n")

def generate():
    base_dir = os.path.dirname(__file__)
    reports_dir = os.path.join(base_dir, "..", "reports")
    screenshots = os.path.join(reports_dir, "screenshots")
    figures = os.path.join(reports_dir, "figures")

    doc = Document()
    
    # PRELIMINARY PAGES
    for _ in range(5): doc.add_paragraph()
    doc.add_heading("Cloud-Based Credit Card Fraud Detection System Using Machine Learning\n", 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("\nA B.Tech Project Report\n\nSubmitted by:\nS. Tarak Ram Reddy (24WU0102051)\nS. Srinivasa Reddy (24WU0102052)\nM. Puneeth Reddy (24WU0102047)\nZunaira Khan (24WU0102020)\nPragnya D (24WU0102058)\n\nSupervised by:\nDr. M. Upendra Kumar\n\nWoxsen University\n2024-2028").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    add_heading(doc, "CERTIFICATE", 1)
    add_p(doc, "This is to certify that the project report entitled 'Cloud-Based Credit Card Fraud Detection System Using Machine Learning' is a bona fide record of work carried out by S. Tarak Ram Reddy, S. Srinivasa Reddy, M. Puneeth Reddy, Zunaira Khan, and Pragnya D under my supervision. The report fulfills the requirements for the degree of Bachelor of Technology.")
    doc.add_paragraph("\n\n_______________________\nDr. M. Upendra Kumar\nSupervisor").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    doc.add_page_break()
    
    add_heading(doc, "DECLARATION", 1)
    add_p(doc, "We hereby declare that the work presented in this report entitled 'Cloud-Based Credit Card Fraud Detection System Using Machine Learning' is our own original work. Where information has been derived from other sources, we confirm that this has been indicated in the report. This work has not been submitted previously for any other degree or diploma.")
    doc.add_paragraph("\n\nS. Tarak Ram Reddy\nS. Srinivasa Reddy\nM. Puneeth Reddy\nZunaira Khan\nPragnya D").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    doc.add_page_break()

    add_heading(doc, "ACKNOWLEDGEMENT", 1)
    add_p(doc, "We would like to express our deepest appreciation to our supervisor, Dr. M. Upendra Kumar, for their continuous guidance, encouragement, and invaluable feedback throughout this project. We would also like to thank our university for providing the resources and environment necessary to complete this technical research.")
    doc.add_page_break()

    add_heading(doc, "ABSTRACT", 1)
    add_p(doc, "The rapid proliferation of digital payments has inevitably been accompanied by an escalation in credit card fraud, necessitating highly reliable, real-time automated detection systems. Traditional rule-based engines suffer from brittleness and high false-positive rates, thereby causing significant customer friction and operational overhead. This project presents the design, development, and deployment of a fully cloud-native Credit Card Fraud Detection System utilizing state-of-the-art machine learning techniques.")
    add_p(doc, "Trained on the highly imbalanced OpenML Credit Card Fraud Dataset (0.17% fraud rate), the system employs an XGBoost classifier integrated with scale_pos_weight tuning to adequately capture the minority class. A critical innovation of this project is the application of Isotonic Probability Calibration. While many ML implementations merely output arbitrary confidence scores, our system maps raw decision margins to true statistical probabilities, drastically improving the Brier Score from 0.00047 to 0.00040. This allows for rigorous risk-based thresholding (final optimal threshold: 0.21).")
    add_p(doc, "The finalized model (CalibratedClassifierCV) achieves an accuracy of 99.95%, precision of 86.96%, recall of 84.51%, and an F1-score of 85.71% on an untouched 15% test split. To prove real-world viability, the model is integrated into a high-performance FastAPI backend connected to a PostgreSQL database for transaction persistence. The entire stack—including a responsive HTML/JS/CSS frontend dashboard—is fully containerized with Docker and deployed live on Blitz.cloud. The result is an academic prototype demonstrating how robust ML pipelines can be seamlessly integrated into modern, scalable cloud environments.")
    doc.add_page_break()

    add_heading(doc, "TABLE OF CONTENTS", 1)
    toc_lines = ["1. INTRODUCTION", "2. LITERATURE REVIEW", "3. REQUIREMENTS AND TECHNOLOGIES", "4. SYSTEM DESIGN AND ARCHITECTURE", "5. DATASET AND DATA PREPROCESSING", "6. MACHINE LEARNING MODEL", "7. SYSTEM IMPLEMENTATION", "8. RESULTS AND EVALUATION", "9. CLOUD APPLICATION DEMONSTRATION", "10. TESTING", "11. SECURITY, LIMITATIONS AND RELIABILITY", "12. CONCLUSION AND FUTURE WORK", "REFERENCES", "APPENDICES"]
    for line in toc_lines: add_p(doc, line, bold=True)
    doc.add_page_break()

    # CHAPTER 1
    add_heading(doc, "CHAPTER 1 — INTRODUCTION", 1)
    add_heading(doc, "1.1 Background", 2)
    add_p(doc, "The global transition toward cashless economies has exponentially increased the volume of credit card transactions. While this provides unprecedented convenience, it has simultaneously opened sophisticated vectors for financial fraud. Credit card fraud costs the global economy billions of dollars annually. To mitigate these losses, financial institutions require intelligent systems capable of analyzing transactions in real-time, instantly identifying suspicious activity before funds are irrevocably transferred.")
    add_heading(doc, "1.2 Problem Statement", 2)
    add_p(doc, "Developing an effective fraud detection system presents multiple severe technical challenges. First, credit card transaction data is characterized by extreme class imbalance; legitimate transactions overwhelmingly outnumber fraudulent ones (often by a ratio of 1000:1). Standard machine learning algorithms fail in this environment because they inherently optimize for overall accuracy, which leads to trivial models that simply predict all transactions as legitimate.")
    add_p(doc, "Second, there is a substantial asymmetry in misclassification costs. A false negative (missing a fraudulent transaction) results in direct monetary theft. A false positive (blocking a legitimate transaction) results in customer frustration and reputational damage. Balancing these trade-offs requires reliable probability outputs, not just binary classifications.")
    add_heading(doc, "1.3 Motivation", 2)
    add_p(doc, "The motivation behind this project is to bridge the gap between theoretical machine learning and applied software engineering. Many academic projects successfully train fraud detection models in Jupyter Notebooks but fail to demonstrate how those models can be consumed by real users. This project aims to deliver a complete, end-to-end software product: from data cleaning and model training to API development, database integration, Docker containerization, and public cloud deployment.")
    add_heading(doc, "1.4 Aim", 2)
    add_p(doc, "To design, develop, and deploy a highly reliable, cloud-based credit card fraud detection system that uses probability-calibrated machine learning to evaluate transaction risk in real-time.")
    add_heading(doc, "1.5 Objectives", 2)
    add_p(doc, "1. To preprocess and resolve the extreme class imbalance of the OpenML dataset.\n2. To train an XGBoost classifier optimized for high recall and precision.\n3. To implement Isotonic Regression to calibrate the model's output probabilities.\n4. To develop a high-performance REST API using FastAPI to serve inferences.\n5. To integrate a PostgreSQL database for persistent transaction logging.\n6. To containerize the entire stack using Docker.\n7. To deploy the application securely to Blitz.cloud.")
    add_heading(doc, "1.6 Scope", 2)
    add_p(doc, "The scope encompasses the training of an ML model on static historical data, backend API development, database integration, and cloud deployment. It provides an academic prototype dashboard for demonstration. It does NOT include direct integration with live banking payment gateways or real-time streaming data infrastructures (like Apache Kafka).")
    add_heading(doc, "1.7 Significance", 2)
    add_p(doc, "From a machine learning perspective, this project highlights the critical necessity of Probability Calibration (Brier Score optimization) in risk-based thresholding. From a software engineering perspective, it demonstrates modern cloud-native deployment patterns (Docker, FastAPI, Managed PostgreSQL) that allow AI models to be served reliably to edge clients.")
    doc.add_page_break()

    # CHAPTER 2
    add_heading(doc, "CHAPTER 2 — LITERATURE REVIEW", 1)
    add_heading(doc, "2.1 Traditional Rule-Based Fraud Detection", 2)
    add_p(doc, "Historically, banks utilized rule-based expert systems consisting of hundreds of hardcoded 'If-Then' statements. While easy to interpret, these systems require constant manual updates, are easily circumvented by modern fraudsters, and suffer from extremely high false-positive rates.")
    add_heading(doc, "2.2 Machine Learning-Based Fraud Detection", 2)
    add_p(doc, "To overcome rule-based limitations, supervised machine learning has become the industry standard. Algorithms learn non-linear decision boundaries directly from historical transaction features. Standard algorithms like Logistic Regression and Random Forests have been widely researched.")
    add_heading(doc, "2.3 Tree-Based Models and XGBoost", 2)
    add_p(doc, "Ensemble tree-based models, particularly Extreme Gradient Boosting (XGBoost) [3], have consistently outperformed other algorithms on tabular data. XGBoost iteratively builds decision trees, where each subsequent tree attempts to correct the residual errors of the previous sequence. It natively handles sparse data and provides parameters specifically designed for imbalanced datasets.")
    add_heading(doc, "2.4 Probability Calibration", 2)
    add_p(doc, "A significant research gap in many academic fraud detection projects is the reliance on raw classifier scores. Tree-based models tend to push probabilities away from 0 and 1, resulting in poorly calibrated outputs. Niculescu-Mizil and Caruana (2005) demonstrated that Isotonic Regression can map these distorted scores into true empirical probabilities [1]. In a banking context, a true probability is absolutely required to align with financial risk thresholds [5].")
    add_heading(doc, "2.5 Real-Time Cloud Architectures", 2)
    add_p(doc, "Modern fraud detection requires inference latencies under 100 milliseconds. Microservice architectures utilizing frameworks like FastAPI deployed via Docker containers represent the current state-of-the-art for serving ML models over REST APIs.")
    doc.add_page_break()

    # CHAPTER 3
    add_heading(doc, "CHAPTER 3 — REQUIREMENTS AND TECHNOLOGIES", 1)
    add_heading(doc, "3.1 Functional Requirements", 2)
    add_p(doc, "1. The system must accept incoming transaction payloads consisting of 29 numerical features.\n2. The system must utilize the pre-trained ML model to classify the transaction as FRAUD or LEGITIMATE.\n3. The system must generate a calibrated fraud probability.\n4. The system must assign a risk level (LOW, MEDIUM, HIGH) based on the 0.21 threshold.\n5. The system must persist the transaction data and results in a PostgreSQL database.\n6. The system must expose REST API endpoints for predicting fraud, fetching history, and viewing statistics.\n7. The system must provide a web dashboard to visually demonstrate these functionalities.")
    add_heading(doc, "3.2 Non-Functional Requirements", 2)
    add_p(doc, "1. Performance: API inference should complete in under 200ms.\n2. Reliability: The application must gracefully handle missing input features via strict Pydantic validation.\n3. Scalability: The backend must be containerized to allow horizontal scaling.\n4. Maintainability: Code must be modularized (separated routes, ML services, DB services).")
    add_heading(doc, "3.3 Technology Stack", 2)
    create_table(doc, ['Component', 'Technology', 'Reason for Selection'], [
        ['Language', 'Python 3.10', 'Industry standard for data science and ML.'],
        ['ML Library', 'Scikit-Learn, XGBoost', 'High performance gradient boosting; robust calibration.'],
        ['Backend Framework', 'FastAPI', 'High speed, native async, automatic OpenAPI (Swagger) generation.'],
        ['Validation', 'Pydantic', 'Strict runtime type checking for incoming JSON payloads.'],
        ['Database ORM', 'SQLAlchemy', 'Abstracts SQL queries, allowing easy swapping of SQLite and PostgreSQL.'],
        ['Database', 'PostgreSQL', 'ACID compliant, highly reliable relational database for production.'],
        ['Frontend', 'HTML, CSS, JS, Bootstrap', 'Lightweight, static assets requiring no separate Node.js server.'],
        ['Containerization', 'Docker', 'Ensures environmental parity between local development and cloud.'],
        ['Cloud Platform', 'Blitz.cloud', 'Provides seamless managed containers and databases.']
    ])
    doc.add_page_break()

    # CHAPTER 4
    add_heading(doc, "CHAPTER 4 — SYSTEM DESIGN AND ARCHITECTURE", 1)
    add_heading(doc, "4.1 Overall System Architecture", 2)
    add_p(doc, "The system follows a classic three-tier architecture: Presentation Layer (HTML/JS), Logic Layer (FastAPI/ML), and Data Layer (PostgreSQL).")
    add_image(doc, os.path.join(figures, "arch.png"), "Figure 4.1: Overall System Architecture")
    add_heading(doc, "4.2 Machine Learning Pipeline", 2)
    add_p(doc, "The offline training pipeline is strictly segregated from the real-time inference pipeline to prevent memory bloat and latency. The training pipeline cleans data, handles splits, trains the model, applies isotonic calibration, and dumps the resulting artifacts (best_model.pkl, scaler.pkl) to disk.")
    add_image(doc, os.path.join(figures, "ml_pipeline.png"), "Figure 4.2: ML Training Pipeline")
    add_heading(doc, "4.3 Application Workflow", 2)
    add_p(doc, "When a user submits a transaction via the frontend, the JavaScript client sends an HTTP POST request to the FastAPI backend. Pydantic validates the 29 features. The ML Service loads the arrays into NumPy, scales them using the pre-fitted StandardScaler, and invokes predict_proba. Based on the threshold (0.21), risk is classified, the record is stored in PostgreSQL via SQLAlchemy, and the JSON response is returned to the client.")
    add_image(doc, os.path.join(figures, "workflow.png"), "Figure 4.3: End-to-End Application Workflow")
    add_heading(doc, "4.4 Cloud Deployment Architecture", 2)
    add_p(doc, "The application is deployed on Blitz.cloud. The Dockerfile instructs the platform to build a Python 3.10 image, copy the backend source code, ML artifacts, and frontend static files into the container. FastAPI serves the frontend assets directly from the root (/) path, eliminating CORS issues. The container connects securely to a managed PostgreSQL database instance via an injected environment variable.")
    add_image(doc, os.path.join(figures, "cloud_arch.png"), "Figure 4.4: Cloud Deployment Architecture")
    doc.add_page_break()

    # CHAPTER 5
    add_heading(doc, "CHAPTER 5 — DATASET AND DATA PREPROCESSING", 1)
    add_heading(doc, "5.1 Dataset Overview and Source", 2)
    add_p(doc, "This project utilizes the OpenML Credit Card Fraud Dataset (Dataset ID: 1597), a widely recognized benchmark in the data science community. The dataset [2] contains transactions made by European cardholders over a period of two days in September 2013.")
    add_heading(doc, "5.2 Feature Description (V1–V28 and Amount)", 2)
    add_p(doc, "The dataset contains 284,807 transactions. Due to strict financial privacy regulations, the original raw features have been obfuscated using Principal Component Analysis (PCA) into 28 continuous numerical components (V1 through V28). The only features not subjected to PCA are 'Time' and 'Amount'. The 'Time' feature was dropped because the developed backend API processes individual transactions statelessly. Therefore, the final inference feature count is exactly 29 (V1-V28 + Amount).")
    add_heading(doc, "5.3 The Challenge of Class Imbalance", 2)
    add_p(doc, "Fraud detection is an anomaly detection problem characterized by severe class imbalance. Within this dataset, out of 284,807 transactions, only 492 are classified as fraudulent. This accounts for a mere 0.172% of the dataset. Resolving this imbalance is the central data engineering challenge of this project.")
    add_heading(doc, "5.4 Data Cleaning and Deduplication", 2)
    add_p(doc, "Exactly 1,081 duplicated transactions were identified and removed. This reduced the total dataset size to 283,726 unique transactions, ensuring that identical overlapping records did not artificially inflate the model's confidence during cross-validation.")
    add_heading(doc, "5.5 Train / Validation / Test Split and Leakage Prevention", 2)
    add_p(doc, "To enforce strict mathematical quarantine, the dataset was divided into a 70% Training set, 15% Validation set, and 15% Test set BEFORE any scaling or balancing occurred. The Validation set was utilized exclusively to determine the optimal decision threshold (0.21) and to fit the Isotonic Calibrator. The Test set was mathematically quarantined until the very final evaluation.")
    add_heading(doc, "5.6 Feature Scaling", 2)
    add_p(doc, "Scikit-Learn's StandardScaler was applied. Crucially, the scaler was fitted ONLY on the Training set to calculate the mean and standard deviation. These stored parameters were then used to transform the Validation and Test sets, guaranteeing zero data leakage.")
    doc.add_page_break()

    # CHAPTER 6
    add_heading(doc, "CHAPTER 6 — MACHINE LEARNING MODEL", 1)
    add_heading(doc, "6.1 Machine Learning Problem Formulation", 2)
    add_p(doc, "The objective is a supervised binary classification problem. Given a feature vector X consisting of 29 numerical dimensions, the model must learn a mapping function f(X) that outputs a probability P(y=1|X), where y=1 denotes a fraudulent transaction.")
    add_heading(doc, "6.2 Why XGBoost?", 2)
    add_p(doc, "Extreme Gradient Boosting (XGBoost) [3] builds sequential decision trees where each new tree specifically targets and minimizes the residual errors of the previous trees. It is highly optimized, handles non-linear relationships effortlessly, and natively supports class weighting.")
    add_heading(doc, "6.3 Handling Imbalance with scale_pos_weight", 2)
    add_p(doc, "Instead of using SMOTE, this project leveraged XGBoost's native algorithmic penalty: `scale_pos_weight`. By calculating the ratio of negative instances to positive instances (approximately 576 to 1), the algorithm penalizes a false negative 576 times more heavily than a false positive. This forces the decision trees to focus intensely on the rare fraudulent patterns.")
    add_heading(doc, "6.4 Decision Threshold Optimization", 2)
    add_p(doc, "By default, machine learning classifiers use a 0.5 decision threshold. However, due to the high cost of missing a fraudulent transaction, the threshold was empirically optimized on the Validation set by maximizing the F1-Score. The optimal threshold discovered was 0.21.")
    add_heading(doc, "6.5 Probability Calibration (Isotonic Regression)", 2)
    add_p(doc, "Tree-based algorithms do not output true statistical probabilities; they output 'margins'. To correct this, Isotonic Regression (via Scikit-Learn's CalibratedClassifierCV) was applied. Isotonic Regression fits a strictly non-decreasing step function that maps the raw XGBoost scores to calibrated empirical probabilities. When the calibrated model outputs 0.21, it means that historically, 21% of transactions with that score were actually fraudulent. This calibration is absolutely mandatory for banks to align ML outputs with financial risk thresholds.")
    add_heading(doc, "6.6 Inference Pipeline and Risk Classification", 2)
    add_p(doc, "During real-time inference on the FastAPI backend, the raw features are scaled, passed to the model, and a calibrated probability is generated. Based on the 0.21 threshold, the system executes the following risk logic:\n- LOW RISK: Calibrated Probability <= 0.21\n- MEDIUM RISK: Calibrated Probability > 0.21 and <= 0.315\n- HIGH RISK: Calibrated Probability > 0.315")
    doc.add_page_break()

    # CHAPTER 7
    add_heading(doc, "CHAPTER 7 — SYSTEM IMPLEMENTATION", 1)
    add_heading(doc, "7.1 Backend Implementation (FastAPI)", 2)
    add_p(doc, "The backend is implemented using FastAPI [4], selected for its native support for asynchronous programming and instantaneous request validation. It handles HTTP requests, orchestrates ML predictions, and communicates with the database.")
    add_heading(doc, "7.2 Request Validation with Pydantic", 2)
    add_p(doc, "Pydantic schemas strictly define the expected incoming JSON payload. If a client attempts to submit a transaction missing a required feature, FastAPI automatically rejects the request with a detailed HTTP 422 error.")
    add_heading(doc, "7.3 REST API Endpoints", 2)
    add_p(doc, "The backend exposes endpoints like POST `/predict/`, GET `/transactions/`, and GET `/statistics/`. A utility endpoint, GET `/demo/transaction`, fetches a known transaction from the dataset to facilitate UI demonstrations without requiring manual entry of 29 PCA features.")
    add_heading(doc, "7.4 Database Architecture (PostgreSQL & SQLAlchemy)", 2)
    add_p(doc, "Data persistence is managed via SQLAlchemy. A single `Transaction` model dictates the schema. The production system utilizes a managed PostgreSQL instance provisioned by Blitz.cloud, connected securely via the `DATABASE_URL` environment variable.")
    add_heading(doc, "7.5 Unified Frontend Implementation", 2)
    add_p(doc, "The user interface is built using HTML5, CSS3, and JavaScript. To simplify cloud deployment and eliminate CORS security issues, FastAPI's `StaticFiles` module mounts the `frontend/` directory, allowing the frontend to be served directly alongside the API.")
    add_heading(doc, "7.6 Containerization and Cloud Deployment", 2)
    add_p(doc, "The entire stack is containerized using Docker. The `Dockerfile` specifies a lightweight Python 3.10 runtime, copies artifacts, and uses `Uvicorn` to serve the API. Blitz.cloud automatically builds the image, provisions PostgreSQL, and exposes the application over HTTPS.")
    doc.add_page_break()

    # CHAPTER 8
    add_heading(doc, "CHAPTER 8 — RESULTS AND EVALUATION", 1)
    add_heading(doc, "8.1 Evaluation Methodology", 2)
    add_p(doc, "The system was evaluated strictly on the untouched 15% Test Split to ensure a completely unbiased representation of real-world performance.")
    add_heading(doc, "8.2 Final Evaluation Metrics", 2)
    create_table(doc, ['Metric', 'Uncalibrated XGBoost', 'Final Calibrated Model'], [
        ['Accuracy', '99.95%', '99.95%'],
        ['Precision', '86.96%', '86.96%'],
        ['Recall', '84.51%', '84.51%'],
        ['F1 Score', '85.71%', '85.71%'],
        ['ROC-AUC', '97.98%', '97.81%'],
        ['PR-AUC', '86.40%', '84.93%'],
        ['Brier Score', '0.00047', '0.00040']
    ])
    add_heading(doc, "8.3 Metric Analysis and Justification", 2)
    add_p(doc, "Accuracy Analysis: Achieving 99.95% accuracy is theoretically impressive but practically misleading due to class imbalance. Precision, Recall, and PR-AUC are far more critical.")
    add_p(doc, "Recall and Precision: The model successfully detects 84.51% of all fraudulent transactions (Recall). Of all the transactions it flags as fraud, 86.96% are genuinely fraudulent (Precision). This represents an excellent operational balance.")
    add_heading(doc, "8.4 The Impact of Probability Calibration", 2)
    add_p(doc, "It is crucial to understand that Isotonic Calibration does NOT change the ranked ordering of predictions; therefore, binary classification metrics (Accuracy, Precision, Recall, F1) remain identical. The ROC-AUC and PR-AUC experience negligible shifts due to mathematical smoothing effects.")
    add_p(doc, "However, the Brier Score significantly improved (dropped) from 0.00047 to 0.00040. The Brier Score measures the mean squared difference between the predicted probability and the actual outcome. The lower Brier Score indicates improved probabilistic calibration and greater reliability of the model's predicted probabilities. This makes the probability outputs more suitable for risk-based thresholding and decision-making.")
    add_image(doc, os.path.join(figures, "calibrated_xgboost_cm.png"), "Figure 8.1: Confusion Matrix")
    add_image(doc, os.path.join(figures, "roc_curve_comparison.png"), "Figure 8.2: ROC Curve")
    doc.add_page_break()

    # CHAPTER 9
    add_heading(doc, "CHAPTER 9 — CLOUD APPLICATION DEMONSTRATION", 1)
    add_p(doc, "The system was successfully deployed and verified on Blitz.cloud. The live application is accessible at:")
    doc.add_paragraph('https://cloud-computing.tarakram.blitz.cloud/index.html').alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_image(doc, os.path.join(screenshots, "01_dashboard.png"), "Figure 9.1: Live Deployed Fraud Detection Dashboard")
    add_p(doc, "Figure 9.1 shows the frontend UI served directly by FastAPI. It contains input fields for the 29 required features, alongside automated Demo controls to populate real dataset examples.")
    add_image(doc, os.path.join(screenshots, "02_legitimate_demo.png"), "Figure 9.2: Legitimate Transaction Input")
    add_image(doc, os.path.join(screenshots, "03_legitimate_prediction.png"), "Figure 9.3: Legitimate Prediction (LOW Risk)")
    add_p(doc, "Figure 9.3 demonstrates a successful REST API call predicting a Legitimate transaction. The calibrated fraud probability is negligible, resulting in a LOW risk classification.")
    add_image(doc, os.path.join(screenshots, "04_fraud_demo.png"), "Figure 9.4: Fraud Transaction Input")
    add_image(doc, os.path.join(screenshots, "05_fraud_prediction.png"), "Figure 9.5: Fraud Prediction (HIGH Risk)")
    add_p(doc, "Figure 9.5 demonstrates the system correctly flagging a known fraudulent transaction. The probability exceeds the 0.21 threshold, resulting in a HIGH risk classification.")
    add_image(doc, os.path.join(screenshots, "06_transaction_history.png"), "Figure 9.6: Live Transaction History & Statistics from PostgreSQL")
    add_p(doc, "Figure 9.6 verifies the database integration. Every prediction made via the dashboard is committed to the cloud-managed PostgreSQL database. The statistics cards dynamically update to reflect the overall fraud ratio.")
    add_image(doc, os.path.join(screenshots, "07_swagger.png"), "Figure 9.7: Automatically Generated Swagger API Documentation")
    add_p(doc, "Figure 9.7 highlights the /docs endpoint, providing interactive OpenAPI specifications for third-party developers to integrate with the backend.")
    doc.add_page_break()

    # CHAPTER 10
    add_heading(doc, "CHAPTER 10 — TESTING", 1)
    add_heading(doc, "10.1 Testing Strategy", 2)
    add_p(doc, "The system underwent unit testing, API integration testing (via Pytest and FastAPI TestClient), local Docker Compose verification, and final production Cloud verification.")
    add_heading(doc, "10.2 Comprehensive Test Results", 2)
    create_table(doc, ['Test Description', 'Expected Result', 'Actual Output', 'Status'], [
        ['Backend Health (/health)', 'HTTP 200, status: healthy', 'HTTP 200, {"status": "healthy"}', 'PASS'],
        ['Model Info (/model-info)', 'HTTP 200, model loaded', 'CalibratedClassifierCV, 29 features', 'PASS'],
        ['Fraud Demo Route', 'Return known fraud sample', 'Returned valid dataset fraud JSON', 'PASS'],
        ['Legitimate Demo Route', 'Return known legit sample', 'Returned valid dataset legit JSON', 'PASS'],
        ['Fraud Prediction', 'Prediction: FRAUD, Risk: HIGH', 'FRAUD predicted, Prob > 0.21', 'PASS'],
        ['Legit Prediction', 'Prediction: LEGITIMATE, Risk: LOW', 'LEGITIMATE predicted, Prob <= 0.21', 'PASS'],
        ['Database Persistence', 'Transaction saved in DB', 'Record verified in /transactions', 'PASS'],
        ['Statistics Update', 'Stats reflect new transaction', 'Counts and percentages incremented', 'PASS'],
        ['Frontend Application (/index.html)', 'Dashboard HTML loads successfully', 'Live dashboard loaded successfully from the deployed application URL', 'PASS']
    ])
    doc.add_page_break()

    # CHAPTER 11
    add_heading(doc, "CHAPTER 11 — SECURITY, LIMITATIONS AND RELIABILITY", 1)
    add_heading(doc, "11.1 Security Implementation", 2)
    add_p(doc, "The application uses Pydantic schemas to validate incoming request data and reject malformed, incomplete, or incorrectly typed payloads. This provides a controlled input-validation layer and reduces the risk associated with unexpected or malformed client input. The PostgreSQL connection string is supplied through the DATABASE_URL environment variable rather than being hardcoded in the source code.")
    add_heading(doc, "11.2 Model Reliability and False Positives", 2)
    add_p(doc, "With a precision of 86.96%, roughly 13% of transactions flagged as fraud are actually legitimate (false positives). In a banking context, this results in blocked cards and requires manual human review. While acceptable for a prototype, banking institutions often require precision rates exceeding 95% to minimize customer friction.")
    add_heading(doc, "11.3 Academic Prototype Limitations", 2)
    add_p(doc, "It must be explicitly stated that this is an academic prototype, not a production-grade banking platform. The dataset features (V1-V28) are PCA-transformed and anonymized, rendering the model largely unexplainable (a 'black box'). Real-world banks require Explainable AI (XAI) to legally justify why a transaction was declined. Furthermore, this system lacks robust user authentication (e.g., JWT/OAuth2) and cannot process millions of concurrent streams.")
    doc.add_page_break()

    # CHAPTER 12
    add_heading(doc, "CHAPTER 12 — CONCLUSION AND FUTURE WORK", 1)
    add_heading(doc, "12.1 Conclusion", 2)
    add_p(doc, "This project successfully architected and deployed a highly performant Cloud-Based Credit Card Fraud Detection System. By addressing extreme class imbalance and rigorously calibrating the XGBoost output probabilities, the system is capable of supplying highly reliable real-time risk scores (Recall: 84.51%, Precision: 86.96%). The integration of FastAPI, PostgreSQL, and Docker culminated in a seamless cloud deployment on Blitz.cloud, proving that advanced machine learning models can be effectively operationalized into usable software products.")
    add_heading(doc, "12.2 Future Work", 2)
    add_p(doc, "1. Streaming Inference: Upgrading the REST API to consume event-driven streaming data using Apache Kafka.\n2. Continuous Training: Implementing a pipeline to automatically retrain the model as new transaction patterns (data drift) emerge.\n3. Explainable AI (XAI): Integrating SHAP (SHapley Additive exPlanations) values to provide users with a breakdown of exactly which features triggered the fraud alert.\n4. Authentication: Securing the API and Dashboard using OAuth2 JWT bearer tokens.")
    doc.add_page_break()

    # REFERENCES
    add_heading(doc, "REFERENCES", 1)
    add_p(doc, "[1] Andrea Dal Pozzolo, Olivier Caelen, Reid A. Johnson and Gianluca Bontempi. 'Calibrating Probability with Undersampling for Unbalanced Classification'. In Symposium on Computational Intelligence and Data Mining (CIDM), IEEE, 2015.")
    add_p(doc, "[2] OpenML, 'creditcard dataset (ID: 1597)', [Online]. Available: https://www.openml.org/d/1597")
    add_p(doc, "[3] Chen, T., & Guestrin, C. (2016). 'XGBoost: A Scalable Tree Boosting System'. In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (pp. 785-794).")
    add_p(doc, "[4] FastAPI Documentation. [Online]. Available: https://fastapi.tiangolo.com/")
    add_p(doc, "[5] Scikit-Learn Developers. 'Probability Calibration'. [Online]. Available: https://scikit-learn.org/stable/modules/calibration.html")
    doc.add_page_break()

    # APPENDICES
    add_heading(doc, "APPENDIX A — API ENDPOINTS", 1)
    create_table(doc, ['HTTP Method', 'Endpoint', 'Purpose'], [
        ['GET', '/index.html', 'Serves the deployed frontend dashboard.'],
        ['GET', '/health', 'Verifies the FastAPI backend is responsive.'],
        ['GET', '/model-info', 'Returns ML model metadata (name, feature count).'],
        ['POST', '/predict/', 'Accepts 29 features and returns risk/probability.'],
        ['GET', '/transactions/', 'Fetches recent transaction history from DB.'],
        ['GET', '/statistics/', 'Aggregates counts and fraud percentages.'],
        ['GET', '/demo/transaction', 'Returns a valid dataset sample for UI testing.']
    ])

    output_path = os.path.join(base_dir, "..", "Cloud_Based_Credit_Card_Fraud_Detection_Report_Final.docx")
    doc.save(output_path)
    print(f"Report generated successfully at {output_path}")

if __name__ == "__main__":
    generate()
