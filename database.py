from neo4j import GraphDatabase


class Neo4j:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def list_last(self):
        with self.driver.session() as session:
            return session.read_transaction(self._list_last)

    def list_by_author(self, author):
        with self.driver.session() as session:
            return session.read_transaction(self._list_by_author, author)

    @staticmethod
    def _list_last(tx):
        result = tx.run("MATCH (m:Media)-[r:HAS_AUTHOR|HAS_COLLECTION]->(n) "
                        "RETURN m,collect(r) as relationships,collect(n) as endNodes "
                        "ORDER BY m.fansadocId DESC LIMIT 10")
        # result = tx.run("MATCH (a:Author)<-[ha:HAS_AUTHOR]-(m:Media)-[hc:HAS_COLLECTION]->(c:Collection) "
        #                 "RETURN m as media, hc as h_collection, ha as h_author, c as collection, a as author "
        #                 "ORDER BY m.fansadocId DESC LIMIT 10")

        values = []
        for record in result:
            item = {
                'media': record[0],
                'relationships': record[1],
                'end_nodes': record[2],
            }
            values.append(item)
        return values

    @staticmethod
    def _list_by_author(tx, author):
        result = tx.run("MATCH (m:Media)-[r:HAS_AUTHOR]->(n:Author {name:'" + author + "'}) "
                        "RETURN m,collect(r) as relationships,collect(n) as endNodes "
                        "ORDER BY m.fansadocId ASC")
        values = []
        for record in result:
            item = {
                'media': record[0],
                'relationships': record[1],
                'end_nodes': record[2],
            }
            values.append(item)
        return values
