"""Windows Hello lewat API resmi Windows: UserConsentVerifier (WinRT).

Membutuhkan: Windows 10/11 dengan Windows Hello aktif (minimal PIN) dan paket winrt-*.
"""
import asyncio
from core import config


class HelloError(Exception):
    pass


async def _verify_async(message: str):
    from winrt.windows.security.credentials.ui import (
        UserConsentVerifier, UserConsentVerifierAvailability, UserConsentVerificationResult)
    availability = await UserConsentVerifier.check_availability_async()
    if availability != UserConsentVerifierAvailability.AVAILABLE:
        raise HelloError("Windows Hello belum aktif. Aktifkan di Settings > Accounts > Sign-in options.")
    result = await UserConsentVerifier.request_verification_async(message)
    if result != UserConsentVerificationResult.VERIFIED:
        raise HelloError("Verifikasi Windows Hello gagal atau dibatalkan.")


def verify(message: str = "SecureVault: verifikasi identitas Anda") -> bool:
    """Blocking. Panggil dari thread terpisah agar GUI tidak membeku."""
    if config.DEV_SKIP_HELLO:
        return True                      # HANYA mode pengembangan
    if not config.IS_WINDOWS:
        raise HelloError("Windows Hello hanya tersedia di Windows.")
    try:
        asyncio.run(_verify_async(message))
    except HelloError:
        raise
    except ImportError:
        raise HelloError("Paket winrt belum terpasang. Jalankan: pip install -r requirements.txt") from None
    except Exception as e:
        raise HelloError(f"Windows Hello tidak dapat dijalankan ({type(e).__name__}).") from None
    return True
