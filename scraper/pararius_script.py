import pypararius.pararius as _pararius_module
from pypararius import Pararius
from utils import LOCATION, PRICE_MIN, PRICE_MAX, AREA_MIN, NEIGHBOURHOODS, REQUIRE_BALCONY_OR_ROOF_TERRACE, NOT_FIRST_FLOOR, SINGLE_STORY, load_seen, save_seen, build_maps_url, build_pararius_buy_search_url

# Patch pypararius to use the Dutch pararius.nl domain
_pararius_module.BASE_URL = 'https://www.pararius.nl'

# ============================================================
#  SCRIPT
# ============================================================

def matches_full_listing(r, full):
    chars = full.get('characteristics') or {}

    if NEIGHBOURHOODS:
        neighbourhood = full.get('neighbourhood', '').lower()
        if not any(n in neighbourhood for n in NEIGHBOURHOODS):
            return False, f"neighbourhood '{neighbourhood}' not in list"

    if REQUIRE_BALCONY_OR_ROOF_TERRACE:
        balkon    = chars.get('Balkon', '').lower()
        dakterras = chars.get('Dakterras', '').lower()
        has_balkon    = 'aanwezig' in balkon    and 'niet aanwezig' not in balkon
        has_dakterras = 'aanwezig' in dakterras and 'niet aanwezig' not in dakterras
        if not has_balkon and not has_dakterras:
            return False, f"no balcony or roof terrace (Balkon: {balkon}, Dakterras: {dakterras})"

    if NOT_FIRST_FLOOR:
        verdieping = chars.get('Verdieping', '').strip()
        if verdieping and (verdieping == '0' or 'begane grond' in verdieping.lower()):
            return False, f"ground floor (Verdieping: {verdieping})"

    if SINGLE_STORY:
        aantal_woonlagen = chars.get('Aantal woonlagen', '').strip()
        if aantal_woonlagen and aantal_woonlagen != '1':
            return False, f"not single storey (Aantal woonlagen: {aantal_woonlagen})"

    return True, "matches"

def get_new_listings(offering_type='buy'):
    # Patch search URL based on offering type
    if offering_type == 'buy':
        Pararius._build_search_url = build_pararius_buy_search_url
    else:
        Pararius._build_search_url = _build_pararius_rent_search_url

    seen_file = f'/data/seen_pararius_{offering_type}.json'
    seen = load_seen(seen_file)
    p    = Pararius()

    try:
        results = p.search_listing(
            location  = LOCATION,
            price_min = PRICE_MIN,
            price_max = PRICE_MAX,
            area_min  = AREA_MIN,
            sort      = 'newest',
        )
    except Exception as e:
        print(f"[Pararius] Search failed: {e}")
        return []

    print(f"[Pararius] Found {len(results)} results from search")

    new_listings = []
    for r in results:
        url = r.get('url', '')
        if not url or url in seen:
            continue
        seen.add(url)

        try:
            full = p.get_listing(url)
        except Exception as e:
            print(f"[Pararius] Could not fetch full listing for {r.get('title')}: {e}")
            continue

        passed, reason = matches_full_listing(r, full)
        if not passed:
            print(f"[Pararius] Skipped ({reason}): {r.get('title')}")
            continue

        chars = full.get('characteristics') or {}
        maps_url = build_maps_url(
            lat   = full.get('latitude') or r.get('latitude'),
            lng   = full.get('longitude') or r.get('longitude'),
            title = full.get('title', '') or r.get('title', ''),
            city  = full.get('city', '') or r.get('city', ''),
        )

        extra_parts = []
        balkon     = chars.get('Balkon', '')
        dakterras  = chars.get('Dakterras', '')
        verdieping = chars.get('Verdieping', '')
        woonlagen  = chars.get('Aantal woonlagen', '')
        if balkon:
            extra_parts.append(f"Balkon: {balkon}")
        if dakterras:
            extra_parts.append(f"Dakterras: {dakterras}")
        if verdieping:
            extra_parts.append(f"Verdieping: {verdieping}")
        elif NOT_FIRST_FLOOR:
            extra_parts.append("⚠️ verdieping onbekend")
        if woonlagen:
            extra_parts.append(f"Woonlagen: {woonlagen}")
        elif SINGLE_STORY:
            extra_parts.append("⚠️ woonlagen onbekend")
        extra_parts.append("⚠️ lift onbekend")
        extra_parts.append("⚠️ kamers onbekend")

        new_listings.append({
            'source':   'Pararius',
            'title':    full.get('title') or r.get('title', ''),
            'price':    f"EUR {full['price']:,}" if full.get('price') else "price unknown",
            'area':     f"{full.get('living_area')} m²" if full.get('living_area') else "",
            'extra':    ' | '.join(extra_parts),
            'url':      url,
            'maps_url': maps_url,
        })
        print(f"[Pararius] New (matches): {full.get('title')} | EUR {full.get('price', '?')}")

    save_seen(seen, seen_file)
    return new_listings


def _build_pararius_rent_search_url(self, city, price_min=None, price_max=None,
                                    area_min=None, bedrooms=None, interior=None,
                                    sort=None, page=1):
    """Build rental search URL for pararius.nl."""
    parts = [f'https://www.pararius.nl/huurwoningen/{city}']
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
