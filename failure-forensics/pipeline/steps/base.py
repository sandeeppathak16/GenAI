from abc import ABC
from typing import Type

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel


PIPELINE_PROMPTS = {
    "entity_extraction": """
            You are an expert information extraction system.

            Your task is to identify every meaningful entity mentioned in the document.

            An entity can represent any important concept, including but not limited to:
            - People
            - Organizations
            - Locations
            - Dates
            - Times
            - Monetary values
            - Products
            - Services
            - Invoice numbers
            - Contract IDs
            - Policies
            - Account numbers
            - Phone numbers
            - Email addresses
            - URLs
            - Technologies
            - Projects
            - Events
            - Medical terms
            - Legal references
            - Domain-specific concepts

            For each entity return:
            - type
            - value
            - confidence (1-5)

            Rules:
            - Extract only information explicitly present in the document.
            - Never hallucinate entities.
            - Preserve the original value exactly as written.
            - Return every important entity.
            - If no entities are found, return an empty list.
""",
    "classification": """
            You are an expert document classification system.

            Determine the most appropriate document type.

            Possible document types include (but are not limited to):
            - Invoice
            - Contract
            - Purchase Order
            - Resume
            - Medical Record
            - Legal Document
            - Research Paper
            - Technical Documentation
            - Report
            - Email
            - Letter
            - Receipt
            - Proposal
            - Policy
            - Bank Statement
            - Tax Document
            - Meeting Notes
            - User Manual
            - Correspondence
            - Other

            Return:
            - document_type
            - confidence (1-5)
            - reasoning

            Rules:
            - Base the decision on the complete document and extracted entities.
            - Choose the closest matching document type.
            - Do not hallucinate information.
            - Keep the reasoning to one concise sentence.
""",
    "summarization": """
        You are an expert document summarization system.

        Generate a concise, accurate, and factual summary.

        Use:
        - The original document
        - The extracted entities
        - The detected document type

        Guidelines:
        - Preserve all important facts.
        - Do not invent or infer missing information.
        - Mention important entities where appropriate.
        - Clearly describe the purpose of the document.
        - Keep the summary under 200 words.

        Return:
        - summary
        - confidence (1-5)
""",
}


class BasePipelineStep(ABC):

    MODEL = "llama-3.3-70b-versatile"

    step: str
    output_model: Type[BaseModel]

    def __init__(self):
        self.llm = ChatGroq(
            model=self.MODEL,
            temperature=0,
        ).with_structured_output(self.output_model)

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.step),
                ("human", "{input}"),
            ]
        )

        self.chain = self.prompt | self.llm

    async def invoke(self, **kwargs):
        return await self.chain.ainvoke(
            {
                "input": self.build_input(**kwargs),
            }
        )

    def build_input(self, **kwargs) -> str:
        raise NotImplementedError