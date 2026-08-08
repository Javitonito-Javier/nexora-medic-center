import argparse
import base64
import json
from datetime import UTC, datetime

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clinicapharma offline license tool.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("keygen", help="Generate an Ed25519 private/public key pair.")

    license_parser = subparsers.add_parser("license", help="Generate a signed license key.")
    license_parser.add_argument(
        "--private-key", required=True, help="Base64url private key from keygen."
    )
    license_parser.add_argument("--customer", required=True, help="Customer or business name.")
    license_parser.add_argument("--installation-id", required=True, help="Installation identifier.")
    license_parser.add_argument("--expires-at", required=True, help="Expiration date, YYYY-MM-DD.")
    license_parser.add_argument(
        "--modules", default="clinic,pharmacy", help="Comma-separated enabled modules."
    )
    license_parser.add_argument("--notes", default="", help="Private payment or contract note.")

    args = parser.parse_args()
    if args.command == "keygen":
        keygen()
    elif args.command == "license":
        generate_license(args)


def keygen() -> None:
    private_key = Ed25519PrivateKey.generate()
    private_bytes = private_key.private_bytes(
        encoding=Encoding.Raw,
        format=PrivateFormat.Raw,
        encryption_algorithm=NoEncryption(),
    )
    public_bytes = private_key.public_key().public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw,
    )
    print("PRIVATE_KEY=" + _b64encode(private_bytes))
    print("PUBLIC_KEY=" + _b64encode(public_bytes))


def generate_license(args) -> None:
    private_key = Ed25519PrivateKey.from_private_bytes(_b64decode(args.private_key))
    expires_at = datetime.fromisoformat(args.expires_at).replace(
        hour=23,
        minute=59,
        second=59,
        tzinfo=UTC,
    )
    payload = {
        "customer_name": args.customer,
        "installation_id": args.installation_id,
        "issued_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "expires_at": expires_at.isoformat(),
        "modules": [item.strip() for item in args.modules.split(",") if item.strip()],
        "notes": args.notes,
    }
    payload_json = json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    payload_part = _b64encode(payload_json.encode("utf-8"))
    signature = private_key.sign(payload_part.encode("ascii"))
    print(payload_part + "." + _b64encode(signature))


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


if __name__ == "__main__":
    main()
