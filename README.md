# BDA Stock Predictor

**Repository:** https://github.com/gaya3jayan-11/StockPredictor.git

This project is a **Big Data Analytics (BDA)** system built to **track and improve the accuracy of a stock prediction model** using MongoDB.

Our goal is to demonstrate **Model Improvement**—proving that our system can detect and fix prediction errors over time (MLOps).

---

## 1. Project Justification (Why MongoDB is Essential)

| Concept | What It Does (Simple Terms) | Why MongoDB? |
| :--- | :--- | :--- |
| **Historical Tracking** | Stores every prediction (the model's guess) and its expected outcome. | Stores **flexible records** that can be easily **updated/enriched** later. |
| **Accuracy Audit** | An automatic process that checks old guesses and calculates the **Error Score** (the model's grade). | MongoDB allows us to efficiently **UPDATE** the original record by adding the final score (Actual Price). |
| **Model Improvement** | Our system uses the historical bad scores from MongoDB to train a **Correction Model** (a "Tutor") to remove the model's systematic bias. | **Reporting** proves the success: Error Rate drops from **25% to 4%**. |

---

## 2. Setup Guide (For Teammates)

Follow these steps exactly to run the project.

### Prerequisites

1.  **MongoDB Server:** You must run the `mongod` command in a separate terminal window to start the local database server.
2.  **Secret File:** You **must** obtain the secure **`.env` file** (containing the cloud database password) from the project owner and place it in the project's root folder.

### Installation and Launch Commands

| Action | Windows (PowerShell) COMMANDS | Mac / Linux (Bash) COMMANDS |
| :--- | :--- | :--- |
| **1. Clone Project** | `git clone https://github.com/gaya3jayan-11/StockPredictor.git && cd StockPredictor` | `git clone https://github.com/gaya3jayan-11/StockPredictor.git && cd StockPredictor` |
| **2. Setup Environment** | `python -m venv venv` | `python3 -m venv venv` |
| **3. Activate Venv** | `.\venv\Scripts\activate` | `source venv/bin/activate` |
| **4. Install Libraries** | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| **5. LAUNCH APP** | `streamlit run streamlit_app.py` | `streamlit run streamlit_app.py` |

---

## 3. Demonstration Flow (The Proof)

Use the Streamlit app to show the grader the project's success:

1.  **Initial Problem:** Show the **Historical Accuracy Tracking** tab to prove the original model had a high error rate ($\approx 25\%$).
2.  **Prove Improvement:** Explain the **Correction Model** process.
3.  **Final Proof:** Show the corrected records in the report where the error rate is now **low ($\mathbf{\approx 4\%}$)**. This is the evidence that the BDA system successfully made the AI better.
