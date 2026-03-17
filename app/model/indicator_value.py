from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class IndicatorValue(Base):
    __tablename__ = "indicator_values"
    __table_args__ = (
        UniqueConstraint(
            "indicator_id", "region_id", "year", "period", name="uq_indicator_region_year"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    indicator_id: Mapped[int] = mapped_column(
        ForeignKey("indicators.id"), nullable=False
    )
    region_id: Mapped[int] = mapped_column(
        ForeignKey("regions.id"), nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[float] = mapped_column(Numeric(18,4), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    period: Mapped[str] = mapped_column(String(20), nullable=False, default="year")
