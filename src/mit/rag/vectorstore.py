"""ChromaDB vector store management."""

from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from mit.config import get_config
from mit.rag.embeddings import get_embeddings

_chroma_client: chromadb.ClientAPI | None = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Get the shared ChromaDB client."""
    global _chroma_client

    if _chroma_client is None:
        config = get_config()
        persist_dir = Path(config.chromadb.persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        _chroma_client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )

    return _chroma_client


class VectorStore:
    """ChromaDB vector store for a specific collection."""

    def __init__(self, collection_name: str) -> None:
        """Initialize vector store for a specific collection.

        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.collection_name = collection_name
        self._vectorstore: Chroma | None = None

    def _get_vectorstore(self) -> Chroma:
        """Get or create the LangChain Chroma vectorstore."""
        if self._vectorstore is None:
            config = get_config()
            self._vectorstore = Chroma(
                client=get_chroma_client(),
                collection_name=self.collection_name,
                embedding_function=get_embeddings(),
                persist_directory=config.chromadb.persist_dir,
            )
        return self._vectorstore

    async def aadd_documents(
        self, documents: list[Document], ids: list[str] | None = None
    ) -> list[str]:
        """Add documents to the vector store.

        Args:
            documents: Documents to add
            ids: Optional document IDs

        Returns:
            List of document IDs
        """
        vectorstore = self._get_vectorstore()
        return await vectorstore.aadd_documents(documents, ids=ids)

    def add_documents(
        self, documents: list[Document], ids: list[str] | None = None
    ) -> list[str]:
        """Add documents to the vector store (sync version).

        Args:
            documents: Documents to add
            ids: Optional document IDs

        Returns:
            List of document IDs
        """
        vectorstore = self._get_vectorstore()
        return vectorstore.add_documents(documents, ids=ids)

    async def asimilarity_search(
        self, query: str, k: int = 5
    ) -> list[Document]:
        """Search for similar documents.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar documents
        """
        vectorstore = self._get_vectorstore()
        return await vectorstore.asimilarity_search(query, k=k)

    def similarity_search(self, query: str, k: int = 5) -> list[Document]:
        """Search for similar documents (sync version).

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar documents
        """
        vectorstore = self._get_vectorstore()
        return vectorstore.similarity_search(query, k=k)

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        client = get_chroma_client()
        try:
            client.delete_collection(self.collection_name)
            self._vectorstore = None
        except ValueError:
            # Collection doesn't exist
            pass
