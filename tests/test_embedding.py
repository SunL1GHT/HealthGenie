import os
import openai

from langchain.embeddings.openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    openai_api_base="http://127.0.0.1:10001/v1",
    openai_api_key="EMPTY"
)
text = "This is a test query."
query_result = embeddings.embed_query(text)
print(query_result)
