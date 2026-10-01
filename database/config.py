# Groq Model Configuration
# Update this file to change the LLM model used by the agent
# 
# Available models on Groq (check https://console.groq.com/docs/models):
# - openai/gpt-oss-120b
# - llama-3.2-90b-vision-preview
# - llama-3.2-11b-vision-preview
# - gemma-7b-it
# - gemma2-9b-it
#
# If your API key doesn't have access to a model, try a different one

MODEL = "openai/gpt-oss-120b"
TEMPERATURE = 0
TIMEOUT_SECONDS = 30
MAX_RETRIES = 1
