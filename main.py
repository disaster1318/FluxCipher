from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client
import os
from passlib.hash import bcrypt
import jwt
import time
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FluxCipher")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET", "secret")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class RegisterRequest(BaseModel):
    phone: str
    password: str
    email: str = None

@app.post("/api/register")
async def register(req: RegisterRequest):
    existing = supabase.table("users").select("*").eq("phone", req.phone).execute()
    if existing.data:
        raise HTTPException(400, "Номер уже занят")
    hashed = bcrypt.hash(req.password)
    result = supabase.table("users").insert({
        "phone": req.phone,
        "password_hash": hashed,
        "email": req.email,
        "username": f"user_{req.phone[-4:]}"
    }).execute()
    return {"status": "ok", "user_id": result.data[0]["id"]}

@app.get("/")
def root():
    return {"status": "FluxCipher running"}
