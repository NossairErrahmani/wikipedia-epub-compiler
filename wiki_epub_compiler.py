#!/usr/bin/env python3

import requests
import time
import re
from bs4 import BeautifulSoup, Comment
from ebooklib import epub
from urllib.parse import urlparse, urljoin
import os
from pathlib import Path

# Respectful User-Agent string for Wikipedia requests
USER_AGENT = 'WikipediaEpubCompiler/1.0 (Educational use; contact: user@example.com)'
REQUEST_DELAY_SECONDS = 1.5

def fetch_wikipedia_content(url):
    """
    Downloads and parses a Wikipedia article's HTML content.
    
    Args:
        url (str): The Wikipedia article URL to fetch
        
    Returns:
        tuple: (article_title, BeautifulSoup_object) on success, (None, None) on failure
    """
    try:
        url = url.strip()
        if not url:
            return None, None
            
        print(f"   [*] Fetching: {url}")
        
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get the article title from the main heading
        title_element = soup.find('h1', {'class': 'firstHeading'})
        article_title = title_element.get_text().strip() if title_element else "Untitled Article"
        
        print(f"   [+] Successfully fetched: {article_title}")
        return article_title, soup
        
    except requests.RequestException as e:
        print(f"   [!] Failed to fetch {url}: {e}")
        return None, None
    except Exception as e:
        print(f"   [!] Error processing {url}: {e}")
        return None, None

def clean_article_content(soup):
    """
    Cleans Wikipedia HTML by removing references, navigation elements, and other clutter
    that interferes with a clean reading experience on e-readers.
    
    Args:
        soup (BeautifulSoup): Parsed HTML of the Wikipedia article
        
    Returns:
        str: Cleaned HTML content suitable for EPUB generation
    """
    if not soup:
        return ""
    
    # Locate Wikipedia's main article content container
    content_div = soup.find('div', {'class': 'mw-parser-output'})
    if not content_div:
        print("   [!] Could not find main content area")
        return ""
    
    # Work with a copy to preserve the original soup object
    content = BeautifulSoup(str(content_div), 'html.parser')
    
    # Target sections that add clutter to e-reader experience
    unwanted_sections = [
        'References', 'Bibliography', 'External links', 'See also', 
        'Further reading', 'Sources', 'Notes', 'Footnotes',
        'External sources', 'Works cited', 'Citations'
    ]
    
    for section_name in unwanted_sections:
        # Scan for headings matching our cleanup list
        for heading in content.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
            if heading.get_text().strip().lower() == section_name.lower():
                # Remove this section and all content until the next major heading
                current_level = int(heading.name[1])  # h2=2, h3=3, etc.
                elements_to_remove = [heading]
                
                # Gather everything in this section for removal
                element = heading.find_next_sibling()
                while element:
                    # Stop when we hit the next major section
                    if (element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] 
                        and int(element.name[1]) <= current_level):
                        break
                    
                    elements_to_remove.append(element)
                    element = element.find_next_sibling()
                
                # Clean out the entire section
                for elem in elements_to_remove:
                    if elem.parent:
                        elem.extract()
                break
    
    # Strip out Wikipedia's navigation and metadata elements
    unwanted_selectors = [
        '.navbox',           # Navigation boxes
        # '.infobox',          # Info boxes - actually useful for context
        '.ambox',            # Article message boxes
        '.hatnote',          # Disambiguation notes
        '.sistersitebox',    # Sister project boxes
        '.metadata',         # Metadata
        '.printfooter',      # Print footer
        '.catlinks',         # Category links
        '.mw-editsection',   # Edit section links
        '.reference',        # Individual reference links
        '.mw-cite-backlink', # Citation backlinks
        'sup.reference',     # Reference superscripts
        '.portal',           # Portal boxes
        '.navframe',         # Collapsible navigation frames
        '.collapsible',      # Other collapsible content
        '.stub',             # Stub notices
        '.reflist',          # References list containers
        '.refbegin',         # Reference begin containers
        '.references',       # References containers
        'cite.citation',     # Citation elements
        '.cs1',              # CS1 citation format
        '.citation',         # General citations
    ]
    
    for selector in unwanted_selectors:
        for element in content.select(selector):
            element.extract()
    
    # Clean up stray reference entries that escaped the section removal
    for li in content.find_all('li'):
        # Check if this list item is just a leftover reference
        non_cite_content = []
        for child in li.children:
            if hasattr(child, 'name'):
                if child.name not in ['cite', 'span'] or not child.get('class') or not any(cls in ['citation', 'cs1', 'reference'] for cls in child.get('class', [])):
                    non_cite_content.append(child)
            elif isinstance(child, str) and child.strip():
                non_cite_content.append(child)
        
        # Remove if it's purely citation content
        if not non_cite_content:
            li.extract()
    
    # Strip HTML comments
    for comment in content.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # Clean up inline citation markers like [1], [2]
    for element in content.find_all('sup'):
        if element.get_text().strip().startswith('[') and element.get_text().strip().endswith(']'):
            element.extract()
    
    # Remove paragraphs that became empty after cleaning
    for p in content.find_all('p'):
        if not p.get_text().strip():
            p.extract()
    
    # Remove images since they don't embed properly in EPUB
    for img in content.find_all('img'):
        img.extract()
    
    # Make Wikipedia links absolute for better EPUB compatibility
    for link in content.find_all('a'):
        href = link.get('href')
        if href and href.startswith('/wiki/'):
            link['href'] = 'https://en.wikipedia.org' + href
    
    return str(content)

