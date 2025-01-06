from langchain_neo4j import Neo4jGraph

enhanced_graph = Neo4jGraph(enhanced_schema=True)

from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_neo4j import Neo4jVector
from langchain_openai import OpenAIEmbeddings

examples = [
    {
        "question": "What is the network topology of the DataCenter in Reykjavik?",
        "query": "MATCH network = (dc:DataCenter {name:'DC1', location:'Iceland, Reykjavik'})-[:CONTAINS]->(:Router)-[:ROUTES]->(:Interface) RETURN network;"
    },
    {
        "question": "How many zones does the DataCenter contain?",
        "query": "MATCH (dc:DataCenter {name:'DC1'})-[:CONTAINS]->(:Router)-[:ROUTES]->(:Interface)-[:CONNECTS]->(nr:Network:Zone) RETURN COUNT(nr) AS zoneCount;"
    },
    {
        "question": "List the racks and their corresponding switches in each zone.",
        "query": "MATCH (dc:DataCenter {name:'DC1'})-[:CONTAINS]->(rack:Rack)-[:HOLDS]->(s:Switch) RETURN rack.name AS Rack, s.name AS Switch;"
    },
    {
        "question": "Which machines are in Rack DC1-RCK-2-1 and their types?",
        "query": "MATCH (r:Rack {name:'DC1-RCK-2-1'})-[:HOLDS]->(m:Machine)-[:TYPE]->(type:Type) RETURN r.name AS Rack, type.name AS MachineType, COUNT(m) AS MachineCount;"
    },
    {
        "question": "What is the total compute power of the DataCenter?",
        "query": "MATCH (m:Machine)-[:TYPE]->(type:Type) RETURN SUM(type.cpu) AS TotalCPUs, SUM(type.ram) AS TotalRAM, SUM(type.disk) AS TotalDisk;"
    },
    {
        "question": "Find all connections between interfaces and their data transfer volumes.",
        "query": "MATCH (source:Interface)-[con:CONNECTIONS]->(target:Interface) RETURN source.ip AS SourceIP, target.ip AS TargetIP, SUM(con.volume) AS TotalVolume;"
    },
    {
        "question": "What are the software dependencies for the service running Neo4j?",
        "query": "MATCH (s:Software)-[:DEPENDS_ON]->(nv:Version)<-[:VERSION]-(n:Software:Service {name:'neo4j'}) RETURN s.name AS Software, nv.name AS Version;"
    },
    {
        "question": "Which machines need an OS update for Debian 8-Jessie?",
        "query": "MATCH (os:OS:Software)-[:VERSION]->(newVersion) WHERE os.name = 'Debian' AND newVersion.name = '8-Jessie' MATCH (m:Machine)-[:RUNS]->(:OS:Process)-[:INSTANCE]->(currentVersion) WHERE (currentVersion)<-[:PREVIOUS*]-(newVersion) RETURN m.name AS Machine;"
    }
]


example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples, OpenAIEmbeddings(), Neo4jVector, k=5, input_keys=["question"]
)