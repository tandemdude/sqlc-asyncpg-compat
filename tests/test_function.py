import os
from importlib import resources

import asyncpg
import pytest
import sql
from sql import queries

from sqlalchemy.ext.asyncio import AsyncConnection


@pytest.mark.asyncio
async def test_basic_functionality() -> None:
    pool = await asyncpg.create_pool(
        os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    )
    assert pool is not None
    try:
        async with pool.acquire() as conn:
            schema = resources.read_text(sql, "schema.sql")
            await conn.execute(schema)
            await conn.execute("DELETE FROM sqlc_test;")

            q = queries.AsyncQuerier(AsyncConnection(conn))

            await q.insert_one(name="foo", description="bar")
            await q.insert_one(name="baz", description="bork")
            await q.insert_one(name="qux", description=None)

            existing_row = await q.select_one(name="foo")
            assert existing_row is not None
            assert existing_row.name == "foo"
            assert existing_row.description == "bar"

            non_existing_row = await q.select_one(name="alskdja")
            assert non_existing_row is None

            rows = [r async for r in q.select_many()]
            assert len(rows) == 3

            assert rows[0].name == "foo"
            assert rows[0].description == "bar"

            assert rows[1].name == "baz"
            assert rows[1].description == "bork"

            assert rows[2].name == "qux"
            assert rows[2].description is None
    finally:
        await pool.close()
