# Final Project II: AI Healthcare Insurance Planner

👥 **Team Members (Group: Placed BtechGroup07, Division D4)**

| # | Name | Enrollment No |
|---|---|---|
| 1 | Himani Jaiswal | EN22CS301423 |
| 2 | Irya Patni | EN22CS301436 |
| 3 | Uday Dubey | EN22EL301058 |
| 4 | Chetan Oswal | EN22CS30 |

---

## 1. Project Objective
The objective of this project is to build a comprehensive, microservice-based web application that leverages **Agentic AI** (LangChain) and **Generative AI** (Google Gemini) to assist users with healthcare and insurance planning. 

By describing their medical condition or needs, the system intelligently processes the query to provide a customized treatment plan, insurance recommendations, cost estimations, and schedules, all orchestrated through a robust DevOps pipeline.

## 2. Problem Statement Mapping (DevOps + Agent AI + GenAI)
- **Agentic AI**: Utilizes LangChain to break down complex user health prompts and structure a multi-faceted response (treatment, insurance, cost, schedule).
- **Generative AI**: Integrates Google Gemini models for rich text generation based on the user's specific query.
- **DevOps**: Employs a robust, production-ready infrastructure using Docker (multi-stage builds), Docker Compose, GitHub Actions for CI/CD, and Kubernetes for scalable deployment.

## 3. High-Level Design (HLD)
The architecture consists of three core components:
1. **Frontend (React + Vite)**: A premium, responsive user interface styled with custom CSS (glassmorphism, dark mode).
2. **API Gateway (Rust + Axum)**: A high-performance, safe backend that handles client requests, CORS, and routing.
3. **AI Service (Python + FastAPI)**: The intelligent core running LangChain agents and executing LLM chains.

## 4. Low-Level Design (LLD)
- **React Client**: Uses `axios` for HTTP requests to the Rust backend. State management via React Hooks, with `localStorage` for chat history persistence.
- **Rust Backend**: Uses `axum` for asynchronous routing and `reqwest` to proxy requests to the Python service. Implements strict JSON serialization/deserialization.
- **Python AI Service**: Uses `FastAPI` for the web framework. `LangChain` constructs the prompt template and parses the JSON response from `gemini-2.5-flash`. Dynamic healthcare infographic images are generated securely via curated Unsplash endpoints.

## 5. Folder Structure Explanation
```text
.
├── ai-service-python/     # Python FastAPI service for AI processing (LangChain, Gemini)
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile         # Multi-stage build for Python
├── backend-rust/          # Rust API Gateway (Axum)
│   ├── src/main.rs
│   ├── Cargo.toml
│   └── Dockerfile         # Multi-stage build for Rust (builder -> distroless)
├── frontend/              # React frontend (Vite)
│   ├── src/
│   │   ├── App.jsx        # Main UI logic
│   │   └── index.css      # Custom premium styles
│   ├── package.json
│   └── Dockerfile         # Multi-stage build for Node.js -> Nginx
├── k8s/                   # Kubernetes deployment manifests
│   ├── deployments.yaml
│   └── services.yaml
├── .github/workflows/     # GitHub Actions CI/CD pipelines
│   └── ci.yml
├── docker-compose.yml     # Local orchestration
└── README.md              # Project documentation
```

## 6. Setup & How to Run (Local Development)

**Prerequisites:**
- Docker and Docker Compose installed on your local machine.

**Step-by-Step Instructions:**

1. **Open a terminal** and navigate to the project directory:
   ```bash
   cd /Users/irya.patni/Desktop/Final_project
   ```

2. **Export your Google Gemini API key**:
   The application requires a valid Gemini API key to function. A `.env` file containing `GOOGLE_API_KEY=AIzaSyBid...` has been provided in the root directory. Docker Compose will automatically inject this into the AI service.

3. **Build and start the application using Docker Compose**:
   ```bash
   docker-compose up --build
   ```
   *(This command will build the React frontend, compile the Rust backend, and install the Python AI service dependencies inside isolated containers. It may take a few minutes the first time.)*

4. **Access the application**:
   - Open your web browser.
   - Navigate to **[http://localhost:3000](http://localhost:3000)**.
   - Try entering a query like *"I have type 2 diabetes, suggest treatment and insurance plan"*.

5. **To stop the application**:
   Press `Ctrl + C` in the terminal where Docker Compose is running, or run:
   ```bash
   docker-compose down
   ```

## 7. Docker & Kubernetes Usage
- **Docker Compose**: Maps the frontend to port `3000`, Rust backend to `8080`, and Python service to `8000`. It networks them seamlessly.
- **Kubernetes**: The `k8s/` directory contains standard manifests. To deploy:
  ```bash
  kubectl apply -f k8s/deployments.yaml
  kubectl apply -f k8s/services.yaml
  ```
  *(Note: You must push the Docker images to your registry and update the image tags in the YAML files before deploying to a real cluster).*

## 8. CI/CD Explanation
The GitHub Actions pipeline (`.github/workflows/ci.yml`) is triggered on pushes and pull requests to the `main` branch. It executes:
1. **Frontend**: Installs Node dependencies and builds the Vite project.
2. **Rust Backend**: Compiles the release binary using `cargo build --release`.
3. **Python Service**: Installs pip dependencies to check for resolution errors.
4. **Docker**: Runs `docker-compose build` to ensure all multi-stage Dockerfiles compile successfully.
