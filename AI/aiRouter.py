from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from database import qdrant_client
from datasets import load_dataset
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack.components.embedders import HuggingFaceAPIDocumentEmbedder, HuggingFaceAPITextEmbedder
from haystack.components.converters import PyPDFToDocument
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator
from haystack.components.builders import PromptBuilder
from haystack import Pipeline
from haystack.components.converters import DOCXToDocument
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from fastapi import APIRouter

router = APIRouter()

#initialize Qdrant db doc
def storeDocs(idProject: str):
    return QdrantDocumentStore(
        url= "49e3e764-01cb-441e-8910-b4bcc220aa17.us-east-1-0.aws.cloud.qdrant.io:6333", 
        api_key='P7gRj69HTdm-k4TYChSo-KWyXoUDuYI4Jf3II4qRg-zqJKaE0IytLw',                                                             
        index="collection" + idProject,                                                          
        similarity="cosine",                                                            
        embedding_dim=768,                                                              
    )

def createQdrant(idProject: str):
    if not qdrant_client.collection_exists("collection" + idProject):
        qdrant_client.create_collection(collection_name= "collection" + idProject,
                                        vectors_config=VectorParams(size=768, distance=Distance.COSINE))

def embedderDoc():
    return HuggingFaceAPIDocumentEmbedder(api_type="serverless_inference_api",
                                    api_params={"model": "sentence-transformers/bert-base-nli-mean-tokens"},
                                    token='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')

def embedderText():
    return HuggingFaceAPITextEmbedder(api_type="serverless_inference_api",
                                    api_params={"model": "sentence-transformers/bert-base-nli-mean-tokens"},
                                    token='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')

def retriever(idProject: str):
    return QdrantEmbeddingRetriever(storeDocs(idProject))

def genAnswer():
    template = """
    Using the information contained in the context that match with the Question, provide a comprehensive and moderate answer for the Question.
    Translate answer if possible
    Only provide an "[Url]: url of article" at bottom of the answer if meta section has the url else DO NOT provide

    Context:
    {% for document in documents %}
        {{ document.content }}
    {% endfor %}

    Question: {{question}}
    Answer:
    """
    prompt_builder = PromptBuilder(template=template)
    generator = GoogleAIGeminiGenerator(model="gemini-pro", api_key="AIzaSyCjDrnrO_gxtKV6873eotq35attC82y7ZA")
    return prompt_builder,generator

def pipelineAddData():
    # Initialize pipeline
    add_data_pipeline = Pipeline()
    # Add components to your pipeline
    add_data_pipeline.add_component("converter", DOCXToDocument())
    add_data_pipeline.add_component("converter",PyPDFToDocument())
    add_data_pipeline.add_component("cleaner", DocumentCleaner(remove_empty_lines=False, remove_extra_whitespaces=False))
    add_data_pipeline.add_component("splitter", DocumentSplitter(split_by="passage", split_length=1))
    add_data_pipeline.add_component("embedder", embedderDoc())
    add_data_pipeline.add_component("writer", DocumentWriter(storeDocs()))

    # Now, connect the components to each other
    add_data_pipeline.connect("converter", "cleaner")
    add_data_pipeline.connect("cleaner", "splitter")
    add_data_pipeline.connect("splitter", "embedder")
    add_data_pipeline.connect("embedder", "writer")
    return add_data_pipeline

def pipelineAns(idProject: str):
    query_pipeline = Pipeline()
    #components
    query_pipeline.add_component("text_embedder",embedderText())
    query_pipeline.add_component("retriever", retriever(idProject))
    query_pipeline.add_component("prompt_builder", genAnswer[0])
    query_pipeline.add_component("llm",genAnswer[1])
    #connect
    query_pipeline.connect("text_embedder","retriever.query_embedding")
    query_pipeline.connect("retriever.documents","prompt_builder.documents")
    query_pipeline.connect("prompt_builder.prompt", "llm")
    return query_pipeline

def writeDoc(docs):
    try:
        pipelineAddData().run({"converter" : {"sources": [docs] , "meta" : {"file_name": [docs]}}})
        print(' Documents wrote to the vectorDB Successfully')
    except Exception as e:
        print('Error: ', e)

# def uploadDocs():
#     return 0

@router.post("/ask")
async def qa(idProject: str):
    question = input("Your question: ")
    response = pipelineAns(idProject).run({"text_embedder": {"text": question}, "prompt_builder": {"question": question}})
    return {
        "Answer": response["llm"]["replies"][0]
    }