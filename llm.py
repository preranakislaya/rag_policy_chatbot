from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def build_prompt(context, query):

    prompt = f'''
    You are a helpful AI assistant.
    Answer ONLY from the provided context.
    If the answer is unavailable, say:
    "I could not find this information in the uploaded documents."

    Context: {context}
    Question: {query}
    '''
    return prompt

def ask_llm(prompt):

    response = client.chat.completions.create(
        model = 'llama-3.3-70b-versatile',
        messages = [{'role': 'user', 'content': prompt}],
        temperature = 0.2
    )

    reply = response.choices[0].message.content
    return reply

