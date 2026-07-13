import time
from rpaflow.browser import Browser


class DealerUtils:
    def __init__(self, browser: Browser):
        self._browser = browser
        self._page = browser.page

    def _logar(self, user: str, password:str):
        """Login no portal."""
        self._log.info("[PgtoDia] Realizando login")

        self._browser.find_element_in_frames(
            '//input[contains(@id, "vUSUARIO_IDENTIFICADORALTERNATIVO")]', timeout=10000
        )
        self._browser.fill_text(
            '//input[contains(@id, "vUSUARIO_IDENTIFICADORALTERNATIVO")]', user
        )
        self._browser.click("//input[contains(@src, 'confirmar')]")
        time.sleep(1)
        self._browser.fill_text("//input[contains(@id, 'USUARIOSENHA_SENHA')]", password)
        self._browser.wait_for_load_state("domcontentloaded")
        time.sleep(2)
        self._browser.click("//input[@id='IMAGE3']")
        time.sleep(2)
        self._log.info("[PgtoDia] Login realizado")