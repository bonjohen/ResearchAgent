"""
Tests for the vector database integration.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add the src directory to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.vector_db import VectorDBManager, RAGProcessor


class TestVectorDBManager(unittest.TestCase):
    """Tests for the VectorDBManager class."""
    
    @patch('src.utils.vector_db.get_storage_path')
    @patch('src.utils.vector_db.chromadb.PersistentClient')
    def setUp(self, mock_client, mock_get_storage_path):
        """Set up the test environment."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Mock the storage path
        mock_get_storage_path.return_value = Path(self.temp_dir.name)
        
        # Mock the ChromaDB client
        self.mock_collection = MagicMock()
        mock_client.return_value.get_collection.side_effect = ValueError("Collection not found")
        mock_client.return_value.create_collection.return_value = self.mock_collection
        
        # Create the VectorDBManager
        self.vector_db = VectorDBManager(collection_name="test_collection")
    
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    def test_add_documents(self):
        """Test adding documents to the vector database."""
        # Set up test data
        documents = ["Document 1", "Document 2", "Document 3"]
        metadatas = [{"source": "test"} for _ in range(len(documents))]
        ids = ["id1", "id2", "id3"]
        
        # Call the method
        result_ids = self.vector_db.add_documents(documents, metadatas, ids)
        
        # Check that the collection's add method was called with the correct arguments
        self.mock_collection.add.assert_called_once_with(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        # Check that the method returns the correct IDs
        self.assertEqual(result_ids, ids)
    
    def test_add_documents_without_ids(self):
        """Test adding documents without providing IDs."""
        # Set up test data
        documents = ["Document 1", "Document 2", "Document 3"]
        
        # Call the method
        result_ids = self.vector_db.add_documents(documents)
        
        # Check that the collection's add method was called
        self.mock_collection.add.assert_called_once()
        
        # Check that the method returns the correct number of IDs
        self.assertEqual(len(result_ids), len(documents))
    
    def test_query(self):
        """Test querying the vector database."""
        # Set up test data
        query_text = "Test query"
        n_results = 5
        expected_results = {
            "ids": [["id1", "id2"]],
            "documents": [["Document 1", "Document 2"]],
            "metadatas": [[{"source": "test"}, {"source": "test"}]],
            "distances": [[0.1, 0.2]]
        }
        self.mock_collection.query.return_value = expected_results
        
        # Call the method
        results = self.vector_db.query(query_text, n_results)
        
        # Check that the collection's query method was called with the correct arguments
        self.mock_collection.query.assert_called_once_with(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # Check that the method returns the correct results
        self.assertEqual(results, expected_results)
    
    def test_get_document(self):
        """Test getting a document by ID."""
        # Set up test data
        doc_id = "id1"
        expected_result = {
            "ids": ["id1"],
            "documents": ["Document 1"],
            "metadatas": [{"source": "test"}]
        }
        self.mock_collection.get.return_value = expected_result
        
        # Call the method
        result = self.vector_db.get_document(doc_id)
        
        # Check that the collection's get method was called with the correct arguments
        self.mock_collection.get.assert_called_once_with(ids=[doc_id])
        
        # Check that the method returns the correct result
        self.assertEqual(result, {
            "id": "id1",
            "document": "Document 1",
            "metadata": {"source": "test"}
        })
    
    def test_get_document_not_found(self):
        """Test getting a document that doesn't exist."""
        # Set up test data
        doc_id = "nonexistent_id"
        self.mock_collection.get.return_value = {
            "ids": [],
            "documents": [],
            "metadatas": []
        }
        
        # Check that the method raises a ValueError
        with self.assertRaises(ValueError):
            self.vector_db.get_document(doc_id)
    
    def test_delete_document(self):
        """Test deleting a document."""
        # Set up test data
        doc_id = "id1"
        
        # Call the method
        self.vector_db.delete_document(doc_id)
        
        # Check that the collection's delete method was called with the correct arguments
        self.mock_collection.delete.assert_called_once_with(ids=[doc_id])
    
    def test_update_document(self):
        """Test updating a document."""
        # Set up test data
        doc_id = "id1"
        document = "Updated document"
        metadata = {"source": "updated"}
        
        # Call the method
        self.vector_db.update_document(doc_id, document, metadata)
        
        # Check that the collection's update method was called with the correct arguments
        self.mock_collection.update.assert_called_once_with(
            ids=[doc_id],
            documents=[document],
            metadatas=[metadata]
        )
    
    def test_get_all_documents(self):
        """Test getting all documents."""
        # Set up test data
        expected_result = {
            "ids": ["id1", "id2"],
            "documents": ["Document 1", "Document 2"],
            "metadatas": [{"source": "test"}, {"source": "test"}]
        }
        self.mock_collection.get.return_value = expected_result
        
        # Call the method
        result = self.vector_db.get_all_documents()
        
        # Check that the collection's get method was called
        self.mock_collection.get.assert_called_once_with()
        
        # Check that the method returns the correct result
        self.assertEqual(result, expected_result)
    
    def test_count_documents(self):
        """Test counting documents."""
        # Set up test data
        self.mock_collection.get.return_value = {
            "ids": ["id1", "id2", "id3"],
            "documents": ["Document 1", "Document 2", "Document 3"],
            "metadatas": [{"source": "test"}, {"source": "test"}, {"source": "test"}]
        }
        
        # Call the method
        count = self.vector_db.count_documents()
        
        # Check that the collection's get method was called
        self.mock_collection.get.assert_called_once_with()
        
        # Check that the method returns the correct count
        self.assertEqual(count, 3)
    
    def test_reset_collection(self):
        """Test resetting the collection."""
        # Set up test data
        collection_name = "test_collection"
        self.mock_collection.name = collection_name
        self.mock_collection._embedding_function = MagicMock()
        
        # Call the method
        self.vector_db.reset_collection()
        
        # Check that the client's delete_collection method was called with the correct arguments
        self.vector_db.client.delete_collection.assert_called_once_with(collection_name)
        
        # Check that the client's create_collection method was called with the correct arguments
        self.vector_db.client.create_collection.assert_called_with(
            name=collection_name,
            embedding_function=self.mock_collection._embedding_function,
            metadata={"description": "Research data for RAG operations"}
        )


class TestRAGProcessor(unittest.TestCase):
    """Tests for the RAGProcessor class."""
    
    @patch('src.utils.vector_db.VectorDBManager')
    @patch('src.utils.vector_db.SentenceTransformer')
    def setUp(self, mock_sentence_transformer, mock_vector_db_manager):
        """Set up the test environment."""
        # Mock the VectorDBManager
        self.mock_vector_db = MagicMock()
        mock_vector_db_manager.return_value = self.mock_vector_db
        
        # Create the RAGProcessor
        self.rag_processor = RAGProcessor(collection_name="test_collection")
    
    def test_process_document(self):
        """Test processing a document."""
        # Set up test data
        document = "This is a test document. It has multiple sentences. Each sentence should be processed."
        metadata = {"source": "test"}
        chunk_size = 50
        chunk_overlap = 10
        
        # Mock the _chunk_document method
        self.rag_processor._chunk_document = MagicMock(return_value=[
            "This is a test document.",
            "It has multiple sentences.",
            "Each sentence should be processed."
        ])
        
        # Mock the vector_db.add_documents method
        expected_ids = ["id1", "id2", "id3"]
        self.mock_vector_db.add_documents.return_value = expected_ids
        
        # Call the method
        result_ids = self.rag_processor.process_document(document, metadata, chunk_size, chunk_overlap)
        
        # Check that the _chunk_document method was called with the correct arguments
        self.rag_processor._chunk_document.assert_called_once_with(document, chunk_size, chunk_overlap)
        
        # Check that the vector_db.add_documents method was called with the correct arguments
        self.mock_vector_db.add_documents.assert_called_once()
        
        # Check that the method returns the correct IDs
        self.assertEqual(result_ids, expected_ids)
    
    def test_chunk_document(self):
        """Test chunking a document."""
        # Set up test data
        document = "This is a test document. It has multiple sentences. Each sentence should be processed."
        chunk_size = 30
        chunk_overlap = 5
        
        # Call the method
        chunks = self.rag_processor._chunk_document(document, chunk_size, chunk_overlap)
        
        # Check that the document was chunked correctly
        self.assertGreater(len(chunks), 1)
        self.assertLessEqual(max(len(chunk) for chunk in chunks), chunk_size)
    
    def test_query_for_context(self):
        """Test querying for context."""
        # Set up test data
        query = "Test query"
        n_results = 3
        expected_results = {
            "ids": [["id1", "id2"]],
            "documents": [["Document 1", "Document 2"]],
            "metadatas": [[{"source": "test"}, {"source": "test"}]],
            "distances": [[0.1, 0.2]]
        }
        self.mock_vector_db.query.return_value = expected_results
        
        # Call the method
        context = self.rag_processor.query_for_context(query, n_results)
        
        # Check that the vector_db.query method was called with the correct arguments
        self.mock_vector_db.query.assert_called_once_with(query, n_results)
        
        # Check that the method returns the correct context
        self.assertEqual(context, "Document 1\n\nDocument 2")
    
    def test_query_for_context_no_results(self):
        """Test querying for context with no results."""
        # Set up test data
        query = "Test query"
        n_results = 3
        self.mock_vector_db.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }
        
        # Call the method
        context = self.rag_processor.query_for_context(query, n_results)
        
        # Check that the method returns an empty string
        self.assertEqual(context, "")
    
    def test_enhance_prompt_with_context(self):
        """Test enhancing a prompt with context."""
        # Set up test data
        query = "Test query"
        prompt_template = "Answer the following question using this context:\n\n{context}\n\nQuestion: {query}"
        n_results = 3
        
        # Mock the query_for_context method
        expected_context = "Document 1\n\nDocument 2"
        self.rag_processor.query_for_context = MagicMock(return_value=expected_context)
        
        # Call the method
        enhanced_prompt = self.rag_processor.enhance_prompt_with_context(query, prompt_template, n_results)
        
        # Check that the query_for_context method was called with the correct arguments
        self.rag_processor.query_for_context.assert_called_once_with(query, n_results)
        
        # Check that the method returns the correct enhanced prompt
        expected_prompt = f"Answer the following question using this context:\n\n{expected_context}\n\nQuestion: {{query}}"
        self.assertEqual(enhanced_prompt, expected_prompt)
    
    def test_enhance_prompt_with_context_no_results(self):
        """Test enhancing a prompt with context when no results are found."""
        # Set up test data
        query = "Test query"
        prompt_template = "Answer the following question using this context:\n\n{context}\n\nQuestion: {query}"
        n_results = 3
        
        # Mock the query_for_context method
        self.rag_processor.query_for_context = MagicMock(return_value="")
        
        # Call the method
        enhanced_prompt = self.rag_processor.enhance_prompt_with_context(query, prompt_template, n_results)
        
        # Check that the method returns the correct enhanced prompt with the context placeholder removed
        expected_prompt = "Answer the following question using this context:\n\n\n\nQuestion: {query}"
        self.assertEqual(enhanced_prompt, expected_prompt)


if __name__ == "__main__":
    unittest.main()
