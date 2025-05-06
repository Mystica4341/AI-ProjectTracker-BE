from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from database import qdrant_client
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.converters import PyPDFToDocument
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator
from haystack.components.builders import PromptBuilder
from haystack import Document, Pipeline
from haystack.components.converters import DOCXToDocument
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from fastapi import APIRouter
from pydantic import BaseModel
from haystack.utils import Secret
from AI import Secret

router = APIRouter()

docs = [Document(content="Company's name is QNA Corps Ltd."),
    Document(content="QNA Corps Ltd. was established in 2000 with a vision to become a leading player in the technology sector. We are committed to providing our customers with high-quality products and services that meet their needs and exceed their expectations."),
    Document(content="• Short-term goals: Expand domestic market, improve product and service quality. • Long-term goals: Become a leading technology group in the ASEAN region."),
    Document(content="QNA Corps Ltd. is headquartered at 123 Tech Street, Quận 1, TP. Hồ Chí Minh, Việt Nam."),
    Document(content="The company has over 500 employees."),
    Document(content="QNA Corps Ltd. specializes in information technology, software development, and enterprise solutions."),
    Document(content="Vision: To become the symbol of technological innovation in Southeast Asia."),
    Document(content="Mission: Deliver superior technological value to customers, partners, and the community."),
    Document(content="Core values: 1. Innovation: Always innovate and continuously develop. 2. Quality: Committed to providing the best products and services. 3. Partnership: Building long-term connections with customers and partners."),
    Document(content="Products: 1. Enterprise Resource Planning (ERP) solutions. 2. Customer Relationship Management (CRM) applications. 3. Big Data analytics systems."),
    Document(content="Services: 1. Technology implementation consulting. 2. Technical support and maintenance. 3. Technology training for enterprises."),
    Document(content="Achievements: 1. Awarded 'Outstanding Technology Enterprise 2022' at the ASEAN Tech Awards. 2. Recognized as a Top 10 reputable technology company in Vietnam for 10 consecutive years."),
    Document(content="Strategic partners: Microsoft, AWS, Google Cloud, IBM, and leading ASEAN corporations such as VinGroup, Grab, and Petronas."),
    Document(content="Contact information: Email: support@qnacorps.com | Phone: +84 123 456 789 | Website: www.qnacorps.com.")
]

class Question(BaseModel):
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
generator = GoogleAIGeminiGenerator(model="gemini-2.0-flash", api_key=Secret.GeminiToken)

def pipelineAddData(idProject: int):
    # Initialize pipeline
    add_data_pipeline = Pipeline()
    # Add components to your pipeline

    add_data_pipeline.add_component("converter",PyPDFToDocument())
    add_data_pipeline.add_component("cleaner", DocumentCleaner(remove_empty_lines=False, remove_extra_whitespaces=False))
    add_data_pipeline.add_component("splitter", DocumentSplitter(split_by="passage", split_length=1))
    add_data_pipeline.add_component("embedder", embedderDoc())
    add_data_pipeline.add_component("writer", DocumentWriter(storeDocs(idProject)))

    # Now, connect the components to each other
    add_data_pipeline.connect("converter", "cleaner")
    add_data_pipeline.connect("cleaner", "splitter")
    add_data_pipeline.connect("splitter", "embedder")
    add_data_pipeline.connect("embedder", "writer")
    return add_data_pipeline

def pipelineAns(idProject: int):
    query_pipeline = Pipeline()
    #components
    query_pipeline.add_component("text_embedder",embedderText())
    query_pipeline.add_component("retriever", retriever(idProject))
    query_pipeline.add_component("prompt_builder", prompt_builder)
    query_pipeline.add_component("llm", generator)
    #connect
    query_pipeline.connect("text_embedder","retriever.query_embedding")
    query_pipeline.connect("retriever.documents","prompt_builder.documents")
    query_pipeline.connect("prompt_builder.prompt", "llm")
    return query_pipeline

def writeDoc(idProject: int):
    embeddedDocs = embedderDoc().run(docs)
    try:
        storeDocs(idProject).write_documents(embeddedDocs['documents'])
        print(' Documents wrote to the vectorDB Successfully')
    except Exception as e:
        print('Error: ', e)

# def uploadDocs():
#     return 0

@router.post("/ask")
async def ask(idProject: int, question: Question):
    createQdrant(idProject)
    response = pipelineAns(idProject).run({"text_embedder": {"text": question.query}, "prompt_builder": {"question": question.query}})
    return {
        "Answer": response["llm"]["replies"][0]
    }