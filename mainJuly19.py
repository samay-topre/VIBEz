from fastapi import FastAPI, HTTPException
from supabase import create_client
from sentence_transformers import SentenceTransformer
import hashlib
import re
import uvicorn

# --- STEP A: CONNECT TO DATABASE ---
# Use your specific credentials
URL = "https://efmqrzhbywxakkoxdfnc.supabase.co"
KEY = "sb_publishable_0oIVfsFlWknztr08KPYakA_kuleoMZa"
supabase = create_client(URL, KEY)

app = FastAPI(title="VIBE - Trust Engine")

# --- STEP B: LOAD AI MODEL ---
print("AI Model Loading... (This may take a minute on first run)")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("AI Ready!")

# --- STEP C: SIGNUP LOGIC ---
@app.post("/signup")
async def signup(user_id_alias: str, password: str, device_id: str):
    # Rule 1: UserID - NO Letters. ONLY Digits and Special Symbols.
    if re.search('[a-zA-Z]', user_id_alias):
        raise HTTPException(status_code=400, detail="UserID can ONLY contain digits and special symbols (No letters allowed).")
    
    # Rule 2: Password - Length 8-16, starts with Alphabet.
    if not re.match(r"^[a-zA-Z].{7,15}$", password):
        raise HTTPException(status_code=400, detail="Password must be 8-16 characters long and start with a letter.")

    # Device Hashing for Anonymity
    dev_hash = hashlib.sha256(device_id.encode()).hexdigest()
    
    try:
        data = {
            "user_id_alias": user_id_alias, 
            "password": password, 
            "device_hash": dev_hash
        }
        # Insert into Supabase
        supabase.table("app_users").insert(data).execute()
        return {"status": "Success", "message": "Account created successfully!"}
    except Exception as e:
        # This will now show the actual error (like RLS or duplicates) instead of a generic message
        error_msg = str(e)
        if "duplicate key" in error_msg:
            raise HTTPException(status_code=400, detail="This UserID or Device is already registered.")
        else:
            raise HTTPException(status_code=400, detail=f"Database Error: {error_msg}")

# --- STEP D: LOGIN LOGIC ---
@app.post("/login")
async def login(user_id_alias: str, password: str):
    res = supabase.table("app_users").select("*").eq("user_id_alias", user_id_alias).eq("password", password).execute()
    if not res.data:
        raise HTTPException(status_code=401, detail="Invalid UserID or Password.")
    
    # Return the internal UUID for posting reviews
    return {"status": "Login Successful", "user_uuid": res.data[0]['id']}

# --- STEP E: VOTING LOGIC ---
@app.post("/vote")
async def vote(review_id: int, vote_type: str):
    """ vote_type should be 'up' or 'down' """
    res = supabase.table("reviews").select("upvotes, downvotes").eq("id", review_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Review not found.")
    
    if vote_type == "up":
        new_count = res.data[0]['upvotes'] + 1
        supabase.table("reviews").update({"upvotes": new_count}).eq("id", review_id).execute()
    elif vote_type == "down":
        new_count = res.data[0]['downvotes'] + 1
        supabase.table("reviews").update({"downvotes": new_count}).eq("id", review_id).execute()
    else:
        raise HTTPException(status_code=400, detail="Use 'up' or 'down' for vote_type.")
        
    return {"status": "Vote recorded."}

# --- STEP F: POSTING REVIEWS ---
@app.post("/post_review")
async def post_review(user_uuid: str, review_text: str):
    # Convert text to Vector
    vector = model.encode(review_text).tolist()
    
    data = {
        "author_id": user_uuid, 
        "content": review_text, 
        "embedding": vector
    }
    
    try:
        supabase.table("reviews").insert(data).execute()
        return {"status": "Success", "message": "Review posted anonymously."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- STEP G: SEARCH LOGIC (AI MATCHING) ---
@app.get("/search")
async def search(query: str):
    # Convert search query to vector
    query_vec = model.encode(query).tolist()
    
    # RPC call to Supabase search function
    res = supabase.rpc("match_reviews", {'query_embedding': query_vec, 'match_count': 50}).execute()
    
    # Categorize and limit to top 15 per category
    output = {
        "Most Matching (80%+)": [], 
        "Partial Match (50-79%)": [], 
        "Others": []
    }
    
    for r in res.data:
        score = r['similarity']
        item = {
            "id": r['id'], 
            "by": r['user_alias'], 
            "text": r['content'], 
            "match_score": f"{round(score, 1)}%",
            "votes": {"upvotes": r['upvotes'], "downvotes": r['downvotes']}
        }
        
        if score >= 80 and len(output["Most Matching (80%+)"]) < 15:
            output["Most Matching (80%+)"].append(item)
        elif 50 <= score < 80 and len(output["Partial Match (50-79%)"]) < 15:
            output["Partial Match (50-79%)"].append(item)
        elif score < 50 and len(output["Others"]) < 15:
            output["Others"].append(item)
            
    return output

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)