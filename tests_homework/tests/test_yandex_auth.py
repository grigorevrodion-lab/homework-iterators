import os
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.skipif(
    not os.getenv("YANDEX_LOGIN") or not os.getenv("YANDEX_PASSWORD"),
    reason="Set YANDEX_LOGIN and YANDEX_PASSWORD env vars to run this test"
)
def test_yandex_auth():
    options = webdriver.ChromeOptions()

    options.add_argument("--window-size=1200,900")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://passport.yandex.ru/auth")

        # 1) Ждём появления поля логина (у Яндекса бывает name=login или id=passp-field-login)
        login_field = wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.NAME, "login")),
                EC.presence_of_element_located((By.ID, "passp-field-login"))
            )
        )
        login_field.clear()
        login_field.send_keys(os.getenv("YANDEX_LOGIN"))
        login_field.send_keys(Keys.ENTER)

        # 2) Ждём поля пароля (name=passwd или id=passp-field-passwd)
        password_field = wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.NAME, "passwd")),
                EC.presence_of_element_located((By.ID, "passp-field-passwd"))
            )
        )
        password_field.clear()
        password_field.send_keys(os.getenv("YANDEX_PASSWORD"))
        password_field.send_keys(Keys.ENTER)

        # 3) Проверка успешного входа:
        # ждём, что URL сменится и в нём не будет /auth
        wait.until(lambda d: "/auth" not in d.current_url)

        assert "passport.yandex" in driver.current_url

    finally:
        driver.quit()
