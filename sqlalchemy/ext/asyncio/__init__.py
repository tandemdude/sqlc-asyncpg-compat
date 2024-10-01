# Copyright (c) 2024-present tandemdude
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import annotations

__all__ = ["AsyncConnection"]

import typing as t

import typing_extensions as t_ex

if t.TYPE_CHECKING:
    from collections.abc import AsyncIterator

    import asyncpg
    from asyncpg import cursor as cursor_
    from asyncpg import transaction as transaction_

ConnectionT = t_ex.TypeVar(
    "ConnectionT",
    "asyncpg.Connection[asyncpg.Record]",
    "asyncpg.pool.PoolConnectionProxy[asyncpg.Record]",
    default="asyncpg.pool.PoolConnectionProxy[asyncpg.Record]",
)


class ResultProxy:
    __slots__ = ("_data",)

    def __init__(self, data: list[asyncpg.Record]) -> None:
        self._data = data

    def first(self) -> asyncpg.Record | None:
        return self._data[0] if self._data else None

    def all(self) -> tuple[asyncpg.Record, ...]:
        return tuple(self._data)


class StreamProxy:
    __slots__ = ("_conn", "_cursor", "_cursor_iter", "_transaction")

    def __init__(self, transaction: transaction_.Transaction, cursor: cursor_.CursorFactory[asyncpg.Record]) -> None:
        self._cursor = cursor
        self._cursor_iter: AsyncIterator[asyncpg.Record] = aiter(self._cursor)
        self._transaction = transaction

    def __aiter__(self) -> AsyncIterator[asyncpg.Record]:
        return self

    async def __anext__(self) -> asyncpg.Record:
        try:
            assert self._cursor_iter is not None
            return await anext(self._cursor_iter)
        except Exception as e:
            if isinstance(e, StopAsyncIteration):
                await self._transaction.commit()
            else:
                await self._transaction.rollback()
            raise e


class AsyncConnection(t.Generic[ConnectionT]):
    """
    Replacement for the sqlalchemy AsyncConnection class. You can pass this to the constructor
    of the generated sqlc AsyncQuerier class.

    Args:
        conn: The asyncpg connection that backs this AsyncConnection instance.
    """

    __slots__ = ("conn",)

    def __init__(self, conn: ConnectionT) -> None:
        self.conn: ConnectionT = conn

    @staticmethod
    def _convert_params(params: dict[str, t.Any]) -> tuple[t.Any, ...]:
        """
        Convert the param dictionary passed to the query methods by sqlc into a tuple that
        can be unpacked into the asynpg query method.

        Args:
            params: Parameter dictionary to convert

        Returns:
            The converted parameters
        """
        return tuple(p[1] for p in sorted(params.items(), key=lambda p: int(p[0][1:])))

    # METHODS USED BY SQLC ASYNC QUERIER

    async def stream(self, query: str, params: dict[str, t.Any] | None = None) -> AsyncIterator[t.Any]:
        param_tuple = self._convert_params(params or {})

        transaction = self.conn.transaction()
        await transaction.start()

        return StreamProxy(transaction, self.conn.cursor(query, *param_tuple))

    async def execute(self, query: str, params: dict[str, t.Any] | None = None) -> ResultProxy:
        param_tup = self._convert_params(params or {})
        return ResultProxy(await self.conn.fetch(query, *param_tup))
