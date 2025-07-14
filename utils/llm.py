import streamlit as st
import openai
import asyncio
from typing import Optional
import time

@st.cache_resource
def init_openai_client():
    """Initialize OpenAI client with API key from secrets"""
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
        return openai.OpenAI(api_key=api_key)
    except Exception as e:
        st.error("Please configure your OpenAI API key in .streamlit/secrets.toml")
        return None

async def get_ai_response_async(prompt: str, user_context: str, system_prompt: str):
    """Asynchronous function to get AI response"""
    client = init_openai_client()
    if not client:
        return "AI recommendations unavailable. Please configure API key."
    
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {user_context}\n\nRequest: {prompt}"}
            ],
            max_tokens=800,
            temperature=0.7,
            stream=True
        )
        return response
    except Exception as e:
        return f"Error generating AI recommendations: {str(e)}"

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_ai_recommendations_cached(prompt_hash: str, prompt: str, user_context: str, system_prompt: str):
    """Cached version of AI recommendations"""
    client = init_openai_client()
    if not client:
        return "AI recommendations unavailable. Please configure API key."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {user_context}\n\nRequest: {prompt}"}
            ],
            max_tokens=800,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating AI recommendations: {str(e)}"

def stream_response(response_generator):
    """Stream response token by token"""
    full_response = ""
    for chunk in response_generator:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
            yield chunk.choices[0].delta.content
    return full_response