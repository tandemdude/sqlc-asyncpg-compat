> [!CAUTION]
> This library is now archived and will not be receiving any updates. You should use the [better sqlc python plugin](https://github.com/rayakame/sqlc-gen-better-python) instead.

# sqlc-asyncpg-compat

Compatibility layer for sqlc generated python code, to allow database interactions to be done using
asyncpg directly, without having to deal with sqlalchemy asyncio and greenlet.

> [!NOTE]
> This library **is not** intended to be used standalone and is only designed to work directly with sqlc
> generated code and queries. Any other usage will not receive support.

## Usage

Ensure that sqlalchemy **is not** installed before installing this library. This installs into the same
namespace as sqlalchemy so that the sqlc generated imports continue to work.

```
pip install git+https://github.com/tandemdude/sqlc-asyncpg-compat
```

Once installed, you can pass an `AsyncConnection` provided by this library in place of the sqlalchemy one
when instantiating the generated `AsyncQuerier` class. A full example application is provided in the `example/`
directory.

## Minimal Example

Assuming that the generated files are in the `sql` package.

```python
import asyncio

import asyncpg
from sqlalchemy.ext.asyncio import AsyncConnection

from sql import queries

async def main():
    pool = await asyncpg.create_pool(...)
    async with pool.acquire() as conn:
        querier = queries.AsyncQuerier(AsyncConnection(conn))
        # perform queries
        ...


if __name__ == "__main__":
    asyncio.run(main())
```

## Links

- **License:** [MIT](https://choosealicense.com/licenses/mit/)
- **Repository:** [GitHub](https://github.com/tandemdude/sqlc-asyncpg-compat)
