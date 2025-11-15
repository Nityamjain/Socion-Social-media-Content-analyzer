import json
import os
import requests
import difflib
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

CACHE_FILE = "hashtags_cache.json"
DATA_FILE = "hashtags_data.json"

CATEGORY_MAP = {
    "ai": "technology",
    "machine learning": "technology",
    "ml": "technology",
    "fitness": "health",
    "gym": "health",
    "yoga": "health",
    "travel": "lifestyle",
    "food": "lifestyle",
    "fashion": "lifestyle",
    "startup": "business",
    "marketing": "business",
    "crypto": "finance",
    "stocks": "finance",
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/',
}

REFRESH_DAYS = 7

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def load_hashtag_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_keyword(keyword):
    return CATEGORY_MAP.get(keyword.lower().strip(), keyword.lower().strip())

def find_closest_match(target, options, cutoff=0.6):
    matches = difflib.get_close_matches(target, options, n=1, cutoff=cutoff)
    return matches[0] if matches else None

def scrape_best_hashtags(keyword):
    url = f"https://best-hashtags.com/hashtag/{keyword.replace(' ', '')}/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            hashtag_div = soup.find('div', class_='tag-box tag-box-v3 margin-bottom-40')
            print (hashtag_div)
            if hashtag_div:
                tags_text = hashtag_div.get_text(separator=" ", strip=True)
                hashtags = re.findall(r"#\w+", tags_text)
                if not hashtags:
                    words = tags_text.split()
                    hashtags = [f"#{w}" if not w.startswith("#") else w for w in words]
                print(f"Found {len(hashtags)} hashtags for '{keyword}'")
                return hashtags
            else:
                print("Hashtag div not found")
        else:
            print(f"Failed to retrieve: {response.status_code}")
    except Exception as e:
        print("Exception in scrape_best_hashtags:", e)
    return []

def get_hashtags_from_data(category, keyword):
    data = load_hashtag_data()
    category_lower = category.lower().strip() if category else ""
    keyword_lower = keyword.lower().strip() if keyword else ""

    categories = list(data.keys())
    matched_category = None
    matched_keyword = None

    # Find category match if category given
    if category_lower:
        matched_category = category_lower if category_lower in categories else find_closest_match(category_lower, categories)

    # If category found
    if matched_category:
        keywords = list(data[matched_category].keys())
        # If keyword given find keyword match, else return all hashtags under category
        if keyword_lower:
            matched_keyword = keyword_lower if keyword_lower in keywords else find_closest_match(keyword_lower, keywords)
        else:
            all_tags = []
            for kw in keywords:
                all_tags.extend(data[matched_category][kw])
            return list(set(all_tags))  # unique hashtags

        if matched_keyword:
            return data[matched_category][matched_keyword]
        else:
            print(f"No matching keyword found '{keyword}' in category '{matched_category}'.")
            return []

    # If no category match but keyword given: search keyword across all categories
    if keyword_lower and not matched_category:
        for cat in categories:
            keywords = list(data[cat].keys())
            if keyword_lower in keywords:
                return data[cat][keyword_lower]
            else:
                close_kw = find_closest_match(keyword_lower, keywords)
                if close_kw:
                    return data[cat][close_kw]

    print("No matching category or keyword found in offline data.")
    return []

def scrape_hashtags(keyword, category=""):
    keyword = keyword.strip() if keyword else ""
    category = category.strip() if category else ""

    if keyword:
        hashtags = scrape_best_hashtags(keyword)
        if hashtags:
            return hashtags
        else:
            print(f"Scraping failed for keyword '{keyword}', falling back to offline data.")
    else:
        print("No keyword provided for scraping.")

    # Fallback if category or keyword exists
    if category or keyword:
        return get_hashtags_from_data(category, keyword)
    else:
        print("No keyword or category provided, cannot retrieve hashtags.")
        return []