def create_epub_chapter(title, content, chapter_id):
    """
    Converts cleaned Wikipedia content into a properly formatted EPUB chapter.
    
    Args:
        title (str): Article title for the chapter
        content (str): Cleaned HTML content
        chapter_id (int): Sequential chapter number
        
    Returns:
        epub.EpubHtml: Ready-to-add EPUB chapter object
    """
    # Sanitize title to create a valid filename
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()
    safe_title = re.sub(r'[-\s]+', '_', safe_title)
    
    chapter = epub.EpubHtml(
        title=title,
        file_name=f'chapter_{chapter_id}_{safe_title}.xhtml',
        lang='en'
    )
    
    # Build complete HTML document for the chapter
    html_content = f'''
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>{title}</title>
    </head>
    <body>
        <h1>{title}</h1>
        {content}
    </body>
    </html>
    '''
    
    chapter.content = html_content
    return chapter

def compile_epub(articles_data, output_filename):
    """
    Takes cleaned Wikipedia articles and assembles them into a complete EPUB file.
    
    Args:
        articles_data (list): List of (title, content) tuples from processed articles
        output_filename (str): Path where the final EPUB should be saved
        
    Returns:
        bool: True if EPUB creation succeeded, False otherwise
    """
    if not articles_data:
        print("[!] No articles to compile!")
        return False
    
    print(f"\n[*] Creating EPUB with {len(articles_data)} articles...")
    
    # Initialize the EPUB book structure
    book = epub.EpubBook()
    
    # Configure book metadata for e-reader display
    book.set_identifier('wikipedia_compilation_' + str(int(time.time())))
    book.set_title('Wikipedia Article Compilation')
    book.add_author('Wikipedia Contributors')
    book.set_language('en')
    
    # Define styling for clean, readable text on e-readers
    nav_css = epub.EpubItem(
        uid="nav_css",
        file_name="style/nav.css",
        media_type="text/css",
        content='''
        body {
            font-family: serif;
            line-height: 1.6;
            margin: 2em;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #333;
            margin-top: 2em;
            margin-bottom: 1em;
        }
        p {
            margin-bottom: 1em;
            text-align: justify;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        .infobox {
            border: 1px solid #ccc;
            background-color: #f9f9f9;
            float: right;
            margin: 0 0 1em 1em;
            padding: 0.5em;
            width: 300px;
        }
        '''
    )
    book.add_item(nav_css)
    
    chapters = []
    
    # Convert each Wikipedia article into an EPUB chapter
    for i, (title, content) in enumerate(articles_data, 1):
        chapter = create_epub_chapter(title, content, i)
        chapter.add_item(nav_css)
        book.add_item(chapter)
        chapters.append(chapter)
        print(f"   [+] Added chapter {i}: {title}")
    
    # Set up the book's navigation structure
    book.toc = chapters
    
    # Include standard EPUB navigation components
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Add basic typography styles
    style = '''
    body { font-family: serif; }
    h1 { text-align: center; }
    '''
    default_css = epub.EpubItem(
        uid="default",
        file_name="style/default.css", 
        media_type="text/css",
        content=style
    )
    book.add_item(default_css)
    
    # Define the reading order of chapters
    book.spine = ['nav'] + chapters
    
    # Save the completed EPUB to disk
    try:
        epub.write_epub(output_filename, book, {})
        print(f"   [+] EPUB created successfully: {output_filename}")
        return True
    except Exception as e:
        print(f"   [!] Failed to create EPUB: {e}")
        return False

def process_wikipedia_articles(urls, output_filename='wiki_compilation.epub'):
    """
    Main orchestration function that handles the complete Wikipedia-to-EPUB workflow.
    Downloads articles, cleans them up, and compiles into a single EPUB file.
    
    Args:
        urls (list): List of Wikipedia URLs to process
        output_filename (str): Name for the output EPUB file
        
    Returns:
        bool: True if the EPUB was successfully created
    """
    print(f"[*] Processing {len(urls)} Wikipedia articles...")
    
    articles_data = []
    failed_count = 0
    
    for i, url in enumerate(urls, 1):
        print(f"\n[*] Processing article {i}/{len(urls)}")
        
        # Download and parse this article
        title, soup = fetch_wikipedia_content(url)
        if not title or not soup:
            failed_count += 1
            continue
        
        # Remove references and cleanup for e-reader
        cleaned_content = clean_article_content(soup)
        if not cleaned_content.strip():
            print(f"   [!] No content extracted from {title}")
            failed_count += 1
            continue
        
        articles_data.append((title, cleaned_content))
        
        # Be respectful to Wikipedia's servers
        if i < len(urls):  # No need to wait after the final article
            time.sleep(REQUEST_DELAY_SECONDS)
    
    print(f"\n[*] Successfully processed {len(articles_data)} articles")
    if failed_count > 0:
        print(f"[!] Failed to process {failed_count} articles")
    
    if articles_data:
        success = compile_epub(articles_data, output_filename)
        if success:
            print(f"\n[+] Compilation complete! EPUB saved as: {output_filename}")
            return True
    
    print(f"\n[!] No articles were successfully processed!")
    return False