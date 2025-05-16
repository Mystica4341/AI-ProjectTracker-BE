from qdrant_client.models import VectorParams, Distance
from database import qdrant_client
from qdrant_client.http import models
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.converters import PyPDFToDocument, DOCXToDocument
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.components.joiners import DocumentJoiner
from haystack.components.routers import FileTypeRouter
# from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import ChatPromptBuilder
from haystack import Pipeline
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from fastapi import APIRouter
from pydantic import BaseModel
from haystack.utils import Secret
from AI import Secret
import os
import requests

router = APIRouter()

class Question(BaseModel):
    idProject: int
    query: str

#initialize Qdrant db doc
def storeDocs(idProject: int):
    return QdrantDocumentStore(
        url="https://49e3e764-01cb-441e-8910-b4bcc220aa17.us-east-1-0.aws.cloud.qdrant.io:6333",
        api_key= Secret.QdrantToken,
        index="collection" + str(idProject),
        similarity="cosine",
        embedding_dim=768,
    )

def createQdrant(idProject: int):
    if not qdrant_client.collection_exists("collection" + str(idProject)):
        qdrant_client.create_collection(collection_name= "collection" + str(idProject),
                                        vectors_config=VectorParams(size=768, distance=Distance.COSINE))

def embedderDoc():
    embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/bert-base-nli-mean-tokens")
    embedder.warm_up()
    return embedder

def embedderText():
    embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/bert-base-nli-mean-tokens")
    embedder.warm_up()
    return embedder

def retriever(idProject: int):
    return QdrantEmbeddingRetriever(document_store=storeDocs(idProject))

# Maintain chat history
chat_history = {}

# Updated template to include conversation history
template = ChatMessage.from_system("""
Using the information contained in the context and the conversation history, provide a comprehensive and moderate answer for the Question.
Translate answer to vietnamese if the question is vietnamese and if possible.
Only provide an "[Url]: url of article" at bottom of the answer if meta section has the url else DO NOT provide.
If the answer is not in the context, try to find relevant information from the context and provide a comprehensive answer.
If the question is about a specific topic, provide a detailed answer based on the context. 
If the question is about a specific document, provide a summary of that document if required. 
If the question is about a specific organization, provide relevant information about that organization based on the context. 
If the question is about a specific product, provide relevant information about that product based on the context.
If the question is about analysis, provide a detailed analysis and recommendation based on the context. Finally, please suggest a better solution if possible.

Conversation History:
{% for message in history %}
    {{ message.role }}: {{ message.content }}
{% endfor %}

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{question}}
Answer:
""")

prompt_builder = ChatPromptBuilder(template=template, required_variables=["question"], variables=["history", "documents", "question"])
"""
Example of how to use the prompt builder

# prompt = prompt_builder.run(
#     question="What is the capital of France?",
#     history=[
#         ChatMessage.from_user("What is the capital of France?"),
#         ChatMessage.from_assistant("The capital of France is Paris."),
#         ChatMessage.from_user("What is the capital of Germany?")
#     ],
#     template=[template, ChatMessage.from_user("What is the capital of France?")]
# )["prompt"]
# print("Prompt Builder:", prompt)
"""

generator = GoogleAIGeminiChatGenerator(model="gemini-2.0-flash", api_key=Secret.GeminiToken)
"""
Example of how to use the generator

# response = generator.run(
#     messages = prompt,
# )
# print("Generator Response:", response["replies"][0].text)
# """
# generator = OpenAIGenerator(model="gpt-4", api_key=Secret.OpenAIToken)

