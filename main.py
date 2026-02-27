"""
Main entry point for the application.
"""
import os
import uvicorn

if __name__ == "__main__":
    ssl_cert = os.environ.get("SSL_CERT", "")
    ssl_key = os.environ.get("SSL_KEY", "")
    
    kwargs = {
        "host": "0.0.0.0",
        "port": int(os.environ.get("PORT", "8000")),
        "reload": True,
    }
    
    if ssl_cert and ssl_key:
        kwargs["ssl_certfile"] = ssl_cert
        kwargs["ssl_keyfile"] = ssl_key
    
    uvicorn.run("src.api.routes:app", **kwargs)
