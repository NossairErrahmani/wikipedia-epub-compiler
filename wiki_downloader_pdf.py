
import requests
import time
import os
import shutil
from urllib.parse import urlparse, quote, unquote, urljoin
from pypdf import PdfWriter
from pathlib import Path
import sys
from google.colab import files
import traceback
from bs4 import BeautifulSoup  # Import BeautifulSoup

# Configuration settings for the Wikipedia PDF downloader
USER_AGENT = 'WikipediaPdfDownloader/1.2 (Educational use; contact: user@example.com)'

OUTPUT_PDF_FILE = 'wiki_compilation.pdf'
TEMP_DIR = 'temp_wiki_pdfs'
# Rate limiting delay between article downloads
DOWNLOAD_DELAY_SECONDS = 1  # Be respectful to Wikipedia's servers
REQUEST_TIMEOUT_STEP1 = 60   # HTML page timeout
REQUEST_TIMEOUT_STEP2 = 180  # PDF download timeout (longer for large files)

# --- User Input ---
wiki_urls_text = """
https://en.wikipedia.org/wiki/Publication_bias
https://en.wikipedia.org/wiki/Data_dredging
https://en.wikipedia.org/wiki/Zero-knowledge_proof
https://en.wikipedia.org/wiki/Brinkmanship
https://en.wikipedia.org/wiki/Flanderization
https://en.wikipedia.org/wiki/Recursive_acronym
https://en.wikipedia.org/wiki/Off-by-one_error
https://en.wikipedia.org/wiki/Category:Programming_language_comparisons
https://en.wikipedia.org/wiki/Python_syntax_and_semantics
https://en.wikibooks.org/wiki/German/Grammar
https://en.wikipedia.org/wiki/Goodhart%27s_law
https://en.wikipedia.org/wiki/List_of_common_misconceptions
https://en.wikipedia.org/wiki/Timeline_of_the_far_future
https://en.wikipedia.org/wiki/List_of_fallacies
https://en.wikipedia.org/wiki/List_of_unusual_deaths
https://en.wikipedia.org/wiki/List_of_confidence_tricks
https://en.wikipedia.org/wiki/Geographical_renaming#Naming_disputes
https://en.wikipedia.org/wiki/Intersectionality
https://en.wikipedia.org/wiki/Behavioral_economics
https://en.wikipedia.org/wiki/Systems_thinking
https://en.wikipedia.org/wiki/Constructivism_(philosophy_of_science)
https://en.wikipedia.org/wiki/Sociotechnical_system
https://en.wikipedia.org/wiki/Heuristic_(psychology)
https://en.wikipedia.org/wiki/Complex_system
https://en.wikipedia.org/wiki/Data_compression
https://en.wikipedia.org/wiki/Coding_theory
https://en.wikipedia.org/wiki/Cognitive_bias_mitigation
https://en.wikipedia.org/wiki/List_of_cognitive_biases
https://en.wikipedia.org/wiki/Black_swan_theory
https://en.wikipedia.org/wiki/Autogram
https://en.wikipedia.org/wiki/Quine_(computing)
https://en.wikipedia.org/wiki/Droste_effect
https://en.wikipedia.org/wiki/Paraprosdokian
https://en.wikipedia.org/wiki/Garden-path_sentence
https://en.wikipedia.org/wiki/List_of_linguistic_example_sentences
https://en.wikipedia.org/wiki/Wikipedia%3AList_of_hoaxes_on_Wikipedia
https://en.wikipedia.org/wiki/List_of_military_strategies_and_concepts
https://en.wikipedia.org/wiki/Information_asymmetry
https://en.wikipedia.org/wiki/Social_choice_theory
https://en.wikipedia.org/wiki/Lists_of_sovereign_states_and_dependent_territories
https://en.wikipedia.org/wiki/Political_history_of_the_world
https://en.wikipedia.org/wiki/Rose_(mathematics)
https://en.wikipedia.org/wiki/100_prisoners_problem
https://en.wikipedia.org/wiki/Perverse_incentive
https://en.wikipedia.org/wiki/Systems_theory
https://en.wikipedia.org/wiki/Futile_game
https://en.wikipedia.org/wiki/Surreal_humour
https://en.wikipedia.org/wiki/Self-referential_humor
https://en.wikipedia.org/wiki/List_of_paradoxes
https://en.wikipedia.org/wiki/Snowclone
https://en.wikipedia.org/wiki/Dead_man%27s_switch
https://en.wikipedia.org/wiki/Comparative_illusion
https://en.wikipedia.org/wiki/Divide_and_choose
https://en.wikipedia.org/wiki/Category:Types_of_auction
https://en.wikipedia.org/wiki/Reverse_auction
https://en.wikipedia.org/wiki/Crosswordese
https://en.wikipedia.org/wiki/Casus_belli
https://en.wikipedia.org/wiki/Overton_window
https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population
https://en.wikipedia.org/wiki/List_of_numbers
https://en.wikipedia.org/wiki/Metric_prefix#List_of_SI_prefixes
https://en.wikipedia.org/wiki/Numeral_prefix
https://en.wikipedia.org/wiki/List_of_commonly_used_taxonomic_affixes
https://en.wikipedia.org/wiki/List_of_medical_roots,_suffixes_and_prefixes
https://en.wikipedia.org/wiki/List_of_Latin_names_of_cities
https://en.wikipedia.org/wiki/List_of_Latin_words_with_English_derivatives
https://en.wikipedia.org/wiki/List_of_Greek_and_Latin_roots_in_English
https://en.wikipedia.org/wiki/List_of_Latin_and_Greek_words_commonly_used_in_systematic_names
https://en.wikipedia.org/wiki/Glossary_of_scientific_naming
https://en.wikipedia.org/wiki/List_of_mnemonics
https://en.wikipedia.org/wiki/Inherently_funny_word
https://en.wikipedia.org/wiki/Phonestheme
https://en.wiktionary.org/wiki/Appendix:German_cognates_with_English
https://fr.wikipedia.org/wiki/Identit%C3%A9_remarquable
https://en.wikipedia.org/wiki/List_of_territorial_disputes
https://en.wikipedia.org/wiki/United_Nations_list_of_non-self-governing_territories#Current_entries
https://en.wikipedia.org/wiki/List_of_largest_cities_throughout_history
https://en.wikipedia.org/wiki/Euclidean_tilings_by_convex_regular_polygons?wprov=sfti1#Regular_tilings
https://en.wikipedia.org/wiki/Braess%27s_paradox
https://en.wikipedia.org/wiki/Emergence
https://en.wikipedia.org/wiki/Fuzzy_logic
https://en.wikipedia.org/wiki/Collective_effervescence
https://en.wikipedia.org/wiki/Kolmogorov_complexity
https://en.wikipedia.org/wiki/List_of_longest-living_organisms
https://en.wikipedia.org/wiki/List_of_U.S._counties_with_shortest_life_expectancy
https://en.wikipedia.org/wiki/List_of_individual_trees
https://en.wikipedia.org/wiki/List_of_superlative_trees
https://en.wikipedia.org/wiki/Largest_and_heaviest_animals
https://en.wikipedia.org/wiki/List_of_largest_mammals
https://en.wikipedia.org/wiki/List_of_largest_insects
https://en.wikipedia.org/wiki/Wonders_of_the_World
https://endwalker.com/archive.html
https://en.wikipedia.org/wiki/List_of_hypothetical_technologies
https://en.wikipedia.org/wiki/List_of_emerging_technologies
https://en.wikipedia.org/wiki/List_of_natural_disasters_by_death_toll
https://en.wikipedia.org/wiki/List_of_accidents_and_disasters_by_death_toll
https://en.wikipedia.org/wiki/List_of_anthropogenic_disasters_by_death_toll
https://en.wikipedia.org/wiki/List_of_metonyms
https://en.wikipedia.org/wiki/List_of_lists_of_lists
https://en.wikipedia.org/wiki/Timeline_of_association_football
https://en.wikipedia.org/wiki/Wikipedia:Deleted_articles_with_freaky_titles
https://en.wikipedia.org/wiki/List_of_Generation_Z_slang
https://en.wikipedia.org/wiki/Frequency_illusion
https://en.wikipedia.org/wiki/Base_rate_fallacy
https://en.wikipedia.org/wiki/Intuitive_statistics
https://en.wikipedia.org/wiki/Self-defeating_prophecy
https://en.wikipedia.org/wiki/Preparedness_paradox
https://en.wikipedia.org/wiki/Risk_compensation
https://en.wikipedia.org/wiki/Nobel_disease
https://en.wikipedia.org/wiki/Lambda_calculus
https://en.wikipedia.org/wiki/High-context_and_low-context_cultures
https://en.wikipedia.org/wiki/Impossible_color
https://en.wikipedia.org/wiki/Hildegart_Rodr%C3%ADguez_Carballeira
https://en.wikipedia.org/wiki/Surname
https://en.wikipedia.org/wiki/List_of_national_flag_proposals
https://en.wikipedia.org/wiki/Flag_families
https://commons.wikimedia.org/wiki/Flags_of_extinct_states
https://en.wikipedia.org/wiki/List_of_former_sovereign_states
https://en.wikipedia.org/wiki/List_of_sovereign_states
https://en.wikipedia.org/wiki/Internet_aesthetic
https://en.wikipedia.org/wiki/Former_countries_in_Europe_after_1815
https://en.wikipedia.org/wiki/Lists_of_political_entities_by_century
https://en.wikipedia.org/wiki/Timeline_of_geopolitical_changes_(2000%E2%80%93present)
https://en.wikipedia.org/wiki/List_of_ways_people_honor_the_dead
https://en.wikipedia.org/wiki/List_of_folk_heroes
https://en.wikipedia.org/wiki/List_of_destroyed_heritage
https://en.wikipedia.org/wiki/R/K_selection_theory
https://en.wikipedia.org/wiki/List_of_animal_sounds
https://en.wikipedia.org/wiki/Lists_of_animals
https://en.wikipedia.org/wiki/List_of_animal_names
https://en.wikipedia.org/wiki/List_of_Latin_phrases_(full)
https://en.wikipedia.org/wiki/List_of_chord_progressions
https://en.wikipedia.org/wiki/List_of_bones_of_the_human_skeleton
https://fr.wikipedia.org/wiki/Figure_de_style
https://en.wikipedia.org/wiki/Outline_of_human_anatomy
https://en.wikipedia.org/wiki/List_of_national_anthems
https://en.wikipedia.org/wiki/Wikipedia:Language_recognition_chart
https://en.wikipedia.org/wiki/List_of_stock_characters
https://en.wikipedia.org/wiki/Stereotypes_of_groups_within_the_United_States
https://en.wikipedia.org/wiki/List_of_constructed_languages
https://en.wikipedia.org/wiki/List_of_contemporary_ethnic_groups
https://en.wikipedia.org/wiki/List_of_national_border_changes_(1914%E2%80%93present)
https://en.wikipedia.org/wiki/Negotiation#Tactics
https://en.wikipedia.org/wiki/Watershed_(broadcasting)
https://en.wikipedia.org/wiki/List_of_association_footballers_who_died_after_on-field_incidents
https://en.wikipedia.org/wiki/Wikipedia:Lamest_edit_wars
https://en.wikipedia.org/wiki/%CA%BEI%CA%BFrab
https://en.wikipedia.org/wiki/Leverage_(negotiation)
https://en.wikipedia.org/wiki/The_New_York_Times_crossword
https://en.wikipedia.org/wiki/Glossary_of_mathematical_symbols
https://en.wikipedia.org/wiki/List_of_logic_symbols
https://en.wikipedia.org/wiki/List_of_emerging_technologies
https://en.wikipedia.org/wiki/List_of_academic_fields
https://en.wikipedia.org/wiki/List_of_animal_names
https://en.wikipedia.org/wiki/List_of_algorithms
https://en.wikipedia.org/wiki/List_of_colors_by_shade
https://en.wikipedia.org/wiki/List_of_Internet_phenomena
https://en.wikipedia.org/wiki/Glossary_of_medicine
https://en.wikipedia.org/wiki/Outline_of_human_anatomy
https://fr.wikipedia.org/wiki/Liste_des_figures_de_style
https://en.wikipedia.org/wiki/List_of_most-watched_television_broadcasts
https://en.wikipedia.org/wiki/List_of_circulating_currencies
https://en.wikipedia.org/wiki/Currency_symbol
https://en.wikipedia.org/wiki/List_of_current_heads_of_state_and_government
https://en.wikipedia.org/wiki/The_world%27s_100_most_threatened_species
https://en.wikipedia.org/wiki/List_of_historical_unrecognized_states
https://en.wikipedia.org/wiki/Illeism
https://en.wikipedia.org/wiki/List_of_obsolete_units_of_measurement
https://en.wikipedia.org/wiki/List_of_humorous_units_of_measurement
https://en.wikipedia.org/wiki/List_of_unusual_units_of_measurement
https://en.wikipedia.org/wiki/Indefinite_and_fictitious_numbers
https://en.wikipedia.org/wiki/Lists_of_most_expensive_items_by_category
https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style
https://en.wikipedia.org/wiki/List_of_most_popular_given_names
https://en.wikipedia.org/wiki/List_of_family_name_affixes
https://en.wikipedia.org/wiki/Lists_of_most_common_surnames
https://en.wikipedia.org/wiki/Induction_puzzles
https://fr.wikipedia.org/wiki/Classification_des_jeux
https://en.wikipedia.org/wiki/Magic_number_(programming)
https://fr.wikipedia.org/wiki/Fen%C3%AAtre_d'Overton
https://fr.wikipedia.org/wiki/Nombre_de_Dunbar
https://en.wikipedia.org/wiki/Affordance?wprov=sfti1
https://fr.wikipedia.org/wiki/%C3%89minence_grise
https://en.wikipedia.org/wiki/Cultural_universal?wprov=sfti1
https://en.wikipedia.org/wiki/Antifragility?wprov=sfti1
https://en.wikipedia.org/wiki/Lists_of_most_expensive_items_by_category
https://en.wikipedia.org/wiki/Pseudo-anglicism?wprov=sfti1
https://en.wikipedia.org/wiki/Lists_of_people_by_nationality
https://en.wikipedia.org/wiki/List_of_tallest_buildings
https://en.wikipedia.org/wiki/List_of_tallest_buildings_and_structures
https://en.wikipedia.org/wiki/List_of_photographs_considered_the_most_important
https://en.wikipedia.org/wiki/List_of_world_association_football_records
https://en.wikipedia.org/wiki/List_of_forms_of_government
https://en.wikipedia.org/wiki/List_of_countries_by_system_of_government
https://en.wikipedia.org/wiki/Illegal_number
https://en.wikipedia.org/wiki/List_of_mythological_places
https://en.wikipedia.org/wiki/List_of_Greek_mythological_figures
https://en.wikipedia.org/wiki/List_of_presidents_of_the_United_States
https://en.wikipedia.org/wiki/Eye_contact#Between_species
https://www.britannica.com/story/history-of-technology-timeline
https://en.wikipedia.org/wiki/Cooperative_principle
https://en.wikipedia.org/wiki/Very_Short_Introductions
https://en.wikipedia.org/wiki/Hypocognition
https://en.wikipedia.org/wiki/R/place
https://en.wikipedia.org/wiki/Auction?wprov=sfti1#Types
https://fr.wikipedia.org/wiki/Antipattern
https://en.wikipedia.org/wiki/Golden_generation#Football
https://en.wikipedia.org/wiki/List_of_heaviest_people
https://en.wikipedia.org/wiki/Maximum_life_span
https://en.wikipedia.org/wiki/Hyperreality
https://en.wikipedia.org/wiki/Sorites_paradox
https://en.wikipedia.org/wiki/List_of_eponymous_laws
https://en.wikipedia.org/wiki/List_of_city_name_changes
https://en.wikipedia.org/wiki/English_exonyms
https://en.wikipedia.org/wiki/News_values
https://en.wikipedia.org/wiki/Roko%27s_basilisk
https://en.wikipedia.org/wiki/DNA_digital_data_storage
https://en.wikipedia.org/wiki/Information_hazard
https://en.wikipedia.org/wiki/Glossary_of_rhetorical_terms
https://en.wikipedia.org/wiki/Path_dependence
https://en.wikipedia.org/wiki/Iron_law_of_oligarchy
https://en.wikipedia.org/wiki/Comparison_of_voting_rules
https://en.wikipedia.org/wiki/List_of_musical_scales_and_modes
https://en.wikipedia.org/wiki/Glossary_of_philosophy
https://en.wikipedia.org/wiki/Glossary_of_professional_wrestling_terms
https://en.wikipedia.org/wiki/Association_football_tactics_and_skills
https://en.wikipedia.org/wiki/Lists_of_English_words
https://en.wikipedia.org/wiki/Glossary_of_British_terms_not_widely_used_in_the_United_States
https://en.wikipedia.org/wiki/Glossary_of_American_terms_not_widely_used_in_the_United_Kingdom
https://en.wikipedia.org/wiki/List_of_English_words_with_disputed_usage
https://en.wikipedia.org/wiki/Mathematical_proof
https://en.wikipedia.org/wiki/Comparison_of_Portuguese_and_Spanish
https://en.wikipedia.org/wiki/List_of_prematurely_reported_obituaries
https://en.wikipedia.org/wiki/Wikipedia:Essay_directory
https://en.wikipedia.org/wiki/Rhetorical_device
https://en.wikipedia.org/wiki/List_of_World_Heritage_in_Danger
https://en.wikipedia.org/wiki/UNESCO_Intangible_Cultural_Heritage_Lists
https://en.wikipedia.org/wiki/Glossary_of_engineering:_A%E2%80%93L
https://en.wikipedia.org/wiki/Glossary_of_engineering:_M%E2%80%93Z
https://en.wikipedia.org/wiki/Glossary_of_computer_science
https://en.wikipedia.org/wiki/List_of_chemical_element_name_etymologies
https://fr.wikipedia.org/wiki/Racine_grecque
https://en.wikipedia.org/wiki/List_of_last_words
https://en.wikipedia.org/wiki/List_of_unusual_deaths_in_the_21st_century
https://en.wikipedia.org/wiki/List_of_entertainers_who_died_during_a_performance
https://en.wikipedia.org/wiki/List_of_narrative_techniques
https://en.wikipedia.org/wiki/List_of_lost_inventions
https://en.wikipedia.org/wiki/Greatest_Britons_spin-offs
https://en.wikipedia.org/wiki/2025_Prayag_Maha_Kumbh_Mela
https://en.wikipedia.org/wiki/List_of_largest_peaceful_gatherings
https://en.wikipedia.org/wiki/List_of_most-attended_concerts
https://en.wikipedia.org/wiki/List_of_most-attended_concert_tours
https://en.wikipedia.org/wiki/List_of_video_games_notable_for_negative_reception
https://en.wikipedia.org/wiki/List_of_media_notable_for_being_in_development_hell
https://en.wikipedia.org/wiki/List_of_television_shows_notable_for_negative_reception
https://en.wikipedia.org/wiki/Extremes_on_Earth
https://en.wikipedia.org/wiki/Handicap_principle
https://en.wikipedia.org/wiki/Letter_frequency
https://en.wikipedia.org/wiki/Frequency_analysis
https://en.wikipedia.org/wiki/English_collocations
https://en.wikipedia.org/wiki/Zipf%27s_law
https://en.wikipedia.org/wiki/Relevance_theory
https://en.wikipedia.org/wiki/Four-sides_model
https://en.wikipedia.org/wiki/Benford%27s_law
https://en.wikipedia.org/wiki/Statelessness
https://en.wikipedia.org/wiki/Lists_of_highest-grossing_films
https://en.wikipedia.org/wiki/List_of_popes
https://en.wikipedia.org/wiki/List_of_highest_mountains_on_Earth
https://en.wikipedia.org/wiki/List_of_elected_and_appointed_female_heads_of_state_and_government
https://en.wikipedia.org/wiki/Lists_of_etymologies
https://fr.wikipedia.org/wiki/Confidentialit%C3%A9_diff%C3%A9rentielle
https://fr.wikipedia.org/wiki/Avantage_comparatif
https://en.wikipedia.org/wiki/Index_of_athletics_record_progressions
https://en.wikipedia.org/wiki/List_of_tallest_statues
https://en.wikipedia.org/wiki/List_of_longest_bridges
https://en.wikipedia.org/wiki/List_of_tallest_structures_built_before_the_20th_century
https://en.wikipedia.org/wiki/Largest_prehistoric_animals
https://en.wikipedia.org/wiki/Square%E2%80%93cube_law
https://en.wikipedia.org/wiki/List_of_world_records_in_chess
https://en.wikipedia.org/wiki/Unintended_consequences
https://en.wikipedia.org/wiki/Conflict-of-interest_editing_on_Wikipedia
https://en.wikipedia.org/wiki/List_of_national_independence_days
https://en.wikipedia.org/wiki/List_of_sovereign_states_by_date_of_formation
https://en.wikipedia.org/wiki/Political_history_of_the_world
https://en.wikipedia.org/wiki/Free-rider_problem
https://en.wikipedia.org/wiki/Tragedy_of_the_commons
https://en.wikipedia.org/wiki/Tragedy_of_the_anticommons
https://en.wikipedia.org/wiki/Headline#Headlinese
https://en.wikipedia.org/wiki/Shibboleth
https://en.wikipedia.org/wiki/Code_word_(figure_of_speech)
https://en.wikipedia.org/wiki/Weasel_word
https://en.wikipedia.org/wiki/Longest_words
https://en.wikipedia.org/wiki/Hapax_legomenon
https://en.wikipedia.org/wiki/Longest_word_in_English
https://en.wikipedia.org/wiki/Autogram
https://en.wikipedia.org/wiki/List_of_natural_disasters_by_death_toll#21st_century
https://en.wikipedia.org/wiki/List_of_the_longest_English_words_with_one_syllable
https://en.wikipedia.org/wiki/List_of_superlatives
https://en.wikipedia.org/wiki/Strange_loop
https://en.wikipedia.org/wiki/List_of_visionary_tall_buildings_and_structures
https://en.wikipedia.org/wiki/Tallest_structures_by_category
https://en.wikipedia.org/wiki/Category:World_records
https://en.wikipedia.org/wiki/List_of_largest_universities_and_university_networks_by_enrollment
https://en.wikipedia.org/wiki/List_of_most_expensive_paintings
https://en.wikipedia.org/wiki/3rd_millennium
https://en.wikipedia.org/wiki/Timeline_of_prehistory
https://en.wikipedia.org/wiki/Timeline_of_human_evolution
https://en.wikipedia.org/wiki/Timeline_of_historic_inventions
https://en.wikipedia.org/wiki/Global_catastrophe_scenarios
https://en.wikipedia.org/wiki/List_of_accidents_and_disasters_by_death_toll
""" # Add your list here

