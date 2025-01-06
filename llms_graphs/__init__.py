from dotenv import load_dotenv
load_dotenv()
from .states import InputState, OutputState, OverallState
from .nodes import guardrails, generate_cypher, execute_cypher, generate_final_answer
from .routers import guardrails_condition 
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver


neo4j_graph_builder = StateGraph(OverallState, input=InputState, output=OutputState)
neo4j_graph_builder.add_node(guardrails)
neo4j_graph_builder.add_node(generate_cypher)
neo4j_graph_builder.add_node(execute_cypher)
neo4j_graph_builder.add_node(generate_final_answer)

neo4j_graph_builder.add_edge(START, "guardrails")
neo4j_graph_builder.add_conditional_edges(
    "guardrails",
    guardrails_condition,
)
neo4j_graph_builder.add_edge("generate_cypher", "execute_cypher")
neo4j_graph_builder.add_edge("execute_cypher", "generate_final_answer")
neo4j_graph_builder.add_edge("generate_final_answer", END)

checkpointer = MemorySaver()
neo4j_graph = neo4j_graph_builder.compile(checkpointer=checkpointer)

# Let's visualize the graph 
neo4j_graph.get_graph().draw_mermaid_png(output_file_path="neo4j_graph.png")