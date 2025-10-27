from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import httpx
import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

app = FastAPI(title="Brevo Email API")

# Request model
class EmailRequest(BaseModel):
    receiver_email: EmailStr
    subject: str
    body_text: str

@app.get("/")
def root():
    return {"message": "Brevo Email API is running"}

@app.post("/send-email")
def send_email(email_data: EmailRequest):
    brevo_api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL")
    print(brevo_api_key, sender_email)
    if not brevo_api_key or not sender_email:
        raise HTTPException(status_code=500, detail="API not configured properly")
    
    # Prepare Brevo request
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": brevo_api_key
    }
    
    payload = {
        "sender": {
            "name": os.getenv("SENDER_NAME", "Email Service"),
            "email": sender_email
        },
        "to": [{"email": email_data.receiver_email}],
        "subject": email_data.subject,
        "textContent": email_data.body_text
    }
    
    # Send request (synchronous)
    try:
        response = httpx.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            return {
                "message": "Email sent successfully",
                "message_id": response.json().get('messageId')
            }
        else:
            error_msg = response.json().get('message', 'Unknown error')
            raise HTTPException(status_code=400, detail=f"Brevo error: {error_msg}")
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)