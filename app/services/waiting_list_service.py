from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from app.models.waiting_list import WaitingList
from app.schemas.waiting_list import WaitingListCreate
from app.deps import get_db


class WaitingListService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_waiting_list_entry(self, entry_id: int) -> WaitingList:
        entry = self.db.query(WaitingList).filter(WaitingList.id == entry_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Waiting list entry not found")
        return entry

    def get_waiting_list(self, reservation_id: int = None, skip: int = 0, limit: int = 100) -> List[WaitingList]:
        query = self.db.query(WaitingList)
        if reservation_id:
            query = query.filter(WaitingList.reservation_id == reservation_id)
        return query.offset(skip).limit(limit).all()

    def create_waiting_list_entry(self, entry: WaitingListCreate) -> WaitingList:
        db_entry = WaitingList(**entry.dict())
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        return db_entry

    def delete_waiting_list_entry(self, entry_id: int):
        db_entry = self.get_waiting_list_entry(entry_id)
        self.db.delete(db_entry)
        self.db.commit()
