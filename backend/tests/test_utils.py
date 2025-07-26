"""
Tests for utility functions in the EdutechHackathon backend.

Tests file processing utilities and other helper functions:
- File type detection
- Text extraction from different file formats
- File validation and processing
- Error handling in utility functions
"""
import pytest
import tempfile
import os
import asyncio
from unittest.mock import patch, MagicMock
from app.utils.file_processor import FileProcessor


class TestFileProcessor:
    """Test file processing utilities."""
    
    def test_file_processor_initialization(self):
        """Test FileProcessor initialization."""
        processor = FileProcessor()
        
        assert processor.upload_dir is not None
        assert processor.temp_dir is not None
    
    def test_get_file_extension(self):
        """Test file extension extraction."""
        processor = FileProcessor()
        
        # Test various file extensions
        assert processor._get_file_extension("test.txt") == ".txt"
        assert processor._get_file_extension("document.pdf") == ".pdf"
        assert processor._get_file_extension("notes.md") == ".md"
        assert processor._get_file_extension("report.docx") == ".docx"
        assert processor._get_file_extension("no_extension") == ""
        assert processor._get_file_extension("") == ""
    
    def test_mime_from_extension(self):
        """Test MIME type detection from extension."""
        processor = FileProcessor()
        
        # Test supported MIME types
        assert processor._mime_from_extension("test.txt") == "text/plain"
        assert processor._mime_from_extension("document.pdf") == "application/pdf"
        assert processor._mime_from_extension("notes.md") == "text/markdown"
        assert processor._mime_from_extension("report.docx") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        # Test unsupported extensions
        assert processor._mime_from_extension("image.jpg") == "application/octet-stream"
        assert processor._mime_from_extension("video.mp4") == "application/octet-stream"
    
    def test_detect_mime_type(self):
        """Test MIME type detection."""
        processor = FileProcessor()
        
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            f.flush()
            
            mime_type = processor.detect_mime_type(f.name)
            os.unlink(f.name)
        
        # Should detect as text/plain
        assert mime_type == "text/plain"
    
    def test_detect_mime_type_markdown(self):
        """Test MIME type detection for markdown files."""
        processor = FileProcessor()
        
        # Create a markdown file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Markdown")
            f.flush()
            
            mime_type = processor.detect_mime_type(f.name)
            os.unlink(f.name)
        
        # Should detect as text/markdown
        assert mime_type == "text/markdown"
    
    @pytest.mark.asyncio
    async def test_extract_text_file(self):
        """Test text extraction from plain text files."""
        processor = FileProcessor()
        
        test_content = "This is a test document.\nIt has multiple lines.\nAnd some special characters: éñüß"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            f.flush()
            
            extracted_text = await processor._extract_text_file(f.name)
            os.unlink(f.name)
        
        assert extracted_text == test_content
    
    @pytest.mark.asyncio
    async def test_extract_text_file_markdown(self):
        """Test text extraction from markdown files."""
        processor = FileProcessor()
        
        test_content = """# Test Document
        
This is a **markdown** document with *formatting*.

## Section 1
- List item 1
- List item 2

## Section 2
Some more content here.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            f.flush()
            
            extracted_text = await processor._extract_text_file(f.name)
            os.unlink(f.name)
        
        # Should extract text content
        assert "Test Document" in extracted_text
        assert "markdown" in extracted_text
        assert "List item 1" in extracted_text
    
    @pytest.mark.asyncio
    @patch('app.utils.file_processor.PDF_AVAILABLE', True)
    @patch('app.utils.file_processor.PDF')
    async def test_extract_pdf_text(self, mock_pdf):
        """Test text extraction from PDF files."""
        processor = FileProcessor()
        
        # Mock PDF reader
        mock_pdf_instance = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"
        mock_pdf_instance.pages = [mock_page1, mock_page2]
        
        mock_pdf.open.return_value.__enter__.return_value = mock_pdf_instance
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"fake pdf content")
            f.flush()
            
            extracted_text = await processor._extract_pdf_text(f.name)
            os.unlink(f.name)
        
        expected_text = "Page 1 content\nPage 2 content"
        assert extracted_text == expected_text
    
    @pytest.mark.asyncio
    @patch('app.utils.file_processor.DOCX_AVAILABLE', True)
    @patch('app.utils.file_processor.Document')
    async def test_extract_docx_text(self, mock_document):
        """Test text extraction from DOCX files."""
        processor = FileProcessor()
        
        # Mock document
        mock_doc = MagicMock()
        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "First paragraph"
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = "Second paragraph"
        mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2]
        mock_doc.tables = []  # No tables
        mock_document.return_value = mock_doc
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            f.write(b"fake docx content")
            f.flush()
            
            extracted_text = await processor._extract_docx_text(f.name)
            os.unlink(f.name)
        
        expected_text = "First paragraph\nSecond paragraph"
        assert extracted_text == expected_text
    
    @pytest.mark.asyncio
    async def test_extract_text_content_unsupported_format(self):
        """Test text extraction from unsupported formats."""
        processor = FileProcessor()
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b"fake image content")
            f.flush()
            
            extracted_text = await processor.extract_text_content(f.name, "image/jpeg")
            os.unlink(f.name)
        
        assert extracted_text is None
    
    @pytest.mark.asyncio
    async def test_extract_text_content_file_not_found(self):
        """Test text extraction when file doesn't exist."""
        processor = FileProcessor()
        
        extracted_text = await processor.extract_text_content("nonexistent_file.txt", "text/plain")
        
        assert extracted_text is None
    
    @pytest.mark.asyncio
    @patch('app.utils.file_processor.PDF_AVAILABLE', False)
    async def test_extract_pdf_text_not_available(self):
        """Test PDF text extraction when libraries are not available."""
        processor = FileProcessor()
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"fake pdf content")
            f.flush()
            
            extracted_text = await processor._extract_pdf_text(f.name)
            os.unlink(f.name)
        
        assert extracted_text is None
    
    @pytest.mark.asyncio
    @patch('app.utils.file_processor.DOCX_AVAILABLE', False)
    async def test_extract_docx_text_not_available(self):
        """Test DOCX text extraction when libraries are not available."""
        processor = FileProcessor()
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            f.write(b"fake docx content")
            f.flush()
            
            extracted_text = await processor._extract_docx_text(f.name)
            os.unlink(f.name)
        
        assert extracted_text is None
    
    def test_get_file_size(self):
        """Test file size retrieval."""
        processor = FileProcessor()
        
        test_content = "This is test content for size calculation."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            f.flush()
            
            file_size = processor.get_file_size(f.name)
            os.unlink(f.name)
        
        assert file_size == len(test_content.encode('utf-8'))
    
    def test_delete_file(self):
        """Test file deletion."""
        processor = FileProcessor()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            f.flush()
            file_path = f.name
        
        # File should exist
        assert os.path.exists(file_path)
        
        # Delete file
        result = processor.delete_file(file_path)
        
        assert result is True
        assert not os.path.exists(file_path)
    
    def test_delete_nonexistent_file(self):
        """Test deletion of non-existent file."""
        processor = FileProcessor()
        
        result = processor.delete_file("nonexistent_file.txt")
        
        assert result is False


