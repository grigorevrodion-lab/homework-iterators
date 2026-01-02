import os
import pytest
from src.yandex_disk import create_folder, get_folder_info


def has_token() -> bool:
    return bool(os.getenv("YANDEX_TOKEN"))


@pytest.mark.skipif(not has_token(), reason="YANDEX_TOKEN is not set")
def test_create_folder_success():
    folder_name = "pytest_test_folder"
    response = create_folder(folder_name)

    assert response.status_code in (201, 409), f"{response.status_code}: {response.text}"

    check = get_folder_info(folder_name)
    assert check.status_code == 200, f"{check.status_code}: {check.text}"


@pytest.mark.skipif(not has_token(), reason="YANDEX_TOKEN is not set")
@pytest.mark.parametrize(
    "path, expected_status",
    [
        ("", 400),
        ("/", 400),
    ]
)
def test_create_folder_negative(path, expected_status):
    response = create_folder(path)
    assert response.status_code == expected_status, f"{response.status_code}: {response.text}"


def test_create_folder_without_token(monkeypatch):
    monkeypatch.delenv("YANDEX_TOKEN", raising=False)

    response = create_folder("no_token_folder")
    assert response.status_code == 401