# --- Helper Functions ---

def get_pdf_render_url(wiki_url):
    """Converts a Wikipedia article URL to a PDF render page URL."""
    # Builds the URL for Wikipedia's PDF generation service
    try:
        wiki_url = wiki_url.strip()
        if not wiki_url: return None
        parsed_url = urlparse(wiki_url)
        if not parsed_url.scheme or not parsed_url.netloc or not parsed_url.path.startswith('/wiki/'):
            print(f"   [!] Skipping invalid/malformed Wikipedia URL: {wiki_url}")
            return None

        article_title_decoded = unquote(parsed_url.path.split('/wiki/', 1)[1])
        if not article_title_decoded:
             print(f"   [!] Could not extract article title from path: {parsed_url.path}")
             return None

        # Note: Wikipedia uses underscores instead of spaces in the 'page' parameter here.
        # Let's stick to the path component's original encoding which handles both.
        article_title_encoded = quote(parsed_url.path.split('/wiki/', 1)[1], safe='') # Get path part and encode

        render_url = f"{parsed_url.scheme}://{parsed_url.netloc}/w/index.php?title=Special:DownloadAsPdf&page={article_title_encoded}"
        return render_url
    except Exception as e:
        print(f"   [!] Error parsing URL {wiki_url}: {e}")
        return None

