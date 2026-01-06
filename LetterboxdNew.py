import requests
from bs4 import BeautifulSoup
import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
import logging
from pathlib import Path
import concurrent.futures
from datetime import datetime

class FilmScraper:
    def __init__(self, use_selenium=True, browser='chrome', debug=False):
        self.use_selenium = use_selenium
        self.browser_type = browser
        self.session = requests.Session()
        self.browser = None
        self.debug = debug
        
        # Setup logging
        if debug:
            logging.basicConfig(level=logging.INFO, 
                                format='%(asctime)s - %(levelname)s - %(message)s')
            self.logger = logging.getLogger(__name__)
        
        # Set up requests session with headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.5',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        if use_selenium:
            self.setup_browser()

    def setup_browser(self):
        """Set up browser with fallback options"""
        try:
            if self.browser_type == 'chrome':
                self.browser = self._setup_chrome()
            else:
                self.browser = self._setup_firefox()
        except Exception as e:
            print(f"Failed to set up {self.browser_type}: {e}")
            try:
                if self.browser_type == 'chrome':
                    print("Trying Firefox as fallback...")
                    self.browser = self._setup_firefox()
                else:
                    print("Trying Chrome as fallback...")
                    self.browser = self._setup_chrome()
            except Exception as e2:
                print(f"Failed to set up fallback browser: {e2}")
                print("Falling back to requests-only mode...")
                self.use_selenium = False
                self.browser = None

    def _setup_chrome(self):
        """Set up Chrome browser"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def _setup_firefox(self):
        """Set up Firefox browser"""
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        firefox_options.set_preference("dom.webnotifications.enabled", False)
        firefox_options.set_preference("media.volume_scale", "0.0")
        
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=firefox_options)

    def get_page_content(self, url, retries=3):
        """Get page content using available method"""
        if not url or url == 'None' or not isinstance(url, str):
            return None
            
        if not url.startswith(('http://', 'https://')):
            return None
            
        for attempt in range(retries):
            try:
                if self.use_selenium and self.browser:
                    return self._get_content_selenium(url)
                else:
                    return self._get_content_requests(url)
            except Exception as e:
                if self.debug:
                    print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    delay = (2 ** attempt) + random.uniform(1, 3)
                    time.sleep(delay)
                else:
                    return None
        return None

    def _get_content_selenium(self, url):
        """Get content using Selenium with better error handling and waits"""
        self.browser.get(url)
        
        try:
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.filmtitle"))
            )
            
            try:
                WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".film-poster[data-average-rating], .average-rating, meta[property='letterboxd:average_rating']"))
                )
            except Exception:
                pass
            
            time.sleep(1)
            
        except Exception as e:
            if self.debug:
                print(f"Waited 10 seconds for elements, but they weren't found: {e}")
        
        return self.browser.page_source

    def _get_content_requests(self, url):
        """Get content using requests with better error handling"""
        response = self.session.get(url, timeout=15)
        response.raise_for_status()
        return response.text

    def scrape_film_details(self, film_url):
        """Scrape detailed information from a single film page"""
        if not film_url or film_url == 'None' or not isinstance(film_url, str):
            return self.create_minimal_film_data(film_url or "Invalid URL", "Invalid or missing URL")
            
        print(f"Scraping: {film_url}")
        
        html = self.get_page_content(film_url)
        if not html:
            return self.create_minimal_film_data(film_url, "Failed to get page content")
        
        soup = BeautifulSoup(html, 'html.parser')
        
        page_title = soup.select_one("title")
        has_film_title = page_title and ("directed by" in page_title.get_text() or "Letterboxd" in page_title.get_text())
        has_film_elements = soup.select_one("h1") or soup.select_one(".film-header")
        
        if not has_film_title and not has_film_elements:
            return self.create_minimal_film_data(film_url, "Invalid page structure")
        
        film_data = {
            'url': film_url,
            'title': self.extract_title(soup),
            'release_date': self.extract_release_date(soup),
            'runtime': self.extract_runtime(soup),
            'genres': self.extract_genres(soup),
            'directors': self.extract_directors(soup),
            'actors': self.extract_actors(soup),
            'studios': self.extract_studios(soup),
            'language': self.extract_language(soup),
            'country': self.extract_country(soup),
            'writers': self.extract_writers(soup),
            'composer': self.extract_composer(soup),
            'cinematographer': self.extract_cinematographer(soup),
            'average_rating': self.extract_average_rating(soup),
            'description': self.extract_description(soup),
            'scrape_status': 'success',
            'last_scraped': datetime.now().isoformat()
        }
        
        return film_data

    def extract_title(self, soup):
        """Extract film title with multiple selectors"""
        page_title = soup.select_one("title")
        if page_title:
            full_title = page_title.get_text().strip()
            if " directed by " in full_title and "• Letterboxd" in full_title:
                film_title = full_title.split(" directed by ")[0].strip()
                film_title = ''.join(char for char in film_title if char.isprintable()).strip()
                if film_title and film_title != "Letterboxd":
                    return self._remove_year_from_title(film_title)
            elif " • Letterboxd" in full_title:
                film_title = full_title.split(" • Letterboxd")[0].strip()
                if film_title and film_title != "Letterboxd":
                    return self._remove_year_from_title(film_title)
        
        selectors = [
            "h1.headline-1.filmtitle",
            "h1.filmtitle",  
            "section.film-header h1",
            ".film-header h1",
            "h1.headline-1"
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text().strip()
                if title and title != "Letterboxd — Your life in film" and len(title) > 1:
                    return self._remove_year_from_title(title)
        
        h1_elements = soup.select("h1")
        for h1 in h1_elements:
            title = h1.get_text().strip()
            if (title and 
                title != "Letterboxd — Your life in film" and 
                "Add" not in title and 
                "to lists" not in title and
                len(title) > 3):
                return self._remove_year_from_title(title)
        
        return "Unknown Title"

    def _remove_year_from_title(self, title):
        """Remove year in parentheses from title"""
        return re.sub(r'\s*\(\d{4}\)\s*$', '', title).strip()

    def extract_release_date(self, soup):
        """Extract release date/year"""
        selectors = [
            "div.releaseyear a",
            ".releaseyear",
            "small.number a",
            "[href*='/films/year/']"
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                year = elem.get_text().strip()
                if year and year.isdigit():
                    return year
        
        text = soup.get_text()
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if year_match:
            return year_match.group()
        
        return None

    def extract_runtime(self, soup):
        """Extract runtime"""
        time_elem = soup.find("time", {"class": "u-slug", "datetime": True})
        if time_elem:
            return time_elem.get_text(strip=True)

        selectors = [
            "a[href*='/runtime/']",
            ".film-facts .text-slug",
            ".film-facts .runtime",
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                runtime_text = elem.get_text(strip=True)
                match = re.search(r'(\d+)\s*mins', runtime_text)
                if match:
                    return match.group(0)

        text_content = soup.get_text()
        match = re.search(r'(\d+)\s*mins', text_content, re.IGNORECASE)
        if match:
            return match.group(0)
        
        return None

    def extract_genres(self, soup):
        """Extract genres"""
        genres = []
        selectors = [
            "div#tab-genres a[href*='/films/genre/']",
            "a[href*='/films/genre/']",
            ".text-slug[href*='/genre/']"
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                genre = link.get_text().strip()
                if genre and len(genre) > 1 and genre not in genres:
                    genres.append(genre)
        
        return genres[:10]

    def extract_directors(self, soup):
        """Extract first 2 directors"""
        directors = []
        selectors = [
            "a[href*='/director/']",
            "a[href*='/person/'][title*='Director']",
            ".text-slug[href*='/director/']"
        ]
        
        for selector in selectors:
            links = soup.select(selector)[:2]
            for link in links:
                director = link.get_text().strip()
                if director and director not in directors:
                    directors.append(director)
        
        return directors[:2]

    def extract_actors(self, soup):
        """Extract first 10 actors"""
        actors = []
        
        cast_section = soup.select_one("div#tab-cast, .cast-list")
        if cast_section:
            links = cast_section.select("a")[:10]
        else:
            links = soup.select("a[href*='/actor/'], a[href*='/person/']")[:10]
        
        for link in links:
            actor = link.get_text().strip()
            if actor and len(actor) > 1 and actor not in actors:
                actors.append(actor)
        
        return actors[:10]

    def extract_studios(self, soup):
        """Extract studios"""
        studios = []
        links = soup.select("a[href*='/films/studio/'], a[href*='/studio/']")
        
        for link in links:
            studio = link.get_text().strip()
            if studio and studio not in studios:
                studios.append(studio)
        
        return studios

    def extract_language(self, soup):
        """Extract primary language"""
        link = soup.select_one("a[href*='/films/language/'], a[href*='/language/']")
        return link.get_text().strip() if link else None

    def extract_country(self, soup):
        """Extract countries"""
        countries = []
        links = soup.select("a[href*='/films/country/'], a[href*='/country/']")
        
        for link in links:
            country = link.get_text().strip()
            if country and country not in countries and len(country) > 2 and country != "Country":
                countries.append(country)
        
        return countries

    def extract_writers(self, soup):
        """Extract first 2 writers"""
        writers = []
        links = soup.select("a[href*='/writer/']")[:2]
        
        for link in links:
            writer = link.get_text().strip()
            if writer:
                writers.append(writer)
        
        return writers

    def extract_composer(self, soup):
        """Extract composer"""
        link = soup.select_one("a[href*='/composer/']")
        return link.get_text().strip() if link else None

    def extract_cinematographer(self, soup):
        """Extract cinematographer"""
        link = soup.select_one("a[href*='/cinematography/']")
        return link.get_text().strip() if link else None
    
    def extract_average_rating(self, soup):
        """Extract average community rating"""
        selectors = [
            ".average-rating .rating",
            ".film-stats .rating",
            ".rating .average-rating",
            "[data-average-rating]",
            ".average-rating",
            ".film-poster[data-average-rating]"
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                avg_rating = elem.get('data-average-rating')
                if avg_rating:
                    return avg_rating
                
                rating_text = elem.get_text().strip()
                rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                if rating_match:
                    return rating_match.group(1)
        
        return None

    def extract_description(self, soup):
        """Extract film description"""
        selectors = [
            ".review .body-text",
            ".film-synopsis .body-text",  
            ".truncate p",
            "[data-truncate] p"
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                desc = elem.get_text().strip()
                if desc and len(desc) > 10:
                    return desc[:500] + "..." if len(desc) > 500 else desc
        
        return None

    def create_minimal_film_data(self, film_url, error_message):
        """Create minimal film data when scraping fails"""
        if film_url and film_url != 'None' and '/' in str(film_url):
            title = str(film_url).split('/')[-2].replace('-', ' ').title()
        else:
            title = 'Unknown'
            
        return {
            'url': film_url,
            'title': title,
            'release_date': None,
            'runtime': None,
            'genres': [],
            'directors': [],
            'actors': [],
            'studios': [],
            'language': None,
            'country': [],
            'writers': [],
            'composer': None,
            'cinematographer': None,
            'average_rating': None,
            'description': None,
            'scrape_status': f'failed: {error_message}',
            'last_scraped': datetime.now().isoformat()
        }

    def scrape_all_films(self, all_films, max_films=None, start_index=0):
        """Scrape details for all films in the list"""
        detailed_films = []
        
        valid_films = []
        invalid_count = 0
        
        for film in all_films:
            if film and isinstance(film, dict) and film.get('url') and film['url'] != 'None':
                valid_films.append(film)
            else:
                invalid_count += 1
        
        print(f"Found {len(valid_films)} valid films out of {len(all_films)} total films")
        if invalid_count > 0:
            print(f"Skipped {invalid_count} films with invalid URLs")
        
        try:
            films_to_process = valid_films[start_index:start_index + max_films] if max_films else valid_films[start_index:]
            
            for idx, film in enumerate(films_to_process, start=start_index + 1):
                print(f"\n[{idx}/{len(valid_films)}] Processing: {film.get('title', 'Unknown')}")
                
                film_details = self.scrape_film_details(film['url'])
                if film_details:
                    detailed_films.append(film_details)
                    if film_details.get('scrape_status') == 'success':
                        print(f"✓ Successfully scraped: {film_details['title']}")
                        if film_details.get('average_rating'):
                            print(f"  Rating: {film_details['average_rating']}/5")
                    else:
                        print(f"⚠ Partially scraped: {film_details['title']} - {film_details.get('scrape_status')}")
                
                time.sleep(random.uniform(2, 4))
                
                if self.use_selenium and self.browser and idx % 100 == 0:
                    print("Refreshing browser...")
                    self.browser.quit()
                    self.setup_browser()
                    
        except KeyboardInterrupt:
            print("\nScraping interrupted by user. Saving current progress...")
        except Exception as e:
            print(f"Critical error during scraping: {e}")
        finally:
            self.cleanup()
        
        return detailed_films

    def save_progress(self, films, filename):
        """Save current progress to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(films, f, indent=2, ensure_ascii=False)
        print(f"Progress saved: {len(films)} films to {filename}")

    def cleanup(self):
        """Clean up resources"""
        if self.browser:
            self.browser.quit()
        if hasattr(self.session, 'close'):
            self.session.close()


def load_existing_data(username):
    """Load existing scraped data if available"""
    filename = f'{username}_detailed_films.json'
    if Path(filename).exists():
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ Loaded existing data: {len(data)} films")
            return data
        except Exception as e:
            print(f"Error loading existing data: {e}")
            return []
    return []


def get_scraped_urls(existing_data):
    """Extract URLs from existing scraped data"""
    return {film['url'] for film in existing_data if film.get('url')}


def merge_film_data(existing_films, new_films):
    """Merge existing and new film data, updating existing entries"""
    # Create a dict of existing films by URL for quick lookup
    films_dict = {film['url']: film for film in existing_films}
    
    # Update with new data
    for film in new_films:
        films_dict[film['url']] = film
    
    # Return as list, sorted by title
    return sorted(films_dict.values(), key=lambda x: x.get('title', '').lower())


def collect_all_films(username="Agendia", max_pages=None):
    """Collect all films from a Letterboxd profile using parallel workers"""
    session_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.5',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    base = f"https://letterboxd.com/{username}/films/page/"

    def fetch_page(url):
        try:
            resp = requests.get(url, headers=session_headers, timeout=12)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def parse_films_from_html(html):
        if not html:
            return []
        soup = BeautifulSoup(html, 'html.parser')
        films = []

        film_containers = soup.select("div.react-component[data-component-class='LazyPoster']")
        if not film_containers:
            film_containers = soup.select("li.poster-container")
        if not film_containers:
            film_containers = soup.select("li[data-film-id]")

        for film_container in film_containers:
            link_tag = film_container.select_one("a.frame")
            if not link_tag:
                link_tag = film_container.select_one("div.film-poster a")
            if not link_tag:
                link_tag = film_container.select_one("a")

            if link_tag and link_tag.get('href'):
                film_url = "https://letterboxd.com" + link_tag.get('href')
                title = None
                if film_container.get('data-item-name'):
                    title = film_container.get('data-item-name')
                elif link_tag.get('data-original-title'):
                    title = link_tag.get('data-original-title')
                elif link_tag.get('title'):
                    title = link_tag.get('title')
                elif film_container.select_one('img'):
                    title = film_container.select_one('img').get('alt')
                else:
                    title = link_tag.get_text().strip()

                if film_url and title:
                    films.append({'title': title, 'url': film_url})

        return films

    # Fetch first page to detect total pages
    first_page_url = base + '1/'
    first_html = fetch_page(first_page_url)
    if not first_html:
        print('Failed to fetch first page; aborting')
        return []

    first_soup = BeautifulSoup(first_html, 'html.parser')

    # Detect total pages
    total_pages = 1
    try:
        page_links = first_soup.select('a[href*="/films/page/"]')
        nums = []
        for a in page_links:
            href = a.get('href') or ''
            m = re.search(r'/page/(\d+)/', href)
            if m:
                nums.append(int(m.group(1)))
        if nums:
            total_pages = max(nums)
    except Exception:
        total_pages = 1

    if max_pages:
        total_pages = min(total_pages, max_pages)

    print(f"Detected {total_pages} pages to fetch")

    page_urls = [f"{base}{i}/" for i in range(1, total_pages + 1)]

    all_films = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as exc:
        future_to_url = {exc.submit(fetch_page, url): url for url in page_urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            html = future.result()
            films = parse_films_from_html(html)
            if films:
                print(f"{url} -> found {len(films)} films")
                all_films.extend(films)

    # Deduplicate by URL
    seen = set()
    unique_films = []
    for f in all_films:
        if f['url'] not in seen:
            seen.add(f['url'])
            unique_films.append(f)

    print(f"Total unique films collected: {len(unique_films)}")
    
    # Selenium fallback if needed
    if len(unique_films) == 0:
        print("No films found via requests; falling back to Selenium...")
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            service = Service(ChromeDriverManager().install())
            browser = webdriver.Chrome(service=service, options=chrome_options)

            selenium_films = []
            for i in range(1, total_pages + 1):
                page_url = f"{base}{i}/"
                print(f"Selenium fetching {page_url}")
                try:
                    browser.get(page_url)
                    WebDriverWait(browser, 8).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.react-component[data-component-class='LazyPoster']"))
                    )
                except Exception:
                    time.sleep(3)

                html = browser.page_source
                films = parse_films_from_html(html)
                if films:
                    print(f"{page_url} -> found {len(films)} films (selenium)")
                    selenium_films.extend(films)

            try:
                browser.quit()
            except Exception:
                pass

            # Deduplicate selenium results
            seen2 = set()
            unique2 = []
            for f in selenium_films:
                if f['url'] not in seen2:
                    seen2.add(f['url'])
                    unique2.append(f)

            print(f"Total unique films collected (selenium): {len(unique2)}")
            return unique2
        except Exception as e:
            print(f"Selenium fallback failed: {e}")

    return unique_films


def display_film_details(film):
    """Display film details in a readable format"""
    print(f"\nTitle: {film['title']}")
    print(f"Release Year: {film['release_date']}")
    print(f"Runtime: {film.get('runtime', 'N/A')}")
    print(f"Average Rating: {film.get('average_rating', 'N/A')}/5")
    print(f"Genres: {', '.join(film['genres']) if film['genres'] else 'N/A'}")
    print(f"Directors: {', '.join(film['directors']) if film['directors'] else 'N/A'}")
    print(f"Actors: {', '.join(film['actors'][:10]) if film['actors'] else 'N/A'}")
    print(f"Studios: {', '.join(film['studios']) if film['studios'] else 'N/A'}")
    print(f"Language: {film['language'] or 'N/A'}")
    print(f"Country: {', '.join(film['country']) if film['country'] else 'N/A'}")
    print(f"Writers: {', '.join(film['writers']) if film['writers'] else 'N/A'}")
    print(f"Composer: {film['composer'] or 'N/A'}")
    print(f"Cinematographer: {film['cinematographer'] or 'N/A'}")
    if film.get('description'):
        print(f"Description: {film['description'][:200]}...")
    print(f"Status: {film.get('scrape_status', 'unknown')}")
    print(f"Last Scraped: {film.get('last_scraped', 'N/A')}")
    print(f"URL: {film['url']}")
    print("-" * 80)


