import asyncio

async def mock_check():
    await asyncio.sleep(0.1)
    return "mock_result"

async def main():
    # Test how gather works
    coroutines = [mock_check(), mock_check()]
    
    try:
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        print("Results:", results)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())