import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

DATA_DIR = '/data'
LISTINGS_KOOP_FILE = os.path.join(DATA_DIR, 'listings_koop.json')
LISTINGS_HUUR_FILE = os.path.join(DATA_DIR, 'listings_huur.json')
REACTIONS_FILE     = os.path.join(DATA_DIR, 'reactions.json')

def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

@app.get('/api/listings/{category}')
def get_listings(category: str):
    if category == 'koop':
        listings = load_json(LISTINGS_KOOP_FILE, [])
    elif category == 'huur':
        listings = load_json(LISTINGS_HUUR_FILE, [])
    else:
        raise HTTPException(status_code=404, detail='Unknown category')

    reactions = load_json(REACTIONS_FILE, {})
    for l in listings:
        l['reaction'] = reactions.get(l['url'], None)
    return JSONResponse(listings)

@app.post('/api/react/{reaction}')
def set_reaction(reaction: str, body: dict):
    if reaction not in ('favourite', 'reject', 'clear'):
        raise HTTPException(status_code=400, detail='Invalid reaction')
    url = body.get('url')
    if not url:
        raise HTTPException(status_code=400, detail='Missing url')
    reactions = load_json(REACTIONS_FILE, {})
    if reaction == 'clear':
        reactions.pop(url, None)
    else:
        reactions[url] = reaction
    save_json(REACTIONS_FILE, reactions)
    return {'ok': True}

@app.get('/', response_class=HTMLResponse)
def index():
    here = os.path.dirname(os.path.abspath(__file__))
    return open(os.path.join(here, 'index.html'), encoding='utf-8').read()
