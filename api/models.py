from pydantic import BaseModel, Field
from typing import Optional


class PocketClinicRequest(BaseModel):
    """Request model for PocketClinic API"""
    text_message: Optional[str] = Field(None, description="SMS text describing patient symptoms")
    phone_number: str = Field(..., description="Phone number to send referral (E.164 format)")
    # Note: Audio file will be handled via Form data, not in the JSON body


class PocketClinicResponse(BaseModel):
    """Response model for PocketClinic API"""
    status: str = Field(..., description="Status of the request (success or error)")
    message: str = Field(..., description="Result message or error details")
    details: Optional[dict] = Field(None, description="Additional details about the result")


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = Field("error", description="Error status")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
