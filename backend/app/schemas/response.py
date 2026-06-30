"""Standard API response models."""

from __future__ import annotations

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ApiResponse(BaseModel, Generic[DataT]):
    success: bool = True
    data: Optional[DataT] = None
    message: Optional[str] = None


class ApiErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
