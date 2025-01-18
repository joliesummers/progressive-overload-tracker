import asyncio
import pytest
from tests.test_integration import run_all_tests
from app.models.database import get_db

async def main():
    """Run all integration tests"""
    db = next(get_db())
    try:
        await run_all_tests(db)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
