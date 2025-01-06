import chainlit as cl
from llms_graphs import neo4j_graph, InputState
from uuid import uuid4
from typing import Generator
from langchain_core.runnables import RunnableConfig

@cl.on_chat_start
async def home():
    image_schema = cl.Image(display="inline", path="network-schema-arrows.jpg", size="large")
    await cl.Message("Hola! Soy un sistema multiagente conectado a la base de datos orientada a grafos ___network-management___ de Neo4j. Aquí tienes el esquema de la base de datos", elements=[image_schema]).send()


@cl.on_message
async def on_message(message: cl.Message): 
    #create the initial state
    state = InputState(question=message.content)
    message_from_llm = cl.Message(content="")
    
    # let's stream it 
    async with cl.Step(name="Thinking") as step:
        for msg, metadata in await cl.make_async(stream_neo_graph)(state):
            if metadata["langgraph_node"] == "generate_cypher":
                step_name = "Generating Cypher query"
                if step.name != step_name:
                    step.name = step_name
                    await step.update()
                    await cl.sleep(0.001)
            elif metadata["langgraph_node"] == "execute_cypher":
                step_name = "Executing Cypher query"
                if step.name != step_name:
                    step.name = step_name
                    await step.update()
                    await cl.sleep(0.001)
            elif metadata["langgraph_node"]=="generate_final_answer":
                step_name = "Writing answer"
                if step.name != step_name:
                    step.name = step_name
                    await step.update()
                    await cl.sleep(0.001)
                await message_from_llm.stream_token(msg.content)
        await step.remove()
    await message_from_llm.send()

def stream_neo_graph(state) -> Generator:
    yield from neo4j_graph.stream(state, stream_mode="messages", config=RunnableConfig(configurable={"thread_id" : uuid4()}))