from typing import List, Dict
import re
import os
from mistralai import Mistral
import os
import time
print("Mistral API Key:", os.environ.get("MISTRAL_API_KEY"))
# Initialize Mistral client
client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))

def classify_email(email: Dict, target_industries: List[str]) -> str:
    try:
        # Prepare the prompt
        industries_str = ", ".join(target_industries)
        prompt = f"""Given the following email, classify it into one of these industries: {industries_str}.
        Wrap your classification with the tags <INDUSTRY></INDUSTRY>. YOU MUST DO THIS OR I WILL BE VERY MAD.
        Make sure the industry classification is one of the following: {industries_str} fail to classify it into
        this list and I WILL ALSO BE VERY MAD.
        
        Subject: {email['subject']}
        Content: {email['content'][:1000]}  # Limit content length
        
        Industry:"""
        response = client.chat.complete(model="mistral-small-latest", messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that classifies emails into industries."
            },
            {
                "content": prompt,
                "role": "user",
            },
        ], stream=False)
        industry = response.choices[0].message.content.strip()
        pattern = r"<INDUSTRY>(.*?)</INDUSTRY>"
        match = re.search(pattern, industry)
        if match:
            industry = match.group(1)
            print("Industry identified: ", industry)
            return industry if industry in target_industries else 'Other'
        return 'Other'
        
    except Exception as e:
        print(f"Error classifying email: {e}")
        return 'Other'

def process_emails(emails: List[Dict], target_industries: List[str]) -> Dict[str, List[Dict]]:
    industry_groups = {industry: [] for industry in target_industries}
    industry_groups['Other'] = []  # Add 'Other' category
    count = 0
    for email in emails:
        industry = classify_email(email, target_industries)
        industry_groups[industry].append({
            'content': email.get('content', ''),
            'subject': email.get('subject', 'No Subject'),
            'sender': email.get('sender', 'Unknown'),
            'timestamp': email.get('timestamp'),
            'identifier': email.get('identifier')
        })
        wait_time = 0.4
        if count == 3:
            wait_time=1
            count = 0
        time.sleep(wait_time)
    
    return industry_groups