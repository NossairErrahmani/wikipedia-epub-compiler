# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Wikipedia article compiler that downloads and processes Wikipedia articles for e-reader consumption. The implementation generates clean EPUB files with references sections removed for optimal reading experience on e-readers.

## Key Files

- `wiki_articles.txt` - Contains the list of Wikipedia URLs to process (one per line)
- `wiki_epub_compiler.py` - Core EPUB generation module with Wikipedia content processing
- `main.py` - Main entry point that orchestrates the EPUB generation process
- `requirements.txt` - Python dependencies (requests, beautifulsoup4, pathlib, ebooklib)
- `wiki_compilation.epub` - Generated EPUB output file
- `wiki_downloader_pdf.py` - Legacy PDF generation script (retained for reference)

## Architecture

The EPUB compiler uses a streamlined process:
1. **Fetch**: Downloads Wikipedia article HTML content directly 
2. **Clean**: Removes references, navigation, and unwanted sections using BeautifulSoup
3. **Convert**: Creates EPUB chapters with proper formatting
4. **Compile**: Assembles final EPUB with table of contents and metadata

Key functions in `wiki_epub_compiler.py`:
- `fetch_wikipedia_content()` - Downloads article HTML and extracts title
- `clean_article_content()` - Removes references sections and cleans HTML content
- `create_epub_chapter()` - Converts cleaned HTML to EPUB chapter format
- `compile_epub()` - Assembles final EPUB with proper structure and styling
- `process_wikipedia_articles()` - Main orchestration function

## Configuration

Important settings in `wiki_epub_compiler.py`:
- `USER_AGENT` - Set to respectful identifier for Wikipedia requests
- `REQUEST_DELAY_SECONDS` - Rate limiting delay between requests (1.5 seconds)
- Content filtering targets: References, Bibliography, External links, See also sections

## Development Commands

Install dependencies:
```bash
pip install -r requirements.txt
```

Generate EPUB from wiki_articles.txt:
```bash
python main.py
```

Run legacy PDF downloader:
```bash
python wiki_downloader_pdf.py
```

## Features

- ✅ EPUB generation with fluid, e-reader-friendly formatting
- ✅ Automatic removal of references and navigation sections  
- ✅ Rate-limited Wikipedia requests for respectful scraping
- ✅ Table of contents generation
- ✅ Progress reporting during compilation
- ✅ Error handling for failed article downloads
- ✅ Support for both wikipedia.org and wikibooks.org URLs