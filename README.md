# datascience-equity-research

> 👋 **New here?** Read **[START-HERE.md](START-HERE.md)** first (5-min overview), then
> **[docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md)** for the full, plain-language walk-through.
> Run it: `pip install pandas numpy yfinance` → `cd engine && python run_today.py`.
> Structure: **`app/`** (website) · **`engine/`** (Python + data) · **`docs/`** (explanations).

Manual + AI-powered stock **discovery** system for the Thai stock market (SET100).
*Educational Data Science project — not investment advice.*

# SETScout

> An Explainable Investment Decision Support System (EIDSS) for the Thai Stock Market

SETScout is a web-based investment decision support platform developed as a senior Data Science in Finance project. The system assists retail investors in discovering Thai stocks that are worthy of further investigation by integrating quantitative financial indicators, qualitative market information, and explainable artificial intelligence into a unified recommendation framework.

Unlike traditional stock screening platforms that require users to manually browse hundreds of listed companies, SETScout automatically identifies promising investment opportunities and provides transparent explanations behind every recommendation, allowing investors to make more informed investment decisions.

---

# Project Vision

Retail investors often struggle with one fundamental problem: **they do not know where to begin.**

Existing trading platforms such as Streaming provide execution tools but offer limited support during the stock discovery process. Investors must manually search through hundreds of listed companies, financial statements, technical indicators, and market news before deciding which stocks deserve attention.

SETScout aims to bridge this gap by functioning as an **Explainable Investment Decision Support System** rather than an automated trading system. Instead of predicting stock prices or making investment decisions on behalf of investors, the platform identifies companies that are most worthy of further investigation through a transparent multi-factor evaluation framework.

---

# Objectives

The project aims to:

- Build a complete financial data pipeline using real-world financial data.
- Develop a multi-factor recommendation framework for Thai listed companies.
- Integrate quantitative and qualitative financial information.
- Provide explainable recommendations using Large Language Models (LLMs).
- Demonstrate an end-to-end Data Science workflow, from data engineering to deployment.

---

# Key Features

- Multi-factor stock recommendation engine
- Financial statement analysis
- Technical indicator analysis
- News sentiment integration
- Macroeconomic factor analysis
- Explainable AI-generated investment summaries
- Interactive web dashboard
- Historical recommendation tracking
- Sector-based stock discovery

---

# System Architecture

```
External Data Sources
──────────────────────────────────────────────

Yahoo Finance
Stock Exchange of Thailand (SET)
Financial Statements
Bangkok Post News
Federal Reserve Economic Data (FRED)

                │

        Data Collection

                │

   Data Cleaning & Validation

                │

        Data Storage

                │

      Feature Engineering

                │

 Multi-factor Recommendation Engine

                │

      LLM Explanation Module

                │

        Interactive Dashboard
```

---

# Data Pipeline

## 1. Data Collection

Financial market information is collected from multiple reliable data sources, including stock prices, financial statements, company information, macroeconomic indicators, and financial news. Python-based data collection tools and APIs are used to automate the acquisition process.

## 2. Data Cleaning & Validation

Raw datasets are cleaned, validated, and standardized before further analysis. This stage includes handling missing values, duplicate removal, date formatting, ticker normalization, and consistency checks across different data sources.

## 3. Data Storage

Processed data are stored in a centralized relational database to support efficient querying, feature engineering, and historical recommendation tracking.

## 4. Feature Engineering

Raw financial information is transformed into meaningful quantitative and qualitative features, including:

- Fundamental indicators
- Technical indicators
- Financial ratios
- Macroeconomic variables
- News sentiment
- Risk indicators

These engineered features become the inputs for the recommendation engine.

## 5. Multi-factor Recommendation Engine

Rather than relying on a single predictive model, SETScout evaluates each company across multiple investment dimensions.

The current framework consists of:

- Fundamental Analysis
- Technical Analysis
- Qualitative Analysis
- Risk Assessment

Each dimension contributes to an overall **Investment Attractiveness Score**, which is used to rank companies according to their investment potential.

## 6. LLM Explanation Module

Large Language Models (LLMs) are **not responsible for selecting stocks**.

Instead, the LLM is used to:

- summarize financial news
- explain recommendation results
- translate quantitative outputs into human-readable insights
- improve interpretability for retail investors

This ensures that investment recommendations remain transparent and explainable.

## 7. Web Dashboard

The final recommendations are presented through an interactive web application where users can explore:

- Top recommended stocks
- Sector rankings
- Company information
- Financial indicators
- News summaries
- Recommendation history
- Investment explanations

---

# Primary Research

คือจะเอาความเห็นของอาจารย์ว่าเรียงลำดับความสำคัญอย่างไรกับแต่ละปัจจัย เพื่อมาใส่เป็น weights
To improve the practical relevance of the recommendation framework, the project incorporates **primary data collected through expert interviews** with finance and economics lecturers from the National Institute of Development Administration (NIDA).

The interviews aim to identify the investment factors that experienced practitioners consider most important during the stock screening process.

Participants will evaluate the importance of factors such as:

- Profitability
- Revenue Growth
- Financial Stability
- Technical Trend
- Industry Outlook
- News Sentiment
- Macroeconomic Conditions
- Investment Risk

The aggregated responses will be normalized to construct the **initial weighting scheme** of the Multi-factor Recommendation Engine.

Rather than allowing expert opinions to directly determine investment recommendations, the interviews serve as an academically grounded foundation for designing an explainable recommendation framework supported by both financial literature and domain expertise.

---

# Technology Stack

## Programming Language

- Python

## Data Science

- Pandas
- NumPy
- Scikit-learn

## Data Collection

- yfinance
- requests
- BeautifulSoup

## Database

- PostgreSQL
- SQLAlchemy

## Visualization

- Plotly

## Web Application

- Streamlit

## Artificial Intelligence

- Large Language Model (LLM)

## Version Control

- Git
- GitHub

---

# Repository Structure

```
SETScout/

│── README.md
│── requirements.txt

├── docs/
│      proposal.md
│      product_vision.md
│      architecture.md

├── data/
│      raw/
│      processed/

├── database/

├── models/

├── notebooks/

├── src/
│      data_collection/
│      preprocessing/
│      feature_engineering/
│      recommendation/
│      llm/
│      dashboard/

└── tests/
```

---

# Future Development

Future versions of SETScout may include:

- Portfolio optimization
- Personalized recommendations
- Reinforcement learning
- Alternative data integration
- Real-time market monitoring
- Automated backtesting framework

---

# Team

Senior Year Data Science in Finance Project

Department of Financial Engineering

King Mongkut's Institute of Technology Ladkrabang (KMITL) × National Institute of Development Administration (NIDA)

---

# Disclaimer

SETScout is developed solely for educational and research purposes.
The platform provides investment decision support and should **not** be interpreted as financial advice or a guarantee of future investment performance. Final investment decisions remain the responsibility of the user.