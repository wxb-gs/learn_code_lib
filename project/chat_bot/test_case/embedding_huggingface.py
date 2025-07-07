# pip install llama-index-embeddings-huggingface
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(model_name="../app/models/bge-m3")
print(embed_model.get_query_embedding("hello world"))