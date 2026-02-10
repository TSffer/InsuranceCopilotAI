
import sys
import asyncio
if __name__ == "__main__":
    if sys.platform == "win32":
        # Fix for Psycopg ProactorEventLoop issue on Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    import uvicorn
    
    async def main():
        config = uvicorn.Config("main:app", host="127.0.0.1", port=8000, reload=False)
        server = uvicorn.Server(config)
        await server.serve()

    # Run the application using asyncio.run which respects the set policy
    asyncio.run(main())
