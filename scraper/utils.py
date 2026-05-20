import json
import os
from urllib.parse import quote

# ============================================================
#  SHARED SETTINGS
# ============================================================

LOCATION  = 'amsterdam' 
PRICE_MIN = None
PRICE_MAX = 700000
AREA_MIN  = 75

NEIGHBOURHOODS = []

# ============================================================
#  SHARED PROPERTY FILTERS
# ============================================================

REQUIRE_BALCONY_OR_ROOF_TERRACE = True
NOT_FIRST_FLOOR                 = True
SINGLE_STORY                    = True

# ============================================================
#  SHARED HELPERS
# ============================================================

def build_pararius_buy_search_url(self, city, price_min=None, price_max=None,
                                  area_min=None, bedrooms=None, interior=None,
                                  sort=None, page=1):
    """Monkey-patch for pypararius to search Dutch buy listings instead of rentals."""
    parts = [f'https://www.pararius.nl/koopwoningen/{city}']
    if price_min is not None or price_max is not None:
        p_min = price_min or 0
        p_max = price_max or 0
        if p_min > 0 or p_max > 0:
            parts.append(f'{p_min}-{p_max}')
    if area_min is not None and area_min > 0:
        parts.append(f'{area_min}m2')
    if page > 1:
        parts.append(f'page-{page}')
    if sort is not None:
        sort_map = {'newest': '', 'price_asc': 'sort-price-low',
                    'price_desc': 'sort-price-high'}
        sort_val = sort_map.get(sort, '')
        if sort_val:
            parts.append(sort_val)
    return '/'.join(parts)

LISTINGS_KOOP_FILE = '/data/listings_koop.json'
LISTINGS_HUUR_FILE = '/data/listings_huur.json'

def load_listings(category):
    path = LISTINGS_KOOP_FILE if category == 'koop' else LISTINGS_HUUR_FILE
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []

def save_listings(new_listings, category):
    """Append new matched listings to the appropriate listings file, avoiding duplicates by URL."""
    from datetime import datetime
    path = LISTINGS_KOOP_FILE if category == 'koop' else LISTINGS_HUUR_FILE
    print(f"[save_listings] Writing {len(new_listings)} listings to {path}")
    existing = load_listings(category)
    existing_urls = {l['url'] for l in existing}
    for listing in new_listings:
        if listing['url'] not in existing_urls:
            listing['found_at'] = datetime.now().isoformat()
            existing.append(listing)
            existing_urls.add(listing['url'])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(existing, f, indent=2)

def load_seen(seen_file):
    if os.path.exists(seen_file):
        with open(seen_file) as f:
            return set(json.load(f))
    return set()

def save_seen(seen, seen_file):
    os.makedirs(os.path.dirname(seen_file), exist_ok=True)
    with open(seen_file, 'w') as f:
        json.dump(list(seen), f)

def build_maps_url(lat=None, lng=None, title=None, city=None):
    if lat and lng:
        return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
    if title and city:
        return f"https://www.google.com/maps/search/?api=1&query={quote(f'{title}, {city}, Netherlands')}"
    return ''