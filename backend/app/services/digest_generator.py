import openai
from typing import Dict, List
import re
def generate_digest(industry_data: Dict[str, List[Dict]]) -> Dict[str, Dict]:
    digests = {}
    
    for industry, emails in industry_data.items():
        if not emails:
            continue
        email_info = []
        for email in emails:
            email_info.append(f"""
Subject: {email['subject']}
From: {email['sender']}
Content: {email['content'][:500]}  # Limit content length for each email
---""")
            
        # Create the prompt
        prompt = f"""Comprehensive Email Digest Analysis for {len(emails)} Emails in the {industry} Industry

Objective: Generate a multi-point digest that breaks down key insights using a structured format. Each significant finding or trend should be presented with a clear subject and detailed content explanation.

ANALYSIS REQUIREMENTS:

DELIVERABLE FORMAT:
For each major insight, you MUST use the following XML structure:

<SUBJECT>First Key Trend/Insight Headline</SUBJECT>
<CONTENT>
- Detailed explanation of the trend
- Specific evidence from email communications
- Potential strategic implications
- Quantitative or qualitative supporting data
</CONTENT>

<SUBJECT>Second Key Trend/Insight Headline</SUBJECT>
<CONTENT>
- Comprehensive breakdown of the trend
- Contextual analysis within the {industry}
- Specific email-derived observations
- Potential action items or recommendations
</CONTENT>

<SUBJECT>Third Key Trend/Insight Headline</SUBJECT>
<CONTENT>
- In-depth exploration of the identified trend
- Cross-referencing multiple email sources
- Impact assessment
- Forward-looking strategic guidance
</CONTENT>

GUIDELINES:
- Generate at least 3 distinct <SUBJECT> and <CONTENT> pairs
- Maximum of 5 insights to maintain focus
- Ensure each insight is unique and substantive
- Prioritize trends with the highest strategic value
- Use clear, concise language
- Avoid redundancy between insights

OPTIONAL SECTIONS:
If critical insights emerge, additional <SUBJECT> and <CONTENT> pairs can be added to capture:
- Emerging market signals
- Potential disruptions
- Collaboration opportunities
- Significant communication patterns

CONFIDENTIALITY: Treat all derived insights with professional discretion."""

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise email digests."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            subject_pattern = r"<SUBJECT>\s*(.*?)\s*</SUBJECT>"
            content_pattern = r"<CONTENT>\s*(.*?)\s*</CONTENT>"
            digest_content = response.choices[0].message.content

            subjects = re.findall(subject_pattern, digest_content, re.DOTALL | re.IGNORECASE)
            contents = re.findall(content_pattern, digest_content, re.DOTALL | re.IGNORECASE)
            
            result = []
            for i in range(max(len(subjects), len(contents))):
                subject = subjects[i] if i < len(subjects) else "Untitled Subject"
                content = contents[i] if i < len(contents) else "No content available"
                
                # Clean up whitespace and newlines
                subject = re.sub(r'\s+', ' ', subject).strip()
                content = re.sub(r'\s+', ' ', content).strip()
                
                result.append({
                    "subject": subject,
                    "content": content
                })
            print(result)
            # Store digest with email references and metadata
            digests[industry] = {
                'content': result,
                'email_count': len(emails),
                'sources': [{'subject': e['subject'], 'sender': e['sender']} for e in emails]
            }
            
        except Exception as e:
            print(f"Error generating digest for {industry}: {e}")
            digests[industry] = {
                'content': f"Error generating digest for {industry}",
                'email_count': len(emails),
                'sources': [{'subject': e['subject'], 'sender': e['sender']} for e in emails]
            }
    
    return digests
