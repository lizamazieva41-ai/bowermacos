"""
Main entry point for the Bower Antidetect Browser application.
Supports multiple modes: API only, GUI only, or both.
"""

import os
import sys
import argparse
import threading
import time
import uvicorn
from typing import Optional


def run_api_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    ssl_cert: Optional[str] = None,
    ssl_key: Optional[str] = None,
):
    """Run the FastAPI server."""
    kwargs = {
        "host": host,
        "port": port,
        "reload": reload,
    }

    if ssl_cert and ssl_key:
        kwargs["ssl_certfile"] = ssl_cert
        kwargs["ssl_keyfile"] = ssl_key

    print(f"[API] Starting server on {host}:{port}")
    uvicorn.run("src.api.routes:app", **kwargs)


def run_gui():
    """Run the DearPyGui application."""
    print("[GUI] Starting GUI application...")
    from src.gui.main import main as gui_main

    try:
        gui_main()
    except KeyboardInterrupt:
        print("[GUI] Shutting down GUI...")


def run_both(host: str = "0.0.0.0", port: int = 8000):
    """Run both API server and GUI simultaneously."""
    api_thread = threading.Thread(
        target=run_api_server,
        kwargs={
            "host": host,
            "port": port,
            "reload": False,
        },
        daemon=True,
    )
    api_thread.start()

    print(f"[BOTH] API server started on {host}:{port}")
    print("[BOTH] Starting GUI (ensure API is running)...")
    time.sleep(2)

    run_gui()


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Bower Antidetect Browser - Main Entry Point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run API server only (default)
  python main.py --mode=api         # Run API server only
  python main.py --mode=gui        # Run GUI only
  python main.py --mode=both       # Run both API and GUI
  python main.py --mode=both --port=9000  # Custom port
  python main.py --host=127.0.0.1 --port=9000  # Custom host/port
        """
    )

    parser.add_argument(
        "--mode",
        choices=["api", "gui", "both"],
        default="api",
        help="Application mode: api (FastAPI only), gui (DearPyGui only), or both (default: api)"
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the API server (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the API server (default: 8000)"
    )

    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload for API server"
    )

    args = parser.parse_args()

    ssl_cert = os.environ.get("SSL_CERT", "")
    ssl_key = os.environ.get("SSL_KEY", "")

    if args.mode == "api":
        print("[API] Starting API server only...")
        run_api_server(
            host=args.host,
            port=args.port,
            reload=not args.no_reload,
            ssl_cert=ssl_cert,
            ssl_key=ssl_key,
        )

    elif args.mode == "gui":
        print("[GUI] Starting GUI only...")
        print("[GUI] Note: GUI requires API server to be running")
        run_gui()

    elif args.mode == "both":
        print("[BOTH] Starting API server and GUI...")
        run_both(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
