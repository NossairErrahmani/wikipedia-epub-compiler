# Wikipedia Article Compiler

A Python project to compile favorite Wikipedia articles into EPUB format for e-reader consumption. The goal is to download Wikipedia articles as markdown files and compile them into a fluid, readable EPUB format that works well on small screens.

## Features

- Downloads Wikipedia articles from a list of URLs
- Currently generates PDF output (existing functionality)
- Planned: EPUB generation with fluid text formatting
- Removes references sections for cleaner reading experience
- Batch processing of multiple articles

## Current Status

The project currently includes a working PDF downloader (`wiki_downloader_pdf.py`) that processes articles from `wiki_articles.txt`. The main goal is to extend this to generate EPUB files instead of PDFs for better e-reader compatibility.

## Files

- `wiki_articles.txt` - List of Wikipedia URLs to process
- `wiki_downloader_pdf.py` - Current PDF generation script
- `main.py` - Main entry point (minimal)
- `wiki_compilation.pdf` - Example output from PDF script