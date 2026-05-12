import uvicorn

from mcp_server.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run("mcp_server.app:app", host=settings.host, port=settings.port, reload=False)


if __name__ == "__main__":
    main()
