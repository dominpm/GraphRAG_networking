from langchain_core.output_parsers import StrOutputParser
from typing import Literal, Optional, List
from langchain_openai import ChatOpenAI
from .prompts import guardrails_prompt, text2cypher_prompt, generate_final_prompt
from pydantic import BaseModel, Field
from .neo4j import enhanced_graph

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.05)

class GuardrailsOutput(BaseModel):
    decision: Literal["network", "end"] = Field(
        description="Decision on whether the question is related to networking"
    )

guardrails_chain = guardrails_prompt | llm.with_structured_output(GuardrailsOutput)

text2cypher_chain = text2cypher_prompt | llm | StrOutputParser()

generate_final_chain = generate_final_prompt | llm | StrOutputParser()