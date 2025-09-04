from typing import Iterable
from sqlalchemy import ScalarResult, select, TIMESTAMP, Integer, text
from sqlalchemy.sql.functions import now
from sqlalchemy.orm import joinedload, mapped_column
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.declarative import declared_attr, as_declarative


@as_declarative()
class Base:
    """Base class with common attributes."""

    # noinspection PyMethodParameters
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        unique=True,
        nullable=False,
        sort_order=-2
    )
    created_at = mapped_column(
        TIMESTAMP, default=now(), nullable=False, sort_order=-1
    )


class DbWrapper:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, instance: Base) -> None:
        return self.session.add(instance)

    async def delete(self, instance: Base) -> None:
        return await self.session.delete(instance)

    async def flush(self) -> None:
        return await self.session.flush()

    async def commit(self) -> None:
        return await self.session.commit()

    async def scalars(
        self,
        model: type[Base],
        *args,
        select_from: Iterable | None = None,
        join: Iterable | None = None,
        exists: bool = False,
        order_by: Iterable | None = None,
        limit: int | None = None,
        offset: int | None = None
    ) -> ScalarResult:
        stmt = select(model)
        if select_from:
            stmt = stmt.select_from(*select_from)
        if join:
            js: list = []
            for i in join:
                js.append(joinedload(i[0]))
                for j in i[1:]:
                    js[-1] = js[-1].joinedload(j)
            stmt = stmt.options(*js)
        if exists:
            stmt = stmt.exists()
        for arg in args:
            stmt = stmt.where(arg)
        if order_by:
            stmt = stmt.order_by(*order_by)
        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        return await self.session.scalars(stmt)
