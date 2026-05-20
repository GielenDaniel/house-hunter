from funda import Funda
from pypararius import Pararius
import time

OFFERING_TYPE = 'rent'       # 'rent' or 'buy'
LOCATION  = 'amsterdam'      # location for search (e.g. 'amsterdam', 'rotterdam', 'utrecht')
PRICE_MIN = None             # min price for search (e.g. 500 for rent, 100000 for buy)
PRICE_MAX = 1000             # max price for search (e.g. 1000 for rent, 500000 for buy)
LIMIT     = 10               # number of listings to check (from search results)

def check_funda():
    print("\n" + "="*60)
    print("FUNDA CHARACTERISTICS")
    print("="*60)
    f = Funda()
    results = []
    try:
        results = f.search_listing(
            location      = LOCATION,
            offering_type = OFFERING_TYPE,
            price_max     = PRICE_MAX,
            sort          = 'newest',
        )
    except Exception as e:
        print(f"Search failed: {e}")
        return

    for r in results[:LIMIT]:
        listing_id = str(r.get('global_id', ''))
        print(f"\n── {r.get('title')} (id: {listing_id})")
        try:
            listing = f.get_listing(listing_id)
            chars = listing.get('characteristics') or {}
            if chars:
                for key, value in chars.items():
                    print(f"  {key}: {value}")
            else:
                print("  (no characteristics)")
        except Exception as e:
            print(f"  Could not fetch: {e}")
        time.sleep(0.5)

def check_pararius():
    print("\n" + "="*60)
    print("PARARIUS CHARACTERISTICS")
    print("="*60)
    p = Pararius()
    results = []
    try:
        results = p.search_listing(
            location  = LOCATION,
            price_max = PRICE_MAX,
            sort      = 'newest',
        )
    except Exception as e:
        print(f"Search failed: {e}")
        return

    for r in results[:LIMIT]:
        url = r.get('url', '')
        print(f"\n── {r.get('title')} ({url})")
        try:
            listing = p.get_listing(url)
            chars = listing.get('characteristics') or {}
            if chars:
                for key, value in chars.items():
                    print(f"  {key}: {value}")
            else:
                print("  (no characteristics)")
        except Exception as e:
            print(f"  Could not fetch: {e}")
        time.sleep(0.5)

if __name__ == '__main__':
    check_funda()
    check_pararius()
