from PyDAO import SchemaMapping

mapping = SchemaMapping.loadFromXML ('mapping.pydao.xml')
mapping.runJob (overwrite = True)

