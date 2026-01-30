"""Basic x402 resource search example.

This example demonstrates:
- Initializing the client with API key
- Searching for x402 resources
- Iterating through results
"""

import asyncio
import os

# TODO: Uncomment after implementation
# from rencom import AsyncRencomClient


async def main():
    """Search for x402 resources."""
    # Get API key from environment
    api_key = os.getenv("RENCOM_API_KEY")
    if not api_key:
        print("Error: RENCOM_API_KEY environment variable not set")
        print("Get your API key from https://api.rencom.ai")
        return

    # TODO: Uncomment after implementation
    # async with AsyncRencomClient(api_key=api_key) as client:
    #     # Search for weather APIs
    #     print("Searching for weather APIs...")
    #     results = await client.x402.search("weather api", limit=5)
    #
    #     print(f"\nFound {len(results.results)} results:")
    #     for result in results.results:
    #         print(f"\n{result.resource}")
    #         print(f"  Description: {result.description}")
    #         print(f"  Max price: {result.max_amount_required} micro-units")
    #         print(f"  Network: {result.network}")
    #         print(f"  Score: {result.final_score:.2f}")

    print("TODO: Implement after client is ready")


if __name__ == "__main__":
    asyncio.run(main())
