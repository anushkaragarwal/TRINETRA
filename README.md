# TRINETRA 🌊
### AI-Powered Multi-Hazard Monitoring and Early Warning System

TRINETRA is a multi-hazard monitoring and early warning system designed to support disaster preparedness through data-driven risk assessment. It combines river hazard information, rainfall data, satellite observations, and terrain information to help identify potentially vulnerable areas and communicate hazard risks.

## 🌍 Overview

Natural disasters such as floods can threaten lives, infrastructure, and communities. TRINETRA aims to bring multiple environmental data sources together into a unified platform to support hazard monitoring, risk analysis, and early warning.

The project integrates data processing, hazard assessment, and visualization to make environmental risk information easier to understand.

## ✨ Key Features

- **River Hazard Monitoring:** Integrates river-related data from CWC/NWDP sources for river hazard analysis.
- **Satellite Data Integration:** Includes data-fetching workflows for Sentinel-1 and Sentinel-2 satellite observations.
- **Rainfall Analysis:** Supports the integration of rainfall information for environmental risk assessment.
- **Terrain Analysis:** Uses Digital Elevation Model (DEM) and terrain-related information to support hazard analysis.
- **AI-Assisted Risk Assessment:** Combines processed environmental inputs to support hazard identification and risk evaluation.
- **Unified Hazard Assessment:** Aims to combine multiple hazard indicators into a consolidated risk score and risk level.
- **Hazard Zone Visualization:** Provides a dashboard for exploring hazard-related information and identified risk zones.
- **Early Warning Support:** Designed to support timely communication of hazard warnings and risk information.

## 🛠️ Technology Stack

- **Backend:** Python, FastAPI
- **Dashboard:** Streamlit
- **Database:** MongoDB Atlas
- **Data Processing:** Pandas
- **Satellite Data:** Sentinel-1 and Sentinel-2 data-fetching workflows
- **Other Components:** Environmental data processing, hazard assessment, and visualization

## 🏗️ Project Structure

```text
TRINETRA/
├── assets/       # Project assets and resources
├── backend/      # Backend services and API logic
├── data/         # Environmental and processed datasets
├── frontend/     # Frontend components
├── models/       # Model-related files
├── scripts/      # Data fetching and processing scripts
├── src/          # Source modules
├── app.py        # Streamlit dashboard entry point
├── requirements.txt
├── .env.example  # Example environment configuration
└── README.md
```

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version for the project's dependencies
- pip
- MongoDB Atlas access, if required by the configured backend
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/anushkagaragwal/TRINETRA.git
cd TRINETRA
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Check `.env.example` and configure the required environment variables for your local setup. Add database credentials and any required API keys to your local environment file.

**Important:** Never commit real API keys, passwords, or database credentials to GitHub.

### 5. Run the Backend

From the project root, run:

```bash
uvicorn backend.main:app --reload
```

If the backend starts successfully, the FastAPI API documentation is generally available at:

```text
http://127.0.0.1:8000/docs
```

### 6. Run the Dashboard

Open another terminal in the project root, activate the virtual environment, and run:

```bash
streamlit run app.py
```

The Streamlit dashboard is generally available at:

```text
http://localhost:8501
```

**Note:** Follow the project's actual module structure and environment configuration if any command or dependency differs in your local setup.

## 🔄 How It Works

1. **Data Acquisition:** Collects or loads available river, rainfall, satellite, and terrain-related information.
2. **Data Processing:** Processes environmental datasets into a form suitable for analysis.
3. **Hazard Assessment:** Uses the available hazard assessment logic to evaluate environmental risk indicators.
4. **Risk Classification:** Supports the identification of different levels of hazard risk.
5. **Visualization:** Presents available information through the dashboard and related visual components.
6. **Early Warning Support:** Helps communicate potential risks so that users can make more informed decisions.

## 🎯 Project Objectives

- Improve access to environmental hazard information.
- Integrate multiple data sources into a unified monitoring platform.
- Support data-driven hazard assessment and risk visualization.
- Contribute to disaster preparedness and early warning efforts.
- Build a scalable foundation for multi-hazard monitoring.

## 🚧 Current Development

TRINETRA is under active development. Data integration, hazard assessment, visualization, and early warning capabilities are being developed and refined as the project evolves.

The availability and accuracy of individual features depend on the configured data sources, backend services, and model implementations.

## 🔮 Future Scope

- Improve real-time environmental data integration.
- Enhance predictive hazard assessment.
- Expand geographic coverage and hazard types.
- Improve alert delivery and notification mechanisms.
- Develop more accessible, map-based risk visualization.

## 🤝 Contributions

Contributions, suggestions, and feedback that help improve TRINETRA are welcome.

## 📄 License

A license has not yet been specified. Usage and redistribution are subject to the repository owner's chosen license.

---

**TRINETRA — Integrating environmental intelligence to support safer, more prepared communities.**
