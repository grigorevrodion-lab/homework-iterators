import requests
import os

BASE_URL = "https://cloud-api.yandex.net/v1/disk/resources"


def get_headers():
    return {
        "Authorization": f"OAuth {os.getenv('YANDEX_TOKEN')}"
    }


def create_folder(path):
    return requests.put(
        BASE_URL,
        headers=get_headers(),
        params={"path": path}
    )


def get_folder_info(path):
    return requests.get(
        BASE_URL,
        headers=get_headers(),
        params={"path": path}
    )
