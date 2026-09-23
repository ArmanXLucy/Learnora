"""Firebase Admin SDK helpers for Learnora server-side token verification.

The import is intentionally lazy so the rest of the Learnora app can still
start and show a useful configuration error until firebase-admin is installed.
"""
import json
import os


def verify_id_token(id_token):
    try:
        import firebase_admin
        from firebase_admin import auth, credentials
    except ImportError as exc:
        raise RuntimeError("firebase-admin is not installed. Run: pip install -r requirements.txt") from exc

    if not firebase_admin._apps:
        service_account_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH", "")
        service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "")

        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
        elif service_account_json:
            cred = credentials.Certificate(json.loads(service_account_json))
        else:
            raise RuntimeError(
                "Firebase Admin is not configured. Set FIREBASE_SERVICE_ACCOUNT_PATH "
                "or FIREBASE_SERVICE_ACCOUNT_JSON in .env."
            )
        firebase_admin.initialize_app(cred)

    return auth.verify_id_token(id_token)
