import pytest
from core.services import Services
from core import donggle
from core.auth_service import AuthError


@pytest.fixture
def env(tmp_path):
    usb = tmp_path / "usb"; usb.mkdir()
    s = Services(":memory:")
    uid = s.auth.register("alice", "passwordku1", "passwordku1", str(usb))
    return s, str(usb), uid


def test_register_login_logout(env):
    s, usb, _ = env
    pub = donggle.verify_donggle(usb, s.users)
    s.auth.login("alice", "passwordku1", pub)
    assert s.session.active and len(s.session.get_subkey("file")) == 32
    s.auth.logout()
    with pytest.raises(PermissionError):
        s.session.get_subkey("file")


def test_password_not_plaintext_in_db(env):
    s, _, _ = env
    row = s.users.by_username("alice")
    assert "passwordku1" not in row["password_hash"] and row["password_hash"].startswith("$argon2id$")


def test_wrong_password_generic_error(env):
    s, usb, _ = env
    pub = donggle.verify_donggle(usb, s.users)
    with pytest.raises(AuthError) as e1:
        s.auth.login("alice", "salahsalah", pub)
    with pytest.raises(AuthError) as e2:
        s.auth.login("tidakada", "salahsalah", pub)
    assert str(e1.value) == str(e2.value)


def test_donggle_missing_or_fake(env, tmp_path):
    s, usb, _ = env
    empty = tmp_path / "empty"; empty.mkdir()
    with pytest.raises(donggle.DonggleError):
        donggle.verify_donggle(str(empty), s.users)
    # donggle palsu: file ada tapi kunci tidak terdaftar
    fake = tmp_path / "fake"; fake.mkdir()
    donggle.create_donggle(str(fake))
    with pytest.raises(donggle.DonggleError):
        donggle.verify_donggle(str(fake), s.users)


def test_donggle_of_other_user_rejected(env, tmp_path):
    s, _, _ = env
    usb2 = tmp_path / "usb2"; usb2.mkdir()
    s.auth.register("bob", "passwordbob1", "passwordbob1", str(usb2))
    pub_bob = donggle.verify_donggle(str(usb2), s.users)
    with pytest.raises(AuthError):
        s.auth.login("alice", "passwordku1", pub_bob)


def test_change_password_keeps_data_readable(env):
    s, usb, _ = env
    pub = donggle.verify_donggle(usb, s.users)
    s.auth.login("alice", "passwordku1", pub)
    s.save_message("Judul", "Isi rahasia")
    s.auth.change_password("passwordku1", "passwordbaru2", "passwordbaru2")
    s.auth.logout()
    s.auth.login("alice", "passwordbaru2", pub)
    mid = s.list_message_titles()[0][0]
    assert s.read_message(mid) == ("Judul", "Isi rahasia")


def test_db_stores_ciphertext_only(env):
    s, usb, _ = env
    s.auth.login("alice", "passwordku1", donggle.verify_donggle(usb, s.users))
    s.save_message("Judul", "RAHASIA-BESAR")
    raw = bytes(s.messages.list(s.session.user_id)[0]["ciphertext"])
    assert b"RAHASIA-BESAR" not in raw


def test_log_creates_valid_chain(env):
    s, usb, _ = env
    s.auth.login("alice", "passwordku1", donggle.verify_donggle(usb, s.users))
    s.log("LOGIN")
    assert s.chain.verify()[0] and len(s.chain.blocks()) == 2
