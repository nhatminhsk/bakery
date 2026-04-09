from langchain_deepseek import ChatDeepSeek

def LLM(model_name="deepseek-chat", temperature=0.7, top_p=0.9):
    return ChatDeepSeek(model=model_name, temperature=temperature, top_p=top_p)