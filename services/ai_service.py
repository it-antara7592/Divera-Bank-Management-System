import os
import re
from google import genai
from google.genai import errors

class AIService:
    @staticmethod
    def anonymize_data(text: str) -> str:
        #Strips any potential sensitive strings or PII, leaving only aggregate counts.
        text = re.sub(r'CUST-\d{4}-\d+', 'CUST-YYYY-######', text)
        text = re.sub(r'ACC-\d+', 'ACC-#####', text)
        text = re.sub(r'([a-zA-Z0-9_.+-])[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', r'\1***@\2', text)
        text = re.sub(r'\b\d{10}\b', '##########', text)
        return text

    @staticmethod
    def generate_banking_insights(metrics_summary: str) -> dict:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            error_msg = "⚠️ Error: GEMINI_API_KEY is missing from your .env file."
            return {"short": error_msg, "full": error_msg}

        try:
            client = genai.Client(api_key=api_key)
            
            prompt = (
                f"You are an AI banking assistant for Divera Bank (a CRUD-based administrative portal). "
                f"Analyze these operational metrics and database counts:\n{metrics_summary}\n\n"
                f"Provide your response separated into two clear parts using these exact tags:\n"
                f"[SHORT_SUMMARY]\n"
                f"(Provide a concise, precise 3-4 line narrative interpreting what these counts mean for daily banking operations)\n\n"
                f"[FULL_REPORT]\n"
                f"(Provide a comprehensive executive breakdown report with structured analysis, operational health, and administrative notes)"
            )

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            
            text = response.text
            short_summary = "No short summary available."
            full_report = text

            if "[SHORT_SUMMARY]" in text and "[FULL_REPORT]" in text:
                parts = text.split("[FULL_REPORT]")
                short_summary = parts[0].replace("[SHORT_SUMMARY]", "").strip()
                full_report = parts[1].strip()

            return {"short": short_summary, "full": full_report}
            
        except errors.APIError as e:
            err = f"❌ Gemini API Error: {e.message}"
            return {"short": err, "full": err}
        except Exception as e:
            err = f"❌ Unexpected Error: {str(e)}"
            return {"short": err, "full": err}