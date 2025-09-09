#!/usr/bin/env python3

import sys
from pathlib import Path
from wiki_epub_compiler import process_wikipedia_articles

def load_wikipedia_urls(filename='wiki_articles.txt'):
    """Reads Wikipedia URLs from a text file, filtering out invalid entries and comments."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Only keep actual Wikipedia/Wikibooks URLs
        valid_urls = []
        for url in urls:
            if 'wikipedia.org/wiki/' in url or 'wikibooks.org/wiki/' in url:
                valid_urls.append(url)
            else:
                print(f"[!] Skipping non-Wikipedia URL: {url}")
        
        return valid_urls
    except FileNotFoundError:
        print(f"[!] File {filename} not found!")
        return []
    except Exception as e:
        print(f"[!] Error reading {filename}: {e}")
        return []

def main():
    """Entry point that coordinates the entire Wikipedia-to-EPUB conversion process."""
    print("Wikipedia to EPUB Compiler")
    print("=" * 50)
    
    # Read the list of Wikipedia articles to download
    urls = load_wikipedia_urls()
    if not urls:
        print("[!] No valid Wikipedia URLs found!")
        sys.exit(1)
    
    print(f"[*] Found {len(urls)} Wikipedia URLs to process")
    
    # Download articles and compile them into an EPUB
    output_file = 'wiki_compilation.epub'
    success = process_wikipedia_articles(urls, output_file)
    
    if success:
        file_size = Path(output_file).stat().st_size if Path(output_file).exists() else 0
        print(f"\n🎉 Success! Created {output_file} ({file_size:,} bytes)")
        print(f"📚 Your EPUB is ready for your e-reader!")
    else:
        print(f"\n❌ Failed to create EPUB file")
        sys.exit(1)

if __name__ == "__main__":
    main()
