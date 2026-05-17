"""Temporary test: start server, register user, print result."""
import os, sys, logging, threading, time
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")

# Force all logs to stdout so PowerShell captures them
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, force=True)
for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    logging.getLogger(name).handlers = []
    logging.getLogger(name).addHandler(logging.StreamHandler(sys.stdout))

import uvicorn, requests, traceback


def test():
    time.sleep(4)
    try:
        r = requests.post(
            "http://127.0.0.1:8001/api/v1/auth/register",
            json={"full_name": "Live Test", "email": "livetest99@example.com", "password": "TestPass123!"},
        )
        print(f"\n{'='*60}", flush=True)
        print(f"STATUS: {r.status_code}", flush=True)
        print(f"BODY:   {r.text}", flush=True)
        print(f"{'='*60}\n", flush=True)
    except Exception:
        traceback.print_exc()
    finally:
        os._exit(0)


from app.main import app as application
from fastapi import Request
from fastapi.responses import JSONResponse

@application.exception_handler(Exception)
async def catch_all(request: Request, exc: Exception):
    import traceback
    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
    print("\n!!! EXCEPTION !!!", flush=True)
    print("".join(tb), flush=True)
    return JSONResponse(status_code=500, content={"detail": str(exc)})

threading.Thread(target=test, daemon=True).start()
uvicorn.run(application, host="0.0.0.0", port=8001, reload=False, log_level="trace")

