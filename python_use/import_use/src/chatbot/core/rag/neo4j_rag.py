from chatbot.core.load_model.get_model import getModel
from chatbot.utils.prompts import militory
from chatbot.bg.bg import getBg
from chatbot.fg.fg import fg
class Neo4j_rag:
    def __init__(self):
        getModel()
        getBg()
        fg()
        pass

    def process(self):
        return True


if __name__ == "__main__":
    neo4j_processor = Neo4j_rag()
    neo4j_processor.process()
    print(militory)
