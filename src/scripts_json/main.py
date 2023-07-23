import asyncio
import logging
from script import start_run


async def main():
    # Start the background task directly here
    await start_run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
