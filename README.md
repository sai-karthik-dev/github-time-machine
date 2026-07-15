# ⏳ GitHub Time Machine

**GitHub Time Machine** is an AI-powered engineering intelligence platform that provides deep insights into your repositories. It allows you to visualize commit timelines, understand complex code architectures, simulate the impact of changes, and identify technical debt through intuitive heatmaps.

---

## 🚀 Key Features

- **Architectural Explanations:** Understand complex repository structures and module interactions through AI-driven chat.
- **Change Impact Simulator:** Predict the downstream effects of your code modifications before you commit.
- **Knowledge Graph:** Visualize the relationships between different parts of your codebase.
- **Commit Timeline:** A beautiful, interactive timeline of repository events.
- **Technical Debt Heatmap:** Identify high-churn or problematic areas of your code at a glance.

## 🛠️ Tech Stack

- **Frontend:** [Next.js 15](https://nextjs.org/) + [React 19](https://react.dev/)
- **Styling:** [Tailwind CSS v4](https://tailwindcss.com/)
- **AI Backend / API:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **AI Engine:** OpenAI Integration
- **Database:** Supabase (Planned integration)

## 📁 Project Structure

The repository is organized into the following main directories:

```text
github-time-machine/
├── ai/          # AI orchestration backend (FastAPI + OpenAI)
├── backend/     # Core application backend services
├── frontend/    # Next.js web application
├── data/        # Mock data and datasets
└── docs/        # Additional project documentation
```

## 🏁 Getting Started

### Prerequisites

- **Node.js** (v18 or higher)
- **Python** (3.9 or higher)
- **OpenAI API Key**

### 1. AI Backend Setup

Navigate to the `ai` directory to set up the orchestration service.

```bash
cd ai

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the backend server
uvicorn app.main:app --reload --port 8001
```
*(For detailed endpoint information and demo mode, see the [AI README](./ai/README.md).)*

### 2. Frontend Setup

Navigate to the `frontend` directory to launch the web application.

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to view the application.

## 🤝 Contributing

Contributions are welcome! If you'd like to improve the GitHub Time Machine, please fork the repository, create a feature branch, and submit a pull request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
