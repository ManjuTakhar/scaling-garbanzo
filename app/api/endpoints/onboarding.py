from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.crud import onboarding as crud_onboarding
from app.crud import user as user_crud
from app.schemas.onboarding import OnboardingRequest, OnboardingResponse
from typing import List

router = APIRouter()

@router.post("/onboarding", response_model=OnboardingResponse)
def create_onboarding(
    onboarding_data: OnboardingRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Complete the onboarding process in one API call."""
    try:
        user = user_crud.get_user_by_email(db, current_user["email"])
        if not user:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        return crud_onboarding.process_onboarding(db, user.user_id, onboarding_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


