from langchain_core.output_parsers import StrOutputParser
from typing import Literal, Optional, List
from langchain_openai import ChatOpenAI
from .prompts import guardrails_prompt, text2cypher_prompt, validate_cypher_prompt, correct_cypher_prompt, generate_final_prompt
from pydantic import BaseModel, Field
from .neo4j import enhanced_graph

llm = ChatOpenAI(model="gpt-4o", temperature=0)

# from langchain_neo4j import GraphCypherQAChain
# chain = GraphCypherQAChain.from_llm(
#     graph=enhanced_graph, llm=llm, verbose=True, allow_dangerous_requests=True
# )

class GuardrailsOutput(BaseModel):
    decision: Literal["network", "end"] = Field(
        description="Decision on whether the question is related to networking"
    )

guardrails_chain = guardrails_prompt | llm.with_structured_output(GuardrailsOutput)

text2cypher_chain = text2cypher_prompt | llm | StrOutputParser()

class Property(BaseModel):
    """
    Represents a filter condition based on a specific node property in a graph in a Cypher statement.
    """

    node_label: str = Field(
        description="The label of the node to which this property belongs."
    )
    property_key: str = Field(description="The key of the property being filtered.")
    property_value: str = Field(
        description="The value that the property is being matched against."
    )

class ValidateCypherOutput(BaseModel):
    """
    Represents the validation result of a Cypher query's output,
    including any errors and applied filters.
    """

    errors: Optional[List[str]] = Field(
        description="A list of syntax or semantical errors in the Cypher statement. Always explain the discrepancy between schema and Cypher statement"
    )
    filters: Optional[List[Property]] = Field(
        description="A list of property-based filters applied in the Cypher statement."
    )


validate_cypher_chain = validate_cypher_prompt | llm.with_structured_output(
    ValidateCypherOutput
)

from langchain_neo4j.chains.graph_qa.cypher_utils import CypherQueryCorrector, Schema

corrector_schema = [
    Schema(el["start"], el["type"], el["end"])
    for el in enhanced_graph.structured_schema.get("relationships")
]
cypher_query_corrector = CypherQueryCorrector(corrector_schema)

correct_cypher_chain = correct_cypher_prompt | llm | StrOutputParser()

generate_final_chain = generate_final_prompt | llm | StrOutputParser()