"""Authentication flow example.

This example demonstrates:
- Magic link authentication
- JWT token management
- API key creation and management
- Usage statistics
"""

import asyncio

# TODO: Uncomment after implementation
# from rencom import AsyncRencomClient


async def magic_link_flow():
    """Demonstrate magic link authentication."""
    # TODO: Uncomment after implementation
    # # Step 1: Request magic link (no auth needed)
    # client = AsyncRencomClient()
    # await client.auth.request_magic_link("user@example.com")
    # print("Magic link sent! Check your email.")
    #
    # # Step 2: User clicks link, gets token
    # # In production, your frontend would capture this token from the URL
    # token = "token_from_magic_link_url"
    #
    # # Step 3: Verify token and get JWT
    # jwt = await client.auth.verify_magic_link(token)
    # print(f"Got JWT: {jwt[:20]}...")
    #
    # # Step 4: Use JWT for authenticated requests
    # authed_client = AsyncRencomClient(jwt_token=jwt)
    # user = await authed_client.auth.me()
    # print(f"Logged in as: {user.email}")

    print("TODO: Implement after client is ready")


async def api_key_management():
    """Demonstrate API key management."""
    # TODO: Uncomment after implementation
    # # Requires JWT token
    # jwt = "your_jwt_token"
    # client = AsyncRencomClient(jwt_token=jwt)
    #
    # # List existing API keys
    # keys = await client.auth.list_api_keys()
    # print(f"You have {len(keys)} API keys:")
    # for key in keys:
    #     print(f"  - {key.key_prefix}: {key.name}")
    #
    # # Create new API key
    # new_key = await client.auth.create_api_key("Production App")
    # print(f"\nNew API key created: {new_key.key}")
    # print("Save this key! It won't be shown again.")
    #
    # # Check usage stats
    # usage = await client.auth.usage()
    # print(f"\nUsage today: {usage.calls_today}/{usage.daily_limit}")
    # print(f"Rate limit: {usage.calls_last_minute}/{usage.minute_limit} per minute")
    #
    # # Revoke an API key
    # await client.auth.delete_api_key(new_key.key_prefix)
    # print(f"Revoked key: {new_key.key_prefix}")

    print("TODO: Implement after client is ready")


async def main():
    """Run authentication examples."""
    print("=== Magic Link Flow ===")
    await magic_link_flow()

    print("\n=== API Key Management ===")
    await api_key_management()


if __name__ == "__main__":
    asyncio.run(main())
