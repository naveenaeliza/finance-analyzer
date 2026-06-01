# 💰 AI Personal Finance Analyzer

An AI-powered personal finance analysis platform that helps users understand spending patterns, detect anomalies, forecast future expenses, and receive personalized financial insights using Generative AI.

## Features

### 📄 Bank Statement Processing

* Upload PDF bank statements
* Automatic transaction extraction using PDFPlumber
* Structured transaction parsing and cleaning

### 📊 Financial Analytics Dashboard

* Total spending analysis
* Average transaction value
* Category-wise expense visualization
* Interactive charts using Plotly

### 🤖 AI Financial Advisor

* Personalized spending insights using Google Gemini AI
* Budget recommendations
* Financial habit analysis
* Expense optimization suggestions

### 🔮 Spending Forecasting

* Future expense prediction using Prophet
* Trend analysis and visualization
* Forecast confidence intervals

### 🚨 Anomaly Detection

* Detect unusual transactions
* Isolation Forest-based anomaly identification
* Fraud and spending irregularity alerts

## Tech Stack

### Frontend

* Streamlit

### Data Processing

* Pandas
* NumPy
* PDFPlumber
* Regular Expressions

### Machine Learning

* Prophet
* Scikit-Learn (Isolation Forest)

### AI Integration

* Google Gemini API

### Visualization

* Plotly

### Backend (Planned Extension)

* FastAPI
* MySQL

## Project Structure

finance-analyzer/

├── app.py

├── pdf_parser.py

├── requirements.txt

├── sample_transactions.csv

├── backend/

│ ├── main.py

│ └── requirements.txt

└── .streamlit/

## Installation

### Clone Repository

```bash
git clone https://github.com/naveenaeliza/finance-analyzer.git
cd finance-analyzer
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure API Key

Create:

```text
.streamlit/secrets.toml
```

Add:

```toml
GEMINI_API_KEY="YOUR_API_KEY"
```

### Run Application

```bash
streamlit run app.py
```

## Future Enhancements

* User authentication
* Cloud database integration
* Multi-bank statement support
* Expense categorization using LLMs
* Real-time transaction monitoring
* FastAPI microservice architecture
* Deployment on Render

## Author

**Naveena Eliza Thomas**

B.Tech Computer Science (AI)

GitHub: https://github.com/naveenaeliza