def download_pdf_two_step(render_url, output_path_str, headers, session):
    """
    Downloads PDF using the two-step process:
    1. GET the render page.
    2. Parse for form data.
    3. GET the actual PDF using form data.
    Returns True on success, False on failure.
    """
    print(f"   [*] Step 1: Fetching render page: {render_url}")
    form_data = {}
    actual_download_url = None

    try:
        # --- Step 1: Get the intermediate HTML page ---
        response_step1 = session.get(render_url, timeout=REQUEST_TIMEOUT_STEP1)
        response_step1.raise_for_status()

        content_type_step1 = response_step1.headers.get('content-type', '').lower()
        if 'text/html' not in content_type_step1:
            print(f"   [!] Failed Step 1: Expected HTML render page, but got '{content_type_step1}'.")
            # Maybe it directly served PDF this time? Check just in case.
            if 'application/pdf' in content_type_step1:
                print("   [*] Surprise! Received PDF directly on Step 1. Saving...")
                with open(output_path_str, 'wb') as f:
                   f.write(response_step1.content)
                return True
            return False

        print(f"   [*] Step 1: Success. Received HTML render page.")

        # --- Step 2: Parse HTML for the form data and action URL ---
        soup = BeautifulSoup(response_step1.text, 'html.parser')

        # Find the form containing the download button/relevant hidden fields
        # Often the button is inside a form, or the inputs are nearby.
        # Let's look for the hidden input named "page" as an anchor.
        hidden_page_input = soup.find('input', {'type': 'hidden', 'name': 'page'})
        if not hidden_page_input:
            # Fallback: Look for the submit button itself
             submit_button = soup.find('button', {'type': 'submit'})
             if submit_button:
                 form = submit_button.find_parent('form')
             else:
                 form = None # Cannot reliably find form
        else:
           form = hidden_page_input.find_parent('form') # Find the form containing the hidden input

        if not form:
            print("   [!] Failed Step 2: Could not find the download form on the render page.")
            # Save the intermediate HTML for debugging
            debug_html_path = output_path_str + ".render.html"
            with open(debug_html_path, "w", encoding='utf-8') as f_html:
                 f_html.write(response_step1.text)
            print(f"   [*] Saved intermediate HTML for debugging: {os.path.basename(debug_html_path)}")
            return False

        # Extract the form's action URL
        action = form.get('action')
        if not action:
            action = render_url # Submit to the same URL if action is missing
        # Ensure the URL is absolute
        actual_download_url_base = urljoin(render_url, action)

        # Extract all hidden inputs within this form
        hidden_inputs = form.find_all('input', {'type': 'hidden'})
        for input_tag in hidden_inputs:
            name = input_tag.get('name')
            value = input_tag.get('value')
            if name:
                form_data[name] = value
        print(f"   [*] Step 2: Extracted form data: {form_data}")

        # Find the submit button details (optional, but helps construct the URL if needed)
        # The hidden fields are usually enough. The button click typically just submits these.
        # Note: Wikipedia's form here actually submits via GET, using the hidden inputs as parameters.

        # --- Step 3: Make the second request (GET) with the form data ---
        print(f"   [*] Step 3: Requesting actual PDF from: {actual_download_url_base} with params")
        response_step2 = session.get(
            actual_download_url_base,
            params=form_data,        # Send hidden input data as URL parameters for GET
            stream=True,
            timeout=REQUEST_TIMEOUT_STEP2 # Longer timeout for actual download
        )
        response_step2.raise_for_status()

        content_type_step2 = response_step2.headers.get('content-type', '').lower()
        if 'application/pdf' not in content_type_step2:
            print(f"   [!] Failed Step 3: Expected PDF, but got '{content_type_step2}'.")
            # Save the response for debugging
            debug_html_path = output_path_str + ".download.html"
            try:
                 with open(debug_html_path, "w", encoding='utf-8') as f_html:
                      f_html.write(response_step2.text[:5000]) # Save beginning of text content
                 print(f"   [*] Saved unexpected response for debugging: {os.path.basename(debug_html_path)}")
            except Exception as e:
                 print(f"   [!] Could not save debug response: {e}")
            return False

        # Save the PDF content
        with open(output_path_str, 'wb') as f:
            shutil.copyfileobj(response_step2.raw, f)

        file_size = os.path.getsize(output_path_str)
        if file_size < 1000:
            print(f"   [!] Warning: Downloaded file '{os.path.basename(output_path_str)}' is very small ({file_size} bytes).")
        else:
            print(f"   [*] Step 3: Successfully saved PDF: {os.path.basename(output_path_str)} ({file_size // 1024} KB)")
        return True # Success!

    except requests.exceptions.Timeout as e:
        print(f"   [!] Failed: Request timed out. Step 1 timeout={REQUEST_TIMEOUT_STEP1}s, Step 2 timeout={REQUEST_TIMEOUT_STEP2}s")
        print(f"   [!] Timeout occurred on URL: {e.request.url}")
        return False
    except requests.exceptions.RequestException as e:
        step = "Step 1 (Render Page)" if "response_step1" not in locals() else "Step 3 (Actual Download)"
        print(f"   [!] Failed: Network or HTTP error during {step}: {e}")
        if e.response is not None:
             print(f"   [!] Status Code: {e.response.status_code}")
             # print(f"   [!] Response: {e.response.text[:200]}") # Uncomment for more debug info
        return False
    except Exception as e:
        print(f"   [!] Failed: An unexpected error occurred during two-step download:")
        print(traceback.format_exc())
        return False


def merge_pdfs(pdf_files, output_path_str):
    """Merges a list of PDF file paths into a single output PDF using PdfWriter."""
    if not pdf_files:
        print("[!] No valid PDF files were provided for merging.")
        return False

    writer = PdfWriter() # Use PdfWriter instead of PdfMerger
    print(f"\n[*] Merging {len(pdf_files)} downloaded PDF files into {os.path.basename(output_path_str)}...")
    valid_pdfs_appended = 0

    for pdf_file in pdf_files:
        # Basic checks before attempting to merge
        if not os.path.exists(pdf_file):
             print(f"   [!] Skipping merge for non-existent file: {os.path.basename(pdf_file)}")
             continue
        # Check file size more carefully - empty files cause errors
        if os.path.getsize(pdf_file) == 0:
            print(f"   [!] Skipping merge for zero-byte file: {os.path.basename(pdf_file)}")
            continue
        # Add a try-except block specifically for the append operation
        try:
             print(f"   [*] Appending: {os.path.basename(pdf_file)}")
             # Check read permissions (less likely in Colab, but good practice)
             if not os.access(pdf_file, os.R_OK):
                  print(f"   [!] Skipping merge for file without read permissions: {os.path.basename(pdf_file)}")
                  continue
             writer.append(pdf_file) # Use writer.append()
             valid_pdfs_appended += 1
        except Exception as e:
            # PdfWriter.append can raise errors on corrupted PDFs
            print(f"   [!] Error appending file {os.path.basename(pdf_file)}: {e}.")
            print(f"   [!] This might indicate a corrupted or malformed PDF download. Skipping this file.")
            # Consider logging the specific error e for more details if needed
            # print(traceback.format_exc())


    if valid_pdfs_appended > 0:
        try:
            print(f"[*] Writing final merged PDF ({valid_pdfs_appended} articles)...")
            with open(output_path_str, 'wb') as fout:
                writer.write(fout) # Use writer.write()
            writer.close() # Close the writer object
            print(f"[*] Merge complete. Output saved to: {os.path.basename(output_path_str)} in Colab environment.")
            return True
        except Exception as e:
             print(f"[!] Error writing final merged PDF: {e}")
             # Try closing the writer even if writing failed, might release resources
             try:
                 writer.close()
             except:
                 pass # Ignore errors during close after a write error
             return False
    else:
        print("[!] No valid PDFs were successfully appended for merging.")
        # No need to close writer if nothing was appended, but doesn't hurt
        try:
            writer.close()
        except:
            pass
        return False


