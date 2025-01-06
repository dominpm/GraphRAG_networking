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
        "query": "MATCH (dc:DataCenter {name:'DC1'})-[:CONTAINS]->(:Router)-[:ROUTES]->(:Interface)-[:CONNECTS]->(nr:NetworkZone) RETURN COUNT(nr) AS zoneCount;"
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
        "query": "MATCH (os:OS:Software)-[:VERSION]->(newVersion) WHERE os.name = 'Debian' AND newVersion.name = '8-Jessie' MATCH (m:Machine)-[:RUNS]->(:OSProcess)-[:INSTANCE]->(currentVersion) WHERE (currentVersion)<-[:PREVIOUS*]-(newVersion) RETURN m.name AS Machine;"
    },
    {
        "question": "What software applications depend on a specific service?",
        "query": "MATCH (app:SoftwareApplication)-[:DEPENDS_ON]->(service:SoftwareService) WHERE service.name = 'nombre_del_servicio' RETURN app.name;"
    },
    {
        "question": "What machines run service processes?",
        "query": "MATCH (machine:Machine)-[:RUNS]->(process:ServiceProcess) RETURN machine.name, process.name;"
    },
    {
        "question": "What interfaces are exposed on a specific machine?",
        "query": "MATCH (machine:Machine)-[:RUNS]->(:ServiceProcess)-[:EXPOSES]->(interface:Interface) WHERE machine.name = 'nombre_de_la_maquina' RETURN interface.name;"
    },
    {
        "question": "What software or services depend on a specific version?",
        "query": "MATCH (entity)-[:DEPENDS_ON]->(version:Version) WHERE version.name = 'nombre_de_la_version' RETURN entity.name;"
    },
    {
        "question": "What ports are being listened to by application processes in a specific network zone?",
        "query": "MATCH (zone:NetworkZone)<-[:CONNECTS]-(interface:Interface)<-[:LISTENS]-(process:ApplicationProcess)-[:LISTENS]->(port:Port) WHERE zone.name = 'nombre_de_la_zona_de_red' RETURN port.name;"
    },
    {
        "question": "What racks and switches are contained in a specific DataCenter?",
        "query": "MATCH (datacenter:DataCenter)-[:CONTAINS]->(rack:Rack)-[:HOLDS]->(switch:Switch) WHERE datacenter.name = 'nombre_del_centro_de_datos' RETURN rack.name, switch.name;"
    },
    {
        "question": "What OS processes are running on machines of a certain type?",
        "query": "MATCH (machine:Machine)-[:RUNS]->(process:OSProcess) WHERE machine.type = 'tipo_de_maquina' RETURN process.name;"
    },
    {
        "question": "What routes are configured between routers and switches in the network?",
        "query": "MATCH (router:Router)-[:ROUTES]->(switch:Switch) RETURN router.name, switch.name;"
    },
    {
        "question": "What services depend on other services?",
        "query": "MATCH (service1:SoftwareService)-[:DEPENDS_ON]->(service2:SoftwareService) RETURN service1.name, service2.name;"
    },
    {
        "question": "What ports are associated with software applications?",
        "query": "MATCH (app:SoftwareApplication)-[:INSTANCE]->(:ApplicationProcess)-[:LISTENS]->(port:Port) RETURN app.name, port.name;"
    }
]

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples, OpenAIEmbeddings(), Neo4jVector, k=5, input_keys=["question"]
)