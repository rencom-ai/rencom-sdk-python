"""UCP merchant and product search example.

This example demonstrates:
- Searching for UCP merchants
- Searching for products across merchants
- Using filters and pagination
"""

import asyncio
import os

# TODO: Uncomment after implementation
# from rencom import AsyncRencomClient


async def main():
    """Search UCP merchants and products."""
    api_key = os.getenv("RENCOM_API_KEY")
    if not api_key:
        print("Error: RENCOM_API_KEY environment variable not set")
        return

    # TODO: Uncomment after implementation
    # async with AsyncRencomClient(api_key=api_key) as client:
    #     # Search for retail merchants with checkout capability
    #     print("Searching for retail merchants...")
    #     merchants = await client.ucp.merchants.search(
    #         capabilities=["dev.ucp.shopping.checkout"],
    #         industry="retail",
    #         limit=5
    #     )
    #
    #     print(f"\nFound {len(merchants.results)} merchants:")
    #     for merchant in merchants.results:
    #         print(f"\n{merchant.name} ({merchant.domain})")
    #         print(f"  Industry: {merchant.industry}")
    #         print(f"  Region: {merchant.region}")
    #         print(f"  Capabilities: {', '.join(merchant.capabilities)}")
    #
    #     # Search for products
    #     print("\n\nSearching for laptops under $1500...")
    #     products = await client.ucp.products.search(
    #         "laptop",
    #         price_max=150000,  # $1500 in cents
    #         category="electronics",
    #         condition="new",
    #         limit=10
    #     )
    #
    #     print(f"\nFound {len(products.results)} products:")
    #     for product in products.results:
    #         price = product.price_cents / 100
    #         print(f"\n{product.name}")
    #         print(f"  Price: ${price:.2f}")
    #         print(f"  Merchant: {product.merchant_domain}")
    #         print(f"  Brand: {product.brand}")

    print("TODO: Implement after client is ready")


if __name__ == "__main__":
    asyncio.run(main())
