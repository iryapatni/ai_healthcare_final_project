from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(title="AI Healthcare Insurance Planner")

class PlanRequest(BaseModel):
    query: str

class PlanResponse(BaseModel):
    treatment_plan: str
    insurance_suggestions: str
    cost_estimation: str
    schedule: str
    infographic_url: Optional[str] = None

import urllib.parse

def generate_image(prompt: str) -> str:
    # Highly curated, premium healthcare images that are guaranteed to load
    premium_images = [
        "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1024&q=80",
        "https://images.unsplash.com/photo-1530497610245-94d3c16cda28?w=1024&q=80",
        "https://images.unsplash.com/photo-1551076805-e1869043e560?w=1024&q=80",
        "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=1024&q=80",
        "https://images.unsplash.com/photo-1584982751601-97d8cb0f3080?w=1024&q=80",
        "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=1024&q=80",
        "https://images.unsplash.com/photo-1527613426441-4da17471b66d?w=1024&q=80",
        "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=1024&q=80",
        "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=1024&q=80",
        "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=1024&q=80",
        "https://images.unsplash.com/photo-1583324113626-70df0f4deaab?w=1024&q=80",
        "https://images.unsplash.com/photo-1551076805-e1869043e560?w=1024&q=80",
        "https://images.unsplash.com/photo-1666214280557-f1b5022eb634?w=1024&q=80",
        "https://images.unsplash.com/photo-1504813184591-01572f98c85f?w=1024&q=80",
        "https://images.unsplash.com/photo-1512678080530-7760d81faba6?w=1024&q=80"
    ]
    # Create a simple hash from the prompt to consistently select an image for the same query
    hash_val = sum(ord(c) for c in prompt)
    index = hash_val % len(premium_images)
    return premium_images[index]

@app.post("/api/plan", response_model=PlanResponse)
def generate_healthcare_plan(request: PlanRequest):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="ERROR: GOOGLE_API_KEY is missing! You must provide a valid Gemini API Key in your environment or docker-compose.yml to generate real, dynamic plans.")
    
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import PromptTemplate
    
    llm = ChatGoogleGenerativeAI(temperature=0.2, model="gemini-2.5-flash", google_api_key=api_key)
    
    prompt = PromptTemplate(
        input_variables=["query"],
        template='''You are an AI Healthcare and Insurance Planner. 
        A user has requested: '{query}'.
        Provide a CONCISE, PROFESSIONAL, and WELL-STRUCTURED response strictly in JSON format with these exact keys:
        - "treatment_plan": A concise medical/treatment approach. Provide 1-2 short paragraphs. Use bullet points for readability.
        - "insurance_suggestions": Recommended insurance plans available in India and exactly why they fit. Provide 1-2 short paragraphs.
        - "cost_estimation": Estimated costs strictly in Indian Rupees (INR) (e.g. ₹50,000 - ₹1,00,000). Breakdown the costs in a few concise lines.
        - "schedule": A highly specific daily and weekly health schedule. MUST be a single formatted STRING, not a nested object. Keep it brief and well-formatted.
        
        OUTPUT RAW VALID JSON ONLY. Do NOT include ```json markdown blocks or any other text before or after the JSON.
        '''
    )
    
    try:
        chain = prompt | llm
        response_msg = chain.invoke({"query": request.query})
        content = response_msg.content.strip()
        
        # Robust JSON extraction using regex
        import re
        import json
        
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            cleaned_content = json_match.group(0)
        else:
            cleaned_content = content
            
        try:
            data = json.loads(cleaned_content)
        except Exception:
            # Fallback if JSON is still invalid
            data = {
                "treatment_plan": content,
                "insurance_suggestions": "Please consult a professional for insurance details based on this plan.",
                "cost_estimation": "Costs depend on the specific medical approach and coverage.",
                "schedule": "Please follow up with your doctor for a specific schedule."
            }
        
        image_prompt = request.query
        image_url = generate_image(image_prompt)
        
        # Ensure schedule is a formatted string, not a dumped dictionary
        schedule_data = data.get("schedule", "N/A")
        if isinstance(schedule_data, dict):
            schedule_str = ""
            for k, v in schedule_data.items():
                schedule_str += f"**{str(k).capitalize()}**:\n"
                if isinstance(v, list):
                    for item in v:
                        schedule_str += f"• {item}\n"
                else:
                    schedule_str += f"• {v}\n"
                schedule_str += "\n"
            schedule_data = schedule_str.strip()
        else:
            schedule_data = str(schedule_data)
        
        return PlanResponse(
            treatment_plan=str(data.get("treatment_plan", "N/A")),
            insurance_suggestions=str(data.get("insurance_suggestions", "N/A")),
            cost_estimation=str(data.get("cost_estimation", "N/A")),
            schedule=schedule_data,
            infographic_url=image_url
        )
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        if "429" in error_msg or "Quota exceeded" in error_msg:
            raise HTTPException(status_code=429, detail="Google API Quota Exceeded. You have hit the 5 requests/minute limit on your free-tier key. Please wait a few seconds before generating another plan!")
        raise HTTPException(status_code=500, detail=f"Failed to generate plan: {error_msg}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
