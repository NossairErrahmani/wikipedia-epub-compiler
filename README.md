# Wikipedia EPUB Compiler

A Python tool that downloads Wikipedia articles and compiles them into clean, readable EPUB files optimized for e-readers. Perfect for creating custom reading collections from your favorite Wikipedia articles.

## Features

- ✅ **EPUB Generation**: Creates fluid, e-reader-friendly EPUB files
- ✅ **Clean Content**: Automatically removes references, citations, and navigation clutter
- ✅ **Rate-Limited Requests**: Respectful scraping with built-in delays
- ✅ **Multi-Source Support**: Works with both wikipedia.org and wikibooks.org
- ✅ **Custom Styling**: Optimized typography for comfortable reading
- ✅ **Error Handling**: Robust handling of failed downloads and network issues
- ✅ **Progress Reporting**: Real-time feedback during compilation

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add Wikipedia URLs to `wiki_articles.txt`** (one per line):
   ```
   https://en.wikipedia.org/wiki/Data_dredging
   https://en.wikipedia.org/wiki/Zero-knowledge_proof
   https://en.wikipedia.org/wiki/Publication_bias
   ```

3. **Run the compiler:**
   ```bash
   python main.py
   ```

4. **Find your EPUB** at `wiki_compilation.epub`

## How It Works

The compiler uses a multi-step process to create clean, readable EPUBs:

1. **Download**: Fetches Wikipedia article HTML content
2. **Clean**: Removes references sections, navigation elements, and citation markers
3. **Format**: Converts to EPUB-compatible HTML with proper styling
4. **Compile**: Assembles articles into a single EPUB with table of contents

## Project Structure

```
├── main.py                    # Entry point - orchestrates the compilation
├── wiki_epub_compiler.py      # Core EPUB generation and content cleaning
├── wiki_articles.txt          # List of Wikipedia URLs (edit this!)
├── requirements.txt           # Python dependencies
├── wiki_downloader_pdf.py     # Legacy PDF downloader (for reference)
└── README.md                  # This file
```

## Configuration

### Content Cleaning
The tool automatically removes:
- References and bibliography sections
- Citation numbers like [1], [2]
- Navigation boxes and infoboxes
- Edit links and metadata
- External links sections
- "See also" sections

### Rate Limiting
- 1.5 second delay between article downloads
- Respectful User-Agent header
- Proper error handling for failed requests

## Requirements

- Python 3.7+
- BeautifulSoup4 for HTML parsing
- EbookLib for EPUB generation  
- Requests for HTTP handling

See `requirements.txt` for exact versions.

## Examples

The included `wiki_articles.txt` contains a curated list of interesting articles covering:
- Cognitive biases and statistical fallacies
- Computer science concepts
- Interesting phenomena and paradoxes

Feel free to replace with your own selection!

## Legacy PDF Support

The project includes `wiki_downloader_pdf.py` for PDF generation, originally designed for Google Colab. While the EPUB compiler is recommended for e-readers, the PDF version remains available for reference.

## Contributing

This project focuses on creating clean, readable content for e-readers. Contributions welcome for:
- Additional content filtering improvements
- Better error handling
- Performance optimizations
- New output formats

## License

MIT License - feel free to use and modify for your own Wikipedia reading collections!