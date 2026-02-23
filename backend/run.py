import sys
import asyncio
import os

if __name__ == "__main__":
    # El workaround de Windows solo es necesario en local (win32)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    import uvicorn
    
    async def main():
        # En contenedores (Azure), el host DEBE ser 0.0.0.0
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        
        config = uvicorn.Config(
            "main:app", 
            host=host, 
            port=port, 
            reload=False,
            proxy_headers=True,
            forwarded_allow_ips="*"
        )
        server = uvicorn.Server(config)
        await server.serve()

    asyncio.run(main())
