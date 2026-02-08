"""Document retrieval logic."""

from langchain_core.documents import Document

from mit.rag.vectorstore import VectorStore


class Retriever:
    """Document retriever for a specific collection."""

    def __init__(self, collection_name: str) -> None:
        """Initialize retriever for a specific collection.

        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.vectorstore = VectorStore(collection_name)

    async def aretrieve(self, query: str, k: int = 5) -> list[Document]:
        """Retrieve relevant documents asynchronously.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of relevant documents
        """
        return await self.vectorstore.asimilarity_search(query, k=k)

    def retrieve(self, query: str, k: int = 5) -> list[Document]:
        """Retrieve relevant documents synchronously.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of relevant documents
        """
        return self.vectorstore.similarity_search(query, k=k)
