"""Data ingestion script for the MIT framework.

This script loads .md and .txt files from the data directory,
generates embeddings, and stores them in ChromaDB.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from mit.rag.vectorstore import VectorStore


# Collection mapping: data folder -> collection name
COLLECTION_MAPPING = {
    "network/api_ref": "network_api_ref",
    "network/issues": "network_issues",
    "auth/oauth": "auth_oauth",
    "auth/errors": "auth_errors",
}


def load_documents(data_dir: Path, folder: str) -> list:
    """Load documents from a folder.

    Args:
        data_dir: Base data directory
        folder: Subfolder to load from

    Returns:
        List of loaded documents
    """
    folder_path = data_dir / folder

    if not folder_path.exists():
        print(f"  Warning: {folder_path} does not exist, skipping...")
        return []

    documents = []

    # Load markdown files
    try:
        md_loader = DirectoryLoader(
            str(folder_path),
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        documents.extend(md_loader.load())
    except Exception as e:
        print(f"  Warning: Failed to load .md files from {folder}: {e}")

    # Load text files
    try:
        txt_loader = DirectoryLoader(
            str(folder_path),
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        documents.extend(txt_loader.load())
    except Exception as e:
        print(f"  Warning: Failed to load .txt files from {folder}: {e}")

    return documents


def split_documents(documents: list) -> list:
    """Split documents into chunks.

    Args:
        documents: Documents to split

    Returns:
        List of document chunks
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(documents)


def ingest_folder(data_dir: Path, folder: str, collection_name: str) -> int:
    """Ingest a folder into a collection.

    Args:
        data_dir: Base data directory
        folder: Subfolder to ingest
        collection_name: Target collection name

    Returns:
        Number of documents ingested
    """
    print(f"\nIngesting {folder} -> {collection_name}")

    # Load documents
    documents = load_documents(data_dir, folder)
    if not documents:
        print("  No documents found")
        return 0

    print(f"  Loaded {len(documents)} documents")

    # Split into chunks
    chunks = split_documents(documents)
    print(f"  Split into {len(chunks)} chunks")

    # Add metadata
    for chunk in chunks:
        chunk.metadata["collection"] = collection_name
        chunk.metadata["folder"] = folder

    # Store in vector store
    vectorstore = VectorStore(collection_name)

    # Clear existing collection
    vectorstore.delete_collection()

    # Add documents
    vectorstore.add_documents(chunks)
    print(f"  Stored {len(chunks)} chunks in ChromaDB")

    return len(chunks)


def main():
    """Main ingestion function."""
    print("=" * 60)
    print("MIT Data Ingestion")
    print("=" * 60)

    # Determine data directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / "data"

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print("Please create the data directory with your knowledge files.")
        sys.exit(1)

    print(f"Data directory: {data_dir}")

    total_chunks = 0

    for folder, collection_name in COLLECTION_MAPPING.items():
        chunks = ingest_folder(data_dir, folder, collection_name)
        total_chunks += chunks

    print("\n" + "=" * 60)
    print(f"Ingestion complete! Total chunks: {total_chunks}")
    print("=" * 60)


if __name__ == "__main__":
    main()
