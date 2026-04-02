from google import genai
from config.settings import Settings, get_settings

settings = get_settings()

client = genai.Client(api_key=settings.GEMINI_API_KEY)

#gemma-4-26b-a4b-it gemini-3-flash-preview

def generate_commit_message(diff: str) -> str:
    response = client.models.generate_content(
        model="gemma-4-26b-a4b-it", contents=f"""
        You are a senior software developer. Analyze the 'git diff' output provided below
        and write a short, single-line commit message following Conventional Commits rules
        (feat, fix, refactor, chore, docs, etc.).
        
        IMPORTANT RULES:
        1. Return only the commit message.
        2. Do not add any extra explanations like "Hello, here is your message".
        3. The message should be in English.
        
        Here is the git diff output:
        {diff}
        """
    )
    return response.text