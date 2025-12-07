from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app import crud, schemas

router = APIRouter()

@router.post("/", response_model=dict)
def create_assessment(a: schemas.AssessmentCreate, db: Session = Depends(get_db)):
    ass = crud.create_assessment(db, a)
    return {"id": ass.id}

@router.post("/choice", response_model=dict)
def add_choice(c: schemas.ChoiceCreate, db: Session = Depends(get_db)):
    ch = crud.add_choice(db, c)
    return {"id": ch.id}

@router.post("/submit", response_model=dict)
def submit_answer(user_id: int, assessment_id: int, choice_id: int, db: Session = Depends(get_db)):
    sa = crud.record_student_answer(db, user_id, assessment_id, choice_id)
    return {"id": sa.id}
