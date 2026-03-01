from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.user import User
from models.contact import Contact
from database import get_db
from api.deps import get_current_active_user

import csv
import io

router = APIRouter()

# --- Schemas ---
class ContactCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    tags: Optional[str] = ""
    notes: Optional[str] = ""

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None

class ContactResponse(BaseModel):
    id: int
    name: Optional[str]
    phone: str
    email: Optional[str]
    tags: str
    notes: str
    source: str
    total_messages_sent: int

    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("/", response_model=List[ContactResponse])
async def list_contacts(
    tag: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List all contacts for the current business owner. Optionally filter by tag."""
    query = select(Contact).where(Contact.owner_id == current_user.id)
    if tag:
        query = query.where(Contact.tags.contains(tag))
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact_in: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Add a single contact to the business's list."""
    contact = Contact(
        owner_id=current_user.id,
        name=contact_in.name,
        phone=contact_in.phone,
        email=contact_in.email,
        tags=contact_in.tags or "",
        notes=contact_in.notes or "",
        source="manual"
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_in: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update a contact's details."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.owner_id == current_user.id)
    )
    contact = result.scalars().first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for field, value in contact_in.dict(exclude_unset=True).items():
        setattr(contact, field, value)
    
    await db.commit()
    await db.refresh(contact)
    return contact

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Delete a contact."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.owner_id == current_user.id)
    )
    contact = result.scalars().first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    await db.delete(contact)
    await db.commit()
    return {"status": "deleted"}

@router.post("/import-csv")
async def import_contacts_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Import contacts from a CSV file.
    CSV must have columns: name, phone (required), email (optional), tags (optional)
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    
    contents = await file.read()
    decoded = contents.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    imported_count = 0
    errors = []
    
    for i, row in enumerate(reader):
        phone = row.get('phone', '').strip()
        name = row.get('name', '').strip()
        
        if not phone:
            errors.append(f"Row {i+1}: Missing phone number")
            continue
            
        contact = Contact(
            owner_id=current_user.id,
            name=name,
            phone=phone,
            email=row.get('email', '').strip() or None,
            tags=row.get('tags', '').strip(),
            source="csv_import"
        )
        db.add(contact)
        imported_count += 1
    
    await db.commit()
    return {
        "status": "success",
        "imported": imported_count,
        "errors": errors
    }