# Initialize pipeline for adding data
add_data_pipeline = Pipeline()
def pipelineAddData(idProject: int):
    # Add components to your pipeline
    try:
        add_data_pipeline.add_component("file_router", FileTypeRouter(mime_types=["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]))
        add_data_pipeline.add_component("pdfconverter", PyPDFToDocument())
        add_data_pipeline.add_component("docxconverter", DOCXToDocument())
        add_data_pipeline.add_component("joiner", DocumentJoiner())
        add_data_pipeline.add_component("cleaner", DocumentCleaner(remove_empty_lines=True, remove_extra_whitespaces=True))
        add_data_pipeline.add_component("splitter", DocumentSplitter(split_by="word", split_length=500, split_overlap=10))
        add_data_pipeline.add_component("embedder", embedderDoc())
        add_data_pipeline.add_component("writer", DocumentWriter(storeDocs(idProject)))
    except Exception as e:
        print('Error: ', e)

    # Now, connect the components to each other
    add_data_pipeline.connect("file_router.application/pdf", "pdfconverter")
    add_data_pipeline.connect("file_router.application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docxconverter")
    add_data_pipeline.connect("pdfconverter", "joiner")
    add_data_pipeline.connect("docxconverter", "joiner")
    add_data_pipeline.connect("joiner", "cleaner")
    add_data_pipeline.connect("cleaner", "splitter")
    add_data_pipeline.connect("splitter", "embedder")
    add_data_pipeline.connect("embedder", "writer")
    return add_data_pipeline

# Initialize pipeline for answering questions
query_pipeline = Pipeline()
def pipelineAns(idProject: int):
    try:
        #components
        query_pipeline.add_component("text_embedder",embedderText())
        query_pipeline.add_component("retriever", retriever(idProject))
        query_pipeline.add_component("prompt_builder", prompt_builder)    
        query_pipeline.add_component("llm", generator)
    except Exception as e:
        print('Error: ', e)
    #connect
    query_pipeline.connect("text_embedder","retriever.query_embedding")
    query_pipeline.connect("retriever.documents","prompt_builder.documents")
    query_pipeline.connect("prompt_builder.prompt", "llm.messages")

    return query_pipeline

@router.post("/write-docs")
async def write_docs(idProject: int, file_url: str):

    """
    Endpoint to upload a DOCX or PDF file and write its content to the vector database.
    """
    createQdrant(idProject)
    response = requests.get(file_url)
    file_content = response.content
    # Check file type

    file_name = os.path.basename(file_url)
    with open(file_name, "wb") as temp_file:
        temp_file.write(file_content)
    # Read file content


    # Embed and write documents to the vector database
    pipelineAddData(idProject).run({"file_router": {"sources": [file_name]}})
    os.remove(file_name) 
    return {"message": "Documents successfully written to the vector database."}

# @router.post("delete-docs")
# def delete_docs(idProject: int, fileName: str):
#     """
#     Endpoint to delete all documents from the vector database.
#     """
#     try:
#         qdrant_client.delete("collection" + str(idProject), models.FilterSelector(filter = models.Filter(must=[models.FieldCondition(key="meta",match= models.MatchValue(value=fileName))])))
#         return {"message": "Documents successfully deleted from the vector database."}
#     except Exception as e:
#         print('Error: ', e)
#         return {"message": "Error deleting documents from the vector database."}

# messages = [template]

messages = [template]

@router.post("/ask")
def ask(question: Question):

    # Create Qdrant collection if it doesn't exist
    createQdrant(question.idProject)

    # Warm up the pipeline
    pipelineAns(question.idProject).warm_up()
    
    messages.append(ChatMessage.from_user(question.query))

    try:
        # Run the query pipeline with the chat history
        response = query_pipeline.run({
            "text_embedder": {"text": question.query},
            "prompt_builder": {
                "question": question.query,
                "history": [],
                "template": messages
            }, 
        })

        # Check if the response contains replies
        if "llm" in response and "replies" in response["llm"] and response["llm"]["replies"]:
            aiResponse = response["llm"]["replies"][0]
    except Exception as e:
        print(f"Error: {e}")
        aiResponse = f"{e}"
        
    # Append the AI response to the chat history
    messages.append(ChatMessage.from_assistant(aiResponse.text))

    return {
        "Answer": aiResponse.text,
        # "History": [{"role": msg.role, "content": msg.text} for msg in chat_history[question.idProject]]
    }