import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from core.config import settings

os.environ["HF_TOKEN"] = settings.hf_token

embeddings = HuggingFaceEmbeddings(
    model="all-MiniLM-L6-v2", encode_kwargs={"normalize_embeddings": True}
)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=settings.groq_api_key,
    temperature=0,
)
