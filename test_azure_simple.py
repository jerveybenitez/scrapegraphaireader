import os
os.environ["OPENAI_API_VERSION"] = "2024-02-15-preview"

from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="your_api_key_here", # Replace with your Azure OpenAI API key
    api_version="2024-02-15-preview",
    azure_endpoint="https://sg-strategic-marketing-resource.services.ai.azure.com/openai/v1/"
)

try:
    response = client.chat.completions.create(
        model="gpt-5.4-pro",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("✅ Success!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"❌ Error: {e}")