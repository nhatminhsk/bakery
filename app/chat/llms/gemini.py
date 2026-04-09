from langchain_google_genai import ChatGoogleGenerativeAI

def LLM(model_name="gemini-3-flash-preview", temperature=0.7, top_p=0.9):
    return ChatGoogleGenerativeAI(model=model_name, temperature=temperature, top_p=top_p)