def main():
    try:
        # Prompt for username
        username = input("Enter Letterboxd username: ").strip()
        if not username:
            print("Error: Username cannot be empty!")
            return

        # Load existing data
        existing_films = load_existing_data(username)
        existing_urls = get_scraped_urls(existing_films)
        
        print(f"\n{'='*50}")
        print(f"INCREMENTAL SCRAPING MODE")
        print(f"{'='*50}")
        print(f"Existing films in database: {len(existing_films)}")
        print(f"Existing URLs tracked: {len(existing_urls)}")
        
        # Step 1: Collect all films from profile
        print(f"\n{'='*50}")
        print(f"Collecting current film list from profile: {username}")
        print(f"{'='*50}")
        all_films = collect_all_films(username)
        
        # Save the collected films list
        with open('collected_films.json', 'w', encoding='utf-8') as f:
            json.dump(all_films, f, indent=2, ensure_ascii=False)
        print(f"Film list saved to 'collected_films.json'")
        
        if not all_films:
            print("No films collected. Please check the username and try again.")
            return
        
        # Step 2: Identify new films
        new_films = [film for film in all_films if film['url'] not in existing_urls]
        
        print(f"\n{'='*50}")
        print(f"COMPARISON RESULTS")
        print(f"{'='*50}")
        print(f"Total films on profile: {len(all_films)}")
        print(f"Previously scraped: {len(existing_films)}")
        print(f"New films to scrape: {len(new_films)}")
        
        if len(new_films) == 0:
            print("\n✓ No new films found! Your database is up to date.")
            print(f"All {len(all_films)} films are already in your database.")
            
            # Ask if user wants to re-scrape everything
            rescrape = input("\nWould you like to re-scrape all films anyway? (yes/no): ").strip().lower()
            if rescrape not in ['yes', 'y']:
                print("Exiting without scraping.")
                return
            else:
                print("\nRe-scraping all films...")
                new_films = all_films
        else:
            print(f"\n{'='*50}")
            print(f"NEW FILMS TO SCRAPE:")
            print(f"{'='*50}")
            for idx, film in enumerate(new_films[:10], 1):
                print(f"{idx}. {film.get('title', 'Unknown')}")
            if len(new_films) > 10:
                print(f"... and {len(new_films) - 10} more")
        
        # Step 3: Scrape new films
        print(f"\n{'='*50}")
        print(f"STARTING SCRAPE")
        print(f"{'='*50}")
        
        scraper = FilmScraper(use_selenium=True, browser='chrome', debug=True)
        newly_scraped = scraper.scrape_all_films(new_films)
        
        # Step 4: Merge with existing data
        print(f"\n{'='*50}")
        print(f"MERGING DATA")
        print(f"{'='*50}")
        all_detailed_films = merge_film_data(existing_films, newly_scraped)
        
        # Step 5: Save merged results (full detailed backup)
        output_filename = f'{username}_detailed_films.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_detailed_films, f, indent=2, ensure_ascii=False)

        # Also save a minimal export with only the requested fields
        minimal_fields = []
        for film in all_detailed_films:
            minimal_fields.append({
                'title': film.get('title'),
                'release_year': film.get('release_date'),
                'runtime': film.get('runtime'),
                'average_rating': film.get('average_rating'),
                'genres': film.get('genres'),
                'directors': film.get('directors'),
                'actors': film.get('actors'),
                'studios': film.get('studios'),
                'language': film.get('language'),
                'country': film.get('country'),
                'writers': film.get('writers'),
                'composer': film.get('composer'),
                'cinematographer': film.get('cinematographer'),
                'description': film.get('description'),
                'url': film.get('url')
            })

        minimal_filename = f'{username}_films_minimal.json'
        with open(minimal_filename, 'w', encoding='utf-8') as f:
            json.dump(minimal_fields, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*50}")
        print(f"SCRAPING COMPLETE!")
        print(f"{'='*50}")
        print(f"Newly scraped films: {len(newly_scraped)}")
        print(f"Total films in database: {len(all_detailed_films)}")
        print(f"Full results saved to '{output_filename}'")
        print(f"Minimal export saved to '{minimal_filename}' (contains title, year, runtime, rating, genres, directors, actors, studios, language, country, writers, composer, cinematographer, description, url)")
        
        # Step 7: Show statistics
        print(f"\n{'='*50}")
        print(f"FINAL STATISTICS")
        print(f"{'='*50}")
        
        successful = sum(1 for f in all_detailed_films if f.get('scrape_status') == 'success')
        failed = len(all_detailed_films) - successful
        with_ratings = sum(1 for f in all_detailed_films if f.get('average_rating'))
        
        print(f"Total films: {len(all_detailed_films)}")
        print(f"Successfully scraped: {successful}")
        print(f"Failed/Partial: {failed}")
        print(f"Films with ratings: {with_ratings}")
        
        if with_ratings > 0:
            avg_rating = sum(float(f['average_rating']) for f in all_detailed_films if f.get('average_rating')) / with_ratings
            print(f"Average rating across collection: {avg_rating:.2f}/5")
            
    except Exception as e:
        print(f"Error in main function: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()