class TestFileProcessingIntegration:
    """Test integration of file processing utilities."""
    
    @pytest.mark.asyncio
    async def test_complete_file_processing_workflow(self):
        """Test complete file processing workflow."""
        processor = FileProcessor()
        
        # Test with a text file
        test_content = "This is a comprehensive test document.\nIt contains multiple lines and paragraphs.\n\nThis is the second paragraph with some special characters: éñüß"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            f.flush()
            
            # Get file info
            file_size = processor.get_file_size(f.name)
            mime_type = processor.detect_mime_type(f.name)
            
            # Extract text
            extracted_text = await processor.extract_text_content(f.name, mime_type)
            
            os.unlink(f.name)
        
        # Verify results
        assert mime_type == "text/plain"
        assert extracted_text == test_content
        assert len(extracted_text) > 0
        assert file_size == len(test_content.encode('utf-8'))
    
    @pytest.mark.asyncio
    async def test_file_processing_with_large_content(self):
        """Test file processing with large content."""
        processor = FileProcessor()
        
        # Create large content (1MB of text)
        large_content = "A" * 1024 * 1024
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(large_content)
            f.flush()
            
            file_size = processor.get_file_size(f.name)
            extracted_text = await processor.extract_text_content(f.name, "text/plain")
            
            os.unlink(f.name)
        
        assert len(extracted_text) == len(large_content)
        assert file_size == len(large_content.encode('utf-8'))


class TestFileProcessingEdgeCases:
    """Test edge cases in file processing."""
    
    @pytest.mark.asyncio
    async def test_empty_file_processing(self):
        """Test processing of empty files."""
        processor = FileProcessor()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("")
            f.flush()
            
            extracted_text = await processor.extract_text_content(f.name, "text/plain")
            os.unlink(f.name)
        
        assert extracted_text == ""
    
    @pytest.mark.asyncio
    async def test_file_with_special_characters(self):
        """Test processing of files with special characters."""
        processor = FileProcessor()
        
        special_content = "Special chars: éñüß\nUnicode: 🚀🎉💻\nEmojis: 😀😍🎯"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(special_content)
            f.flush()
            
            extracted_text = await processor.extract_text_content(f.name, "text/plain")
            os.unlink(f.name)
        
        assert extracted_text == special_content
        assert "éñüß" in extracted_text
        assert "🚀🎉💻" in extracted_text
        assert "😀😍🎯" in extracted_text
    
    @pytest.mark.asyncio
    async def test_file_with_binary_content(self):
        """Test processing of files with binary content."""
        processor = FileProcessor()
        
        # Create a file with binary content
        binary_content = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09"
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
            f.write(binary_content)
            f.flush()
            
            # Should handle binary content gracefully
            extracted_text = await processor.extract_text_content(f.name, "text/plain")
            os.unlink(f.name)
        
        # Should handle binary content gracefully - it actually returns the binary content as text
        assert extracted_text is not None
        assert len(extracted_text) > 0
    
    @pytest.mark.asyncio
    async def test_file_encoding_handling(self):
        """Test handling of different file encodings."""
        processor = FileProcessor()
        
        # Test UTF-8 encoding
        utf8_content = "UTF-8 content: éñüß"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(utf8_content)
            f.flush()
            
            extracted_text = await processor.extract_text_content(f.name, "text/plain")
            os.unlink(f.name)
        
        assert extracted_text == utf8_content
        
        # Test ASCII encoding
        ascii_content = "ASCII content: Hello World!"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='ascii') as f:
            f.write(ascii_content)
            f.flush()
            
            extracted_text = await processor.extract_text_content(f.name, "text/plain")
            os.unlink(f.name)
        
        assert extracted_text == ascii_content 