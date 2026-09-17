"""
Authentication router for CarbonLoop.
"""

from fastapi import APIRouter, HTTPException, Depends, status
import uuid
from app.database import get_db_connection
from app.models import UserRegister, UserLogin, TokenResponse
from app.security import hash_password, verify_password, create_access_token, get_current_user_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
def register_user(req: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check email
    cursor.execute("SELECT id FROM users WHERE email = ?", (req.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    org_id = f"org-{uuid.uuid4().hex[:8]}"
    user_id = f"user-{uuid.uuid4().hex[:8]}"

    # Organization
    cursor.execute("""
    INSERT INTO organizations (id, name, industry, country, state, employee_count, facility_sqft, baseline_year, is_synthetic)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        org_id,
        req.organization_name,
        "Individual / Consumer" if req.is_individual else "Commercial Enterprise",
        "India",
        "Maharashtra",
        1 if req.is_individual else 10,
        500.0 if req.is_individual else 5000.0,
        2024,
        0
    ))

    # User
    cursor.execute("""
    INSERT INTO users (id, email, hashed_password, full_name, role, org_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        req.email,
        hash_password(req.password),
        req.full_name,
        "admin",
        org_id
    ))

    conn.commit()
    conn.close()

    token = create_access_token({
        "sub": user_id,
        "email": req.email,
        "org_id": org_id,
        "role": "admin"
    })

    return TokenResponse(
        access_token=token,
        user_id=user_id,
        email=req.email,
        full_name=req.full_name,
        org_id=org_id,
        org_name=req.organization_name,
        is_synthetic=False
    )

@router.post("/login", response_model=TokenResponse)
def login_user(req: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT u.id, u.email, u.hashed_password, u.full_name, u.role, u.org_id, o.name as org_name, o.is_synthetic
    FROM users u
    JOIN organizations o ON u.org_id = o.id
    WHERE u.email = ?
    """, (req.email,))
    user = cursor.fetchone()
    conn.close()

    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token({
        "sub": user["id"],
        "email": user["email"],
        "org_id": user["org_id"],
        "role": user["role"]
    })

    return TokenResponse(
        access_token=token,
        user_id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        org_id=user["org_id"],
        org_name=user["org_name"],
        is_synthetic=bool(user["is_synthetic"])
    )

@router.get("/me")
def get_current_user_profile(token_data: dict = Depends(get_current_user_token)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT u.id, u.email, u.full_name, u.role, u.org_id, o.name as org_name, o.employee_count, o.facility_sqft, o.is_synthetic
    FROM users u
    JOIN organizations o ON u.org_id = o.id
    WHERE u.id = ?
    """, (token_data["sub"],))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return dict(row)
