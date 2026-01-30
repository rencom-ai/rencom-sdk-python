"""Pagination example.

This example demonstrates:
- Manual pagination with offset
- Auto-pagination with search_iter
- Handling large result sets
"""

import asyncio
import os

# TODO: Uncomment after implementation
# from rencom import AsyncRencomClient


async def manual_pagination():
    """Demonstrate manual pagination with offset."""
    api_key = os.getenv("RENCOM_API_KEY")
    if not api_key:
        return

    # TODO: Uncomment after implementation
    # async with AsyncRencomClient(api_key=api_key) as client:
    #     page_size = 5
    #     offset = 0
    #     page_num = 1
    #
    #     while True:
    #         print(f"\n=== Page {page_num} ===")
    #         results = await client.x402.search(
    #             "api",
    #             limit=page_size,
    #             offset=offset
    #         )
    #
    #         for result in results.results:
    #             print(f"  - {result.resource}")
    #
    #         if not results.has_more:
    #             print("\nNo more results")
    #             break
    #
    #         offset += page_size
    #         page_num += 1

    print("TODO: Implement after client is ready")


async def auto_pagination():
    """Demonstrate auto-pagination with search_iter."""
    api_key = os.getenv("RENCOM_API_KEY")
    if not api_key:
        return

    # TODO: Uncomment after implementation
    # async with AsyncRencomClient(api_key=api_key) as client:
    #     print("=== Auto-pagination ===")
    #     count = 0
    #
    #     async for result in client.x402.search_iter("api", limit=5):
    #         count += 1
    #         print(f"{count}. {result.resource}")
    #
    #         # Can stop early if needed
    #         if count >= 20:
    #             print("\nStopping after 20 results")
    #             break

    print("TODO: Implement after client is ready")


async def main():
    """Run pagination examples."""
    print("=== Manual Pagination ===")
    await manual_pagination()

    print("\n\n=== Auto-Pagination ===")
    await auto_pagination()


if __name__ == "__main__":
    asyncio.run(main())