# --- Main Execution Logic ---
print("--- Wikipedia Article PDF Downloader and Merger (Colab - Two-Step) ---")

# Display configuration
print(f"[*] Using User-Agent: {USER_AGENT}")
print(f"[*] Delay between articles: {DOWNLOAD_DELAY_SECONDS} seconds")

# --- Process Input URLs ---
urls = [line.strip() for line in wiki_urls_text.strip().split('\n') if line.strip() and not line.strip().startswith('#')]
if not urls:
    print("\n[!] No valid URLs found in the 'wiki_urls_text' variable. Please paste URLs and re-run.")
else:
    print(f"[*] Found {len(urls)} URLs to process.")

    # --- Setup Environment ---
    temp_path = Path(TEMP_DIR)
    output_path_str = str(OUTPUT_PDF_FILE)
    downloaded_pdf_paths = []
    merge_successful = False
    # Use a session for cookie persistence across the two steps for each article
    session = requests.Session()
    session.headers.update({
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,application/pdf,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    })


    try:
        temp_path.mkdir(exist_ok=True)
        print(f"[*] Using temporary directory: ./{temp_path.name}")

        # --- Download Phase ---
        for i, url in enumerate(urls):
            print(f"\n[{i+1}/{len(urls)}] Processing URL: {url}")
            render_url = get_pdf_render_url(url)
            if not render_url:
                continue # Skip invalid URLs

            try:
                article_name = unquote(urlparse(url).path.split('/wiki/', 1)[1]).replace('/','_')
                safe_filename = "".join([c for c in article_name if c.isalnum() or c in (' ', '.', '_', '-')]).rstrip()
                safe_filename = safe_filename[:100]
            except:
                safe_filename = f"article_{i+1}" # Fallback

            temp_filename = temp_path / f"wiki_{safe_filename}.pdf"
            temp_filename_str = str(temp_filename)

            # Call the new two-step download function, passing the session
            if download_pdf_two_step(render_url, temp_filename_str, session.headers, session):
                 if os.path.exists(temp_filename_str) and os.path.getsize(temp_filename_str) > 0:
                      downloaded_pdf_paths.append(temp_filename_str)
                 else:
                      print(f"   [!] Download function reported success, but file is missing or empty: {temp_filename_str}")
            else:
                 print(f"   [!] Skipping article due to download failure.")

            # Delay between processing ARTICLES
            print(f"   [*] Waiting {DOWNLOAD_DELAY_SECONDS} seconds before next article...")
            time.sleep(DOWNLOAD_DELAY_SECONDS)

        # --- Merge Phase ---
        if downloaded_pdf_paths:
            merge_successful = merge_pdfs(downloaded_pdf_paths, output_path_str)
        else:
             print("\n[!] No articles were successfully downloaded. Skipping merge.")


        # --- Colab Download Trigger ---
        if merge_successful and os.path.exists(output_path_str):
             final_size = os.path.getsize(output_path_str)
             print(f"\n[*] Final merged PDF '{OUTPUT_PDF_FILE}' created ({final_size // 1024} KB).")
             print(f"[*] Preparing file for download...")
             try:
                 files.download(output_path_str)
                 print(f"[*] Download initiated. Check your browser.")
             except Exception as e:
                  print(f"[!] Error triggering download: {e}. Manual download might be needed.")

        elif not downloaded_pdf_paths:
             print("\n[*] No file generated as no articles were downloaded.")
        else: # Merge failed
             print(f"\n[!] Merging failed or produced no output file. Cannot download {OUTPUT_PDF_FILE}.")


    except Exception as e:
        print(f"\n[!!!] An unexpected error occurred during the main script execution: {e}")
        print(traceback.format_exc())
    finally:
        # Close the session
        session.close()
        # --- Cleanup Phase ---
        if temp_path.exists():
            try:
                print(f"\n[*] Cleaning up temporary directory: ./{temp_path.name}")
                shutil.rmtree(temp_path)
                print("[*] Temporary files removed.")
            except Exception as e:
                print(f"[!] Warning: Error during cleanup: {e}")

print("\n--- Script execution finished ---")