import uvicorn

from mock_backend.config import get_backend_settings


def main() -> None:
    settings = get_backend_settings()
    uvicorn.run("mock_backend.app:app", host=settings.host, port=settings.port, reload=False)


if __name__ == "__main__":
    main()
