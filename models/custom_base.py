from datetime import datetime
from typing import Optional



from sqlalchemy import func, TIMESTAMP, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


from core import setup

class CustomBase(setup.Base):
    __abstract__ = True

    
    id = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(), default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(), nullable=True)

    
    """Base class for all models.
    Includes common columns and methods for all models.
    
    """


    
    def soft_delete(self) -> None:
        """Mark a record as soft-deleted."""
        self.deleted_at = datetime.now()

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.deleted_at = None

    def hard_delete(self) -> None:
        """Permanently remove the record."""
        self.deleted_at = None

    def __repr__(self) -> str:
        """Generic repr for all inheriting models."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def __str__(self) -> str:
        """Generic string representation."""
        return f"{self.__class__.__name__}({self.id})"

    def __eq__(self, other) -> bool:
        """Check equality based on the id."""
        if isinstance(other, self.__class__):
            return self.id == other.id
        return False

    def __ne__(self, other) -> bool:
        """Check inequality."""
        return not self.__eq__(other)

    # Optional: Raise NotImplementedError for methods expected to be overridden
    def perform_custom_logic(self) -> None:
        """Placeholder for custom logic expected in child classes."""
        raise NotImplementedError("This method should be implemented by subclasses.")
