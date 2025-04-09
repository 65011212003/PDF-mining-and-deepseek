# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI
import sqlite3
from datetime import datetime

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

# Read the text file content
with open('ijms-22-11658.txt', 'r', encoding='utf-8') as f:
    text_content = f.read()

# Prepare the prompt to extract disease information
prompt = """
Please analyze this scientific text about rice diseases and extract comprehensive information in Thai language. Present the information in a clear, structured format with the following sections for each disease mentioned:

1. Disease Name (ชื่อโรค):
   - Scientific name (if available)
   - Common names
   
2. Symptoms (อาการ):
   - Detailed description of visual symptoms
   - Affected plant parts
   - Disease progression stages
   
3. Causes and Pathogens (สาเหตุและเชื้อก่อโรค):
   - Pathogen type (fungal, bacterial, viral)
   - Specific pathogen names
   - Environmental conditions favoring disease
   
4. Treatment Methods (วิธีการรักษา):
   - Chemical treatments
   - Biological controls
   - Cultural practices
   - Resistant rice varieties
   
5. Research Findings (ผลการวิจัย):
   - Key genetic resistance factors
   - Recent scientific breakthroughs
   - Future research directions

For each disease, include relevant citations from the text when available. Present the information in clear, concise bullet points.

Text to analyze:
""" + text_content  # No token limit with OpenRouter

response = client.chat.completions.create(
    extra_headers={
        "HTTP-Referer": "https://example.com",
        "X-Title": "Rice Disease Analysis",
    },
    extra_body={},
    model="deepseek/deepseek-chat-v3-0324:free",
    messages=[
        {"role": "system", "content": "คุณเป็นผู้ช่วยวิจัยที่สามารถสรุปและแยกข้อมูลทางวิทยาศาสตร์เกี่ยวกับโรคพืชเป็นภาษาไทยได้อย่างมีประสิทธิภาพ"},
        {"role": "user", "content": prompt},
    ],
    stream=False
)

ai_response = response.choices[0].message.content

# Save to database
conn = sqlite3.connect('pdf_extracts.db')
cursor = conn.cursor()
cursor.execute('''INSERT INTO pdf_data (filename, content, processed_at)
                  VALUES (?, ?, ?)''', 
               ('disease_analysis', ai_response, datetime.now()))
conn.commit()
conn.close()

print(ai_response)
