from funda import Funda
from utils import LOCATION, PRICE_MIN, PRICE_MAX, AREA_MIN, NEIGHBOURHOODS, REQUIRE_BALCONY_OR_ROOF_TERRACE, NOT_FIRST_FLOOR, SINGLE_STORY, load_seen, save_seen, build_maps_url

# ============================================================
#  SETTINGS
# ============================================================

OBJECT_TYPE  = ['apartment']
MIN_BEDROOMS = 2
MIN_ROOMS    = 3
REQUIRE_LIFT = True

# ============================================================
#  SCRIPT
# ============================================================

def matches_filters(r, full_listing=None):
    if NEIGHBOURHOODS:
        neighbourhood = r.get('neighbourhood', '').lower()
        if not any(n in neighbourhood for n in NEIGHBOURHOODS):
            return False, f"neighbourhood '{neighbourhood}' not in list"

    bedrooms = r.get('bedrooms') or 0
    rooms    = r.get('rooms') or 0
    if MIN_BEDROOMS is not None or MIN_ROOMS is not None:
        meets_bedrooms = MIN_BEDROOMS is not None and bedrooms >= MIN_BEDROOMS
        meets_rooms    = MIN_ROOMS is not None and rooms >= MIN_ROOMS
        if not (meets_bedrooms or meets_rooms):
            return False, f"bedrooms ({bedrooms}) and rooms ({rooms}) too few"

    if full_listing is not None:
        chars            = full_listing.get('characteristics') or {}
        voorzieningen    = chars.get('Voorzieningen', '')
        gelegen_op       = chars.get('Gelegen op', '')
        aantal_woonlagen = chars.get('Aantal woonlagen', '')
        balkon_char      = chars.get('Balkon/dakterras', '')

        if REQUIRE_BALCONY_OR_ROOF_TERRACE:
            has_balcony      = full_listing.get('has_balcony') or full_listing.get('has_roof_terrace')
            has_balcony_char = 'balkon' in balkon_char.lower() or 'dakterras' in balkon_char.lower()
            if not (has_balcony or has_balcony_char):
                return False, "no balcony or roof terrace"

        if NOT_FIRST_FLOOR and gelegen_op and 'begane grond' in gelegen_op.lower():
            return False, f"ground floor (Gelegen op: {gelegen_op})"

        if SINGLE_STORY and aantal_woonlagen and '1 woonlaag' not in aantal_woonlagen.lower():
            return False, f"not single storey (Aantal woonlagen: {aantal_woonlagen})"

    return True, "matches filters"

def get_new_listings(offering_type='buy'):
    seen_file = f'/data/seen_funda_{offering_type}.json'
    seen = load_seen(seen_file)
    f    = Funda()

    try:
        results = f.search_listing(
            location      = LOCATION,
            offering_type = offering_type,
            price_min     = PRICE_MIN,
            price_max     = PRICE_MAX,
            area_min      = AREA_MIN,
            object_type   = OBJECT_TYPE,
            sort          = 'newest',
        )
    except Exception as e:
        print(f"[Funda] Search failed: {e}")
        return []

    print(f"[Funda] Found {len(results)} results from search")

    new_listings = []
    for r in results:
        listing_id = str(r.get('tiny_id') or r.get('global_id'))
        if not listing_id or listing_id in seen:
            continue
        seen.add(listing_id)

        matches, reason = matches_filters(r)
        if not matches:
            print(f"[Funda] Skipped ({reason}): {r['title']}")
            continue

        full = None
        if REQUIRE_LIFT or NOT_FIRST_FLOOR or SINGLE_STORY or REQUIRE_BALCONY_OR_ROOF_TERRACE:
            try:
                full = f.get_listing(listing_id)
            except Exception as e:
                print(f"[Funda] Could not fetch full listing for {r['title']}: {e}")

        passed, reason = matches_filters(r, full_listing=full)
        if not passed:
            print(f"[Funda] Skipped ({reason}): {r['title']}")
            continue

        chars            = (full.get('characteristics') or {}) if full else {}
        voorzieningen    = chars.get('Voorzieningen', '')
        gelegen_op       = chars.get('Gelegen op', '')
        aantal_woonlagen = chars.get('Aantal woonlagen', '')
        balkon_char      = chars.get('Balkon/dakterras', '')

        warnings = []
        if REQUIRE_LIFT and voorzieningen and 'lift' not in voorzieningen.lower():
            warnings.append("⚠️ Mogelijk geen lift")
        if NOT_FIRST_FLOOR and not gelegen_op:
            warnings.append("⚠️ verdieping onbekend")
        if NOT_FIRST_FLOOR and gelegen_op and '1e woonlaag' in gelegen_op.lower():
            warnings.append("⚠️ Eerste verdieping (geen begane grond)")
        if SINGLE_STORY and not aantal_woonlagen:
            warnings.append("⚠️ woonlagen onbekend")

        maps_url = build_maps_url(
            lat   = r.get('latitude'),
            lng   = r.get('longitude'),
            title = r.get('title', ''),
            city  = r.get('city', ''),
        ) or r.get('google_maps_url', '')

        extra_parts = []
        if balkon_char:
            extra_parts.append(balkon_char)
        if gelegen_op:
            extra_parts.append(f"Verdieping: {gelegen_op}")
        if aantal_woonlagen:
            extra_parts.append(aantal_woonlagen)
        extra_parts.extend(warnings)

        new_listings.append({
            'source':   'Funda',
            'title':    r.get('title', ''),
            'price':    f"EUR {r['price']:,}" if r.get('price') else "price unknown",
            'area':     f"{r.get('living_area')} m²" if r.get('living_area') else "",
            'extra':    ' | '.join(extra_parts),
            'url':      'https://www.funda.nl' + r.get('detail_url', ''),
            'maps_url': maps_url,
        })
        print(f"[Funda] New (matches): {r['title']} | EUR {r.get('price', '?')}")

    save_seen(seen, seen_file)
    return new_listings