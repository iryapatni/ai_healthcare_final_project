use axum::{
    extract::Json,
    routing::post,
    Router,
};
use serde::{Deserialize, Serialize};
use std::env;
use tower_http::cors::{Any, CorsLayer};

#[derive(Deserialize, Serialize)]
struct PlanRequest {
    query: String,
}

#[derive(Serialize, Deserialize)]
struct PlanResponse {
    treatment_plan: String,
    insurance_suggestions: String,
    cost_estimation: String,
    schedule: String,
    infographic_url: Option<String>,
}

async fn generate_plan(Json(payload): Json<PlanRequest>) -> Result<Json<PlanResponse>, (axum::http::StatusCode, String)> {
    let python_service_url = env::var("AI_SERVICE_URL").unwrap_or_else(|_| "http://localhost:8000".to_string());
    
    let client = reqwest::Client::new();
    let res = client.post(&format!("{}/api/plan", python_service_url))
        .json(&payload)
        .send()
        .await
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    if res.status().is_success() {
        let plan: PlanResponse = res.json().await.map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
        Ok(Json(plan))
    } else {
        let status = res.status();
        let axum_status = axum::http::StatusCode::from_u16(status.as_u16()).unwrap_or(axum::http::StatusCode::INTERNAL_SERVER_ERROR);
        let error_text = res.text().await.unwrap_or_else(|_| "Unknown error".to_string());
        // Forward the exact status code from Python, and parse the JSON string as Axum's error string
        Err((axum_status, error_text))
    }
}

#[tokio::main]
async fn main() {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/api/generate-plan", post(generate_plan))
        .layer(cors);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();
    println!("Rust API Gateway running on port 8080");
    axum::serve(listener, app).await.unwrap();
}
