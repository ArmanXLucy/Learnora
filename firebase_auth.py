"""Firebase Admin SDK helpers for Learnora server-side token verification."""

import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def verify_id_token(id_token):
    """Verify a Firebase ID token and return the decoded claims."""
    if not id_token:
        raise ValueError("Firebase ID token is missing.")

    try:
        import firebase_admin
        from firebase_admin import auth, credentials
    except ImportError as exc:
        raise RuntimeError(
            "firebase-admin is not installed. Run: pip install -r requirements.txt"
        ) from exc

    if not firebase_admin._apps:
        service_account_path = os.environ.get(
            "FIREBASE_SERVICE_ACCOUNT_PATH",
            "serviceAccountKey.json",
        ).strip()
        service_account_json = os.environ.get(
            "FIREBASE_SERVICE_ACCOUNT_JSON",
            "",
        ).strip()

        if service_account_path and not os.path.isabs(service_account_path):
            service_account_path = os.path.join(BASE_DIR, service_account_path)

        if service_account_path and os.path.isfile(service_account_path):
            print(
                "[Firebase] Loading service account:",
                os.path.abspath(service_account_path),
            )
            cred = credentials.Certificate(service_account_path)
        elif service_account_json:
            try:
                service_info = json.loads(service_account_json)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    "FIREBASE_SERVICE_ACCOUNT_JSON contains invalid JSON."
                ) from exc

            private_key = service_info.get("private_key")
            if isinstance(private_key, str):
                service_info["private_key"] = private_key.replace("\\n", "\n")

            print("[Firebase] Loading service account from FIREBASE_SERVICE_ACCOUNT_JSON")
            cred = credentials.Certificate(service_info)
        else:
            raise RuntimeError(
                "Firebase Admin is not configured. Set FIREBASE_SERVICE_ACCOUNT_PATH "
                "or FIREBASE_SERVICE_ACCOUNT_JSON in .env."
            )

        firebase_admin.initialize_app(cred)
        print("[Firebase] Firebase Admin initialized successfully.")

    try:
        decoded = auth.verify_id_token(
            id_token,
            clock_skew_seconds=10,
        )

        print(
            "[Firebase] Token verified successfully:",
            decoded.get("uid"),
            decoded.get("email"),
        )

        return decoded
    except Exception as exc:
        print("[Firebase] TOKEN VERIFICATION FAILED:")
        print(type(exc).__name__, str(exc))
        raise
