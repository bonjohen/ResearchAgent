"""
Vector Database Integration

This module provides utilities for working with vector databases for RAG operations.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

from src.utils.storage import get_storage_path


class VectorDBManager:
    """Manager for vector database operations."""
    
    def __init__(self, collection_name: str = "research_data"):
        """
        Initialize the vector database manager.
        
        Args:
            collection_name: Name of the collection to use
        """
        # Get the storage path for the vector database
        storage_path = get_storage_path() / "vector_db"
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(storage_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get the collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"Using existing collection: {collection_name}")
        except ValueError:
            # Use sentence-transformers for embeddings
            embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=embedding_function,
                metadata={"description": "Research data for RAG operations"}
            )
            print(f"Created new collection: {collection_name}")
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None) -> List[str]:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            List of document IDs
        """
        # Generate IDs if not provided
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in range(len(documents))]
        
        # Add documents to the collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def query(self, query_text: str, n_results: int = 5) -> Dict:
        """
        Query the vector database for similar documents.
        
        Args:
            query_text: The query text
            n_results: Number of results to return
            
        Returns:
            Dictionary containing query results
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        return results
    
    def get_document(self, doc_id: str) -> Dict:
        """
        Get a document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Dictionary containing the document
        """
        result = self.collection.get(ids=[doc_id])
        
        if not result["documents"]:
            raise ValueError(f"Document with ID {doc_id} not found")
        
        return {
            "id": result["ids"][0],
            "document": result["documents"][0],
            "metadata": result["metadatas"][0] if result["metadatas"] else {}
        }
    
    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document by ID.
        
        Args:
            doc_id: Document ID
        """
        self.collection.delete(ids=[doc_id])
    
    def update_document(self, doc_id: str, document: str, metadata: Optional[Dict] = None) -> None:
        """
        Update a document by ID.
        
        Args:
            doc_id: Document ID
            document: New document text
            metadata: Optional new metadata
        """
        self.collection.update(
            ids=[doc_id],
            documents=[document],
            metadatas=[metadata] if metadata else None
        )
    
    def get_all_documents(self) -> Dict:
        """
        Get all documents in the collection.
        
        Returns:
            Dictionary containing all documents
        """
        return self.collection.get()
    
    def count_documents(self) -> int:
        """
        Count the number of documents in the collection.
        
        Returns:
            Number of documents
        """
        return len(self.collection.get()["ids"])
    
    def reset_collection(self) -> None:
        """Reset the collection, removing all documents."""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            embedding_function=self.collection._embedding_function,
            metadata={"description": "Research data for RAG operations"}
        )


class RAGProcessor:
    """Processor for Retrieval-Augmented Generation operations."""
    
    def __init__(self, collection_name: str = "research_data"):
        """
        Initialize the RAG processor.
        
        Args:
            collection_name: Name of the collection to use
        """
        self.vector_db = VectorDBManager(collection_name=collection_name)
        
        # Initialize sentence transformer for chunking and embedding
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
    
    def process_document(self, document: str, metadata: Optional[Dict] = None, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        """
        Process a document for RAG operations.
        
        Args:
            document: Document text
            metadata: Optional metadata
            chunk_size: Size of chunks in characters
            chunk_overlap: Overlap between chunks in characters
            
        Returns:
            List of document IDs
        """
        # Chunk the document
        chunks = self._chunk_document(document, chunk_size, chunk_overlap)
        
        # Create metadata for each chunk
        if metadata is None:
            metadata = {}
        
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "total_chunks": len(chunks)
            })
            metadatas.append(chunk_metadata)
        
        # Add chunks to the vector database
        return self.vector_db.add_documents(chunks, metadatas)
    
    def _chunk_document(self, document: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        """
        Chunk a document into smaller pieces.
        
        Args:
            document: Document text
            chunk_size: Size of chunks in characters
            chunk_overlap: Overlap between chunks in characters
            
        Returns:
            List of document chunks
        """
        # Simple character-based chunking
        chunks = []
        start = 0
        
        while start < len(document):
            end = min(start + chunk_size, len(document))
            
            # Try to find a natural break point (period, newline, etc.)
            if end < len(document):
                # Look for a period, question mark, or exclamation point followed by a space or newline
                for i in range(end, max(start, end - 50), -1):
                    if document[i] in ['.', '!', '?', '\n'] and (i + 1 == len(document) or document[i + 1].isspace()):
                        end = i + 1
                        break
            
            chunks.append(document[start:end])
            start = end - chunk_overlap
        
        return chunks
    
    def query_for_context(self, query: str, n_results: int = 5) -> str:
        """
        Query the vector database for context relevant to the query.
        
        Args:
            query: Query text
            n_results: Number of results to return
            
        Returns:
            Concatenated context string
        """
        results = self.vector_db.query(query, n_results)
        
        if not results["documents"]:
            return ""
        
        # Concatenate the documents into a single context string
        context = "\n\n".join(results["documents"][0])
        
        return context
    
    def enhance_prompt_with_context(self, query: str, prompt_template: str, n_results: int = 5) -> str:
        """
        Enhance a prompt with context from the vector database.
        
        Args:
            query: Query text
            prompt_template: Prompt template with {context} placeholder
            n_results: Number of results to return
            
        Returns:
            Enhanced prompt with context
        """
        context = self.query_for_context(query, n_results)
        
        if not context:
            # If no context is found, remove the context placeholder
            enhanced_prompt = prompt_template.replace("{context}", "")
        else:
            # Replace the context placeholder with the actual context
            enhanced_prompt = prompt_template.format(context=context)
        
        return enhanced_prompt
