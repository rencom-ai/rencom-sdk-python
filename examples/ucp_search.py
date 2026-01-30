"""UCP merchant and product search example.

This example demonstrates:
- Searching for UCP merchants
- Searching for products across merchants
- Using filters and pagination
"""

import asyncio
import os

from rencom import AsyncRencomClient


async def main():
    """Search UCP merchants and products."""
    api_key = os.getenv("RENCOM_API_KEY")
    if not api_key:
        print("Error: RENCOM_API_KEY environment variable not set")
        return

    async with AsyncRencomClient(api_key=api_key) as client:
        # Search for retail merchants with checkout capability
        print("Searching for retail merchants...")
        merchants = await client.ucp.merchants.search(
            capabilities=["dev.ucp.shopping.checkout"], industry="retail", limit=5
        )

        print(f"\nFound {merchants.total} merchants (showing {len(merchants.merchants)}):")
        for merchant in merchants.merchants:
            print(f"\n{merchant.name} ({merchant.domain})")
            print(f"  Industry: {merchant.industry}")
            print(f"  Region: {merchant.region}")
            print(f"  Capabilities: {', '.join(merchant.capabilities)}")

        # Search for products
        print("\n\nSearching for laptops under $1500...")
        products = await client.ucp.products.search(
            "laptop",
            price_max=150000,  # $1500 in cents
            category="electronics",
            condition="new",
            limit=10,
        )

        print(f"\nFound {products.total} products (showing {len(products.products)}):")
        for product in products.products:
            if product.price:
                price = product.price.amount / 100
                print(f"\n{product.title}")
                print(f"  Price: ${price:.2f}")
                print(f"  Merchant: {product.merchant_domain}")
                if product.brand:
                    print(f"  Brand: {product.brand}")


if __name__ == "__main__":
    asyncio.run(main())
