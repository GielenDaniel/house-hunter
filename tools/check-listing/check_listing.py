import sys
from funda import Funda
from pypararius import Pararius

# ============================================================
#  SET YOUR IDs HERE
# ============================================================

FUNDA_IDS    = []   # global_id from funda logs
PARARIUS_IDS = []   # url from pararius logs,


# ============================================================

def check_funda(ids):
    if not ids:
        return
    print("\n" + "="*60)
    print("FUNDA")
    print("="*60)
    f = Funda()
    for listing_id in ids:
        print(f"\n── ID: {listing_id}")
        try:
            listing = f.get_listing(listing_id)
            print("  ALL FIELDS:")
            for key, value in listing.items():
                if key != 'characteristics':
                    print(f"    {key}: {str(value)[:200]}")
            print("  CHARACTERISTICS:")
            for key, value in (listing.get('characteristics') or {}).items():
                print(f"    {key}: {value}")
        except Exception as e:
            print(f"  Could not fetch: {e}")
 
def check_pararius(urls):
    if not urls:
        return
    print("\n" + "="*60)
    print("PARARIUS")
    print("="*60)
    p = Pararius()
    for url in urls:
        print(f"\n── {url}")
        try:
            listing = p.get_listing(url)
            print("  ALL FIELDS:")
            for key, value in listing.items():
                if key != 'characteristics':
                    print(f"    {key}: {str(value)[:200]}")
            print("  CHARACTERISTICS:")
            for key, value in (listing.get('characteristics') or {}).items():
                print(f"    {key}: {value}")
        except Exception as e:
            print(f"  Could not fetch: {e}")
 
if __name__ == '__main__':
    check_funda(FUNDA_IDS)
    check_pararius(PARARIUS_IDS)