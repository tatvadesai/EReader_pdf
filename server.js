const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 5000;

// Middleware
app.use(express.json({ limit: '100mb' }));
app.use(express.static('.'));

// Store for books, pages, and highlights (simplified in-memory for now)
const books = new Map();
const pages = new Map();
const highlights = new Map();
let nextBookId = 1;
let nextPageId = 1;
let nextHighlightId = 1;

// API Routes

// Get Gemini API configuration
app.get('/api/config', (req, res) => {
    res.json({
        geminiApiKey: process.env.GEMINI_API_KEY
    });
});

// Get all books
app.get('/api/books', (req, res) => {
    const bookList = Array.from(books.values()).map(book => {
        const bookPages = Array.from(pages.values()).filter(p => p.bookId === book.id);
        return {
            ...book,
            processedPages: bookPages.filter(p => p.isProcessed).length
        };
    });
    res.json(bookList);
});

// Create new book
app.post('/api/books', (req, res) => {
    const { title, filename, totalPages, fileData, thumbnail } = req.body;
    
    const book = {
        id: nextBookId++,
        title,
        filename,
        totalPages,
        processedPages: 0,
        fileData,
        thumbnail,
        createdAt: new Date(),
        lastReadAt: new Date(),
        currentPage: 1
    };
    
    books.set(book.id, book);
    res.json(book);
});

// Get specific book
app.get('/api/books/:id', (req, res) => {
    const bookId = parseInt(req.params.id);
    const book = books.get(bookId);
    
    if (!book) {
        return res.status(404).json({ error: 'Book not found' });
    }
    
    res.json(book);
});

// Get pages for a book
app.get('/api/books/:id/pages', (req, res) => {
    const bookId = parseInt(req.params.id);
    const bookPages = Array.from(pages.values())
        .filter(p => p.bookId === bookId)
        .sort((a, b) => a.pageNumber - b.pageNumber);
    
    res.json(bookPages);
});

// Create/update page
app.post('/api/pages', (req, res) => {
    const { bookId, pageNumber, extractedText } = req.body;
    
    // Check if page already exists
    let page = Array.from(pages.values()).find(p => 
        p.bookId === bookId && p.pageNumber === pageNumber
    );
    
    if (page) {
        // Update existing page
        page.extractedText = extractedText;
        page.isProcessed = true;
    } else {
        // Create new page
        page = {
            id: nextPageId++,
            bookId,
            pageNumber,
            extractedText,
            isProcessed: true,
            createdAt: new Date()
        };
        pages.set(page.id, page);
    }
    
    // Update book's processed page count
    const book = books.get(bookId);
    if (book) {
        const processedCount = Array.from(pages.values())
            .filter(p => p.bookId === bookId && p.isProcessed).length;
        book.processedPages = processedCount;
    }
    
    res.json(page);
});

// Update book reading position
app.put('/api/books/:id/position', (req, res) => {
    const bookId = parseInt(req.params.id);
    const { currentPage } = req.body;
    
    const book = books.get(bookId);
    if (!book) {
        return res.status(404).json({ error: 'Book not found' });
    }
    
    book.currentPage = currentPage;
    book.lastReadAt = new Date();
    
    res.json({ success: true });
});

// Create highlight
app.post('/api/highlights', (req, res) => {
    const { bookId, pageNumber, selectedText, highlightId } = req.body;
    
    const highlight = {
        id: nextHighlightId++,
        bookId,
        pageNumber,
        selectedText,
        highlightId,
        createdAt: new Date()
    };
    
    highlights.set(highlight.id, highlight);
    res.json(highlight);
});

// Get highlights for a book
app.get('/api/books/:id/highlights', (req, res) => {
    const bookId = parseInt(req.params.id);
    const bookHighlights = Array.from(highlights.values())
        .filter(h => h.bookId === bookId)
        .sort((a, b) => a.pageNumber - b.pageNumber);
    
    res.json(bookHighlights);
});

// Delete highlight
app.delete('/api/highlights/:id', (req, res) => {
    const highlightId = parseInt(req.params.id);
    highlights.delete(highlightId);
    res.json({ success: true });
});

// Serve the main reader application
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'reader.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`PDF E-Reader with AI server running on port ${PORT}`);
});

module.exports = app;