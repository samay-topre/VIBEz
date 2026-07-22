from fastapi import FastAPI, HTTPException
from supabase import create_client
from sentence_transformers import SentenceTransformer
import hashlib, re, resend, uvicorn, random
from fastapi.middleware.cors import CORSMiddleware

# --- CONFIG ---
URL = "REPLACE_WITH_SUPABASE_URL"
KEY = "REPLACE_WITH_SUPABASE_ANON_KEY"
resend.api_key = "re_YOUR_RESEND_KEY"
supabase = create_client(URL, KEY)

app = FastAPI(title="VIBE Master Backend")

# Enable connection from Mobile App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load AI Model (384 dimensions)
print("AI Model Loading...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("AI Ready!")

# 21 Master Categories
CATEGORIES = ["Dating", "Relationship", "Marriage", "Toxic/Red Flags", "Exes", "Corporate", "Boss", "Coworkers", "Finance", "Freelancers", "College", "Professors", "Health", "Fitness", "Landlords", "Roommates", "Cafes", "Hotels", "Society", "Shopping", "Others"]

# --- 1. SIGNUP LOGIC ---
@app.post("/signup")
async def signup(user_id_alias: str, email: str, age: int, password: str, device_id: str):
    # Rules: 18+, No letters in ID, Alpha-start Password
    if age < 18: raise HTTPException(400, "Must be 18+")
    if re.search('[a-zA-Z]', user_id_alias): raise HTTPException(400, "UserID: No letters allowed")
    if not re.match(r"^[a-zA-Z].{7,15}$", password): raise HTTPException(400, "Password: Start with Letter, 8-16 chars")
    
    # Device Hashing & Limit Check (Max 3)
    dev_hash = hashlib.sha256(device_id.encode()).hexdigest()
    check = supabase.table("app_users").select("id").eq("device_hash", dev_hash).execute()
    if len(check.data) >= 3: raise HTTPException(400, "Device limit (3) reached")

    try:
        data = {"user_id_alias": user_id_alias, "email": email, "age": age, "password": password, "device_hash": dev_hash}
        res = supabase.table("app_users").insert(data).execute()
        return {"status": "Success", "user_uuid": res.data[0]['id']}
    except:
        raise HTTPException(400, "This ID is already taken")

# --- 2. LOGIN LOGIC ---
@app.post("/login")
async def login(user_id_alias: str, password: str):
    res = supabase.table("app_users").select("id").eq("user_id_alias", user_id_alias).eq("password", password).execute()
    if not res.data:
        raise HTTPException(401, "Invalid UserID or Password")
    return {"status": "Login Successful", "user_uuid": res.data[0]['id']}

# --- 3. RECOVERY LOGIC (RESEND) ---
@app.post("/recover-id")
async def recover_id(email: str):
    res = supabase.table("app_users").select("user_id_alias").eq("email", email).execute()
    if res.data:
        ids = [r['user_id_alias'] for r in res.data]
        ids_string = ", ".join(ids)
        resend.Emails.send({
            "from": "VIBE <onboarding@resend.dev>",
            "to": email,
            "subject": "Your VIBE Identities",
            "html": f"The IDs linked to your email are: <strong>{ids_string}</strong>"
        })
    return {"status": "If email is registered, IDs have been sent."}

# --- 4. VOTING LOGIC ---
@app.post("/vote")
async def vote(review_id: int, vote_type: str):
    res = supabase.table("reviews").select("upvotes, downvotes").eq("id", review_id).execute()
    if not res.data: raise HTTPException(404, "Vibe not found")
    
    if vote_type == "up":
        new_val = res.data[0]['upvotes'] + 1
        supabase.table("reviews").update({"upvotes": new_val}).eq("id", review_id).execute()
    else:
        new_val = res.data[0]['downvotes'] + 1
        supabase.table("reviews").update({"downvotes": new_val}).eq("id", review_id).execute()
    return {"status": "Vote recorded"}

# --- 5. SEARCH LOGIC (AI BELTS) ---
@app.get("/search")
async def search(query: str, category: str):
    query_vec = model.encode(query).tolist()
    # Call the SQL function we created in Supabase
    res = supabase.rpc("match_reviews", {"query_embedding": query_vec, "match_count": 60, "search_category": category}).execute()
    
    belts = {"High": [], "Mid": [], "Low": []}
    for r in res.data:
        score = r['similarity']
        item = {"id": r['id'], "by": r['user_alias'], "text": r['content'], "up": r['upvotes'], "down": r['downvotes'], "match": f"{round(score)}%"}
        
        if score >= 70 and len(belts["High"]) < 15: belts["High"].append(item)
        elif 50 <= score < 70 and len(belts["Mid"]) < 15: belts["Mid"].append(item)
        elif 30 <= score < 50 and len(belts["Low"]) < 15: belts["Low"].append(item)
    return belts

# --- 6. VIBE STREAM (300 DUMMY VIBES) ---
@app.get("/vibe-stream")
async def get_stream():
    # Fetches all featured vibes, shuffles them, and returns top 300
    res = supabase.table("featured_vibes").select("content, category").execute()
    data = res.data
    random.shuffle(data) # Makes it feel "Live" every time
    return data[:300]

# --- 7. POSTING A VIBE ---
@app.post("/post_vibe")
async def post_vibe(user_uuid: str, category: str, text: str):
    if category not in CATEGORIES: raise HTTPException(400, "Invalid Category")
    vector = model.encode(text).tolist()
    data = {"author_id": user_uuid, "category": category, "content": text, "embedding": vector}
    supabase.table("reviews").insert(data).execute()
    return {"status": "Vibe shared successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)