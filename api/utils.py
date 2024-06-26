from django.conf import settings
from pathlib import Path
import nest_asyncio

# API KEYS
LLAMA_CLOUD_API_KEY = settings.LLAMA_CLOUD_API_KEY
OPENAI_API_KEY = settings.OPENAI_API_KEY

# SETUP
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# TWO remote reader options
# from llama_index.readers.remote import RemoteReader
from llama_index.readers.remote_depth import RemoteDepthReader

nest_asyncio.apply()
llm = OpenAI(model="gpt-3.5-turbo", temperature=0)
node_parser = MarkdownElementNodeParser(
    llm=OpenAI(model="gpt-3.5-turbo"), num_workers=8
)
Settings.llm = llm
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
remote_loader = RemoteDepthReader(depth=0)

# Check parser
parser = LlamaParse(result_type="markdown")

# PYDANTIC
from pydantic import BaseModel, Field
from typing import List
from typing_extensions import TypedDict
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.core import ChatPromptTemplate
from llama_index.core.llms import ChatMessage


class StudySession(BaseModel):
    """Data model for a study session."""

    description: str = Field(
        description="High-level summary of the given requirement for the session"
    )
    cards: List[TypedDict("cards", {"question": str, "answer": str})] = Field(
        description="The questions and answers list of JSON objects from the study session"
    )


session_prompt = ChatPromptTemplate(
    message_templates=[
        ChatMessage(
            role="system",
            content=(
                "You are an expert assitant for formatting the structure of a study session with a description and a list of JSON objects called cards"
            ),
        ),
        ChatMessage(
            role="user",
            content=(
                "Here is the input I want you to format: \n"
                "------\n"
                "{input}\n"
                "------"
            ),
        ),
    ]
)


program = OpenAIPydanticProgram.from_defaults(
    output_cls=StudySession,
    llm=llm,
    prompt=session_prompt,
    verbose=True,
)


# PROMPT ROLES AND MODEL
def get_cards_from_need(requirement):
    assistant_role = """You are a helpful teaching assistant from which students seek help to create studying material.
    You will be provided with a document and you need to create a JSON object which looks like such based on the requirement provided:

    {
        "description": A one or two word description about the document just to identify it,
        "cards": [
        {"question": A question about specific keywords mentioned in the document, "answer": The answer to that question},
        {"question": A question about specific keywords mentioned in the document, "answer": The answer to that question},
        {"question": A question about specific keywords mentioned in the document, "answer": The answer to that question},
        {"question": A question about specific keywords mentioned in the document, "answer": The answer to that question},
        {"question": A question about specific keywords mentioned in the document, "answer": The answer to that question},
        {"question": A question about specific keywords mentioned in the document, "answer": The answer to that question},
        {"question": A question about specific keywords mentioned in the document, "answer": The answer to that question},
        {"question": A question about specific keywords mentioned in the document, "answer": The answer to that question},
        {"question": A question about specific keywords mentioned in the document, "answer": The answer to that question},
        {"question": A question about specific keywords mentioned in the document, "answer": The answer to that question},
        ]
    }

    You must create 10 of those question:answer JSON objects but make sure to return them in a list format inside the global JSON object.
    It is imperative you make only 10 of those question:answer JSON card objects. Remember, take your time to analyze the document 
    before creating the questions which help students memorize the most. You need to target keywords that appear in the document. 
    This means that students seek to memorize the terms appearing in the document so make sure to focus your questions and answers 
    around specific terms, processes, keywords, initials, and so on.

    Make sure to ignore any information in regards to the authors, submission details, webpages, and contact information from the authors.
    You are only interested in specific terms, keywords, and processes that have to do with the field of the paper.

    Respond with only theJSON pbject and do not add any comment, explanation or further details for it.
    You only need to return the JSON object, with the description and the list of questions and answers and nothing more.
    You will be penalized otherwise for returning more than just the object.

    To help you look for specific areas of the document you will be analyzing, you will receive a brief description provided by the
    student in which it will specify the area of interest for the study session. Make sure to pay close attention to that description
    so that you can look after the information mentioned in the document.
    Make sure to construct the questions and answers around that specific area which the student mentions in the description you will be provided.
    The student´s description will be delimited by triple backticks.
    """
    summary = f"""Considering your role: {assistant_role}, generate the desired response focusing on the need of the student: ```{requirement}```"""
    return summary


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def cardify_pdf(remote_url, requirement):
    """
    Retrieves a remote url and feeds it to LlamaParse and generates the JSON object we need for each pdf
    """
    documents = remote_loader.load_data(url=remote_url)
    nodes = node_parser.get_nodes_from_documents(documents)
    base_nodes, objects = node_parser.get_nodes_and_objects(nodes)
    index = VectorStoreIndex(nodes=base_nodes + objects)
    recursive_query_engine = index.as_query_engine(similarity_top_k=15, verbose=False)
    response = recursive_query_engine.query(get_cards_from_need(requirement))
    raw_pydantic = program(input=response)
    output = raw_pydantic.model_dump()
    return output