def get_hashtags(category, keyword):
    cache = load_cache()
    norm_category = category.lower().strip() if category else ""
    norm_keyword = normalize_keyword(keyword) if keyword else ""

    # Use category or keyword or "default" for cache key to avoid key errors
    cache_cat_key = norm_category if norm_category else "default_category"
    cache_key_key = norm_keyword if norm_keyword else "default_keyword"

    if cache_cat_key not in cache:
        cache[cache_cat_key] = {}

    # Preference logic: use category if available else keyword
    key_to_use = cache_cat_key
    subkey_to_use = ""

    if norm_category:
        # If category present, use category key
        subkey_to_use = ""  # empty string as subkey to get all keywords under this category or handle below
        # Check if empty string subkey exists in cache, else use fallback below
        if "" not in cache[cache_cat_key]:
            # Prepare to fetch all hashtags under the category
            # We'll handle this by modifying get_hashtags_from_data call if subkey is empty
            subkey_to_use = None
        else:
            subkey_to_use = ""

    elif norm_keyword:
        # If no category, use keyword in default category or keyword cache
        key_to_use = "default_category"
        subkey_to_use = norm_keyword
    else:
        # Neither category nor keyword
        key_to_use = "default_category"
        subkey_to_use = "default_keyword"

    # Check cache for preferred keys
    if subkey_to_use is not None and subkey_to_use in cache.get(key_to_use, {}):
        entry = cache[key_to_use][subkey_to_use]
        last_update = datetime.fromisoformat(entry["last_updated"])
        if datetime.now() - last_update < timedelta(days=REFRESH_DAYS):
            print(f"Using cached hashtags for category '{key_to_use}', keyword '{subkey_to_use}'")
            return entry["hashtags"]

    # If no cached entry or expired, scrape fresh using category or keyword prioritization
    if norm_category:
        hashtags = scrape_hashtags("", norm_category)  # Empty keyword, pass category
        if not hashtags and norm_keyword:
            # fallback to keyword if category scrape failed
            hashtags = scrape_hashtags(norm_keyword, "")
    elif norm_keyword:
        hashtags = scrape_hashtags(norm_keyword, "")
    else:
        print("No category or keyword provided, cannot retrieve hashtags.")
        return []

    # Cache updated hashtags under preferring storage key
    store_cat_key = key_to_use
    store_key_key = subkey_to_use if subkey_to_use is not None else ""

    if store_cat_key not in cache:
        cache[store_cat_key] = {}

    cache[store_cat_key][store_key_key] = {
        "last_updated": datetime.now().isoformat(),
        "hashtags": hashtags
    }
    save_cache(cache)
    return hashtags

    cache = load_cache()
    norm_category = category.lower().strip() if category else ""
    norm_keyword = normalize_keyword(keyword) if keyword else ""

    # Use category or keyword or "default" for cache key to avoid key errors
    cache_cat_key = norm_category if norm_category else "default_category"
    cache_key_key = norm_keyword if norm_keyword else "default_keyword"

    if cache_cat_key not in cache:
        cache[cache_cat_key] = {}

    if cache_key_key in cache[cache_cat_key]:
        entry = cache[cache_cat_key][cache_key_key]
        last_update = datetime.fromisoformat(entry["last_updated"])
        if datetime.now() - last_update < timedelta(days=REFRESH_DAYS):
            print(f"Using cached hashtags for category '{cache_cat_key}', keyword '{cache_key_key}'")
            return entry["hashtags"]

    print(f"Fetching fresh hashtags for category '{cache_cat_key}', keyword '{cache_key_key}'")
    hashtags = scrape_hashtags(keyword, norm_category)
    cache[cache_cat_key][cache_key_key] = {
        "last_updated": datetime.now().isoformat(),
        "hashtags": hashtags
    }
    save_cache(cache)
    return hashtags

# Test
if __name__ == "__main__":
    category = input("Category (or leave blank): ").strip()
    keyword = input("Keyword (or leave blank): ").strip()
    hashtags = get_hashtags(category, keyword)
    if hashtags:
        print("Hashtags:", " ".join(hashtags))
    else:
        print("No hashtags found.")
