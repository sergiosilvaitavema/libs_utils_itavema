import time
from rpaflow.browser import Browser



class DealerUtils:

    DEPARA_EMPRESA = {
        "RENAULT": "RENAULT - GASTAO MATRIZ",
        "TOYOTA": "TOYOTA - GASTAO",
        "FIAT": "FIAT - NOVA IGUAÇU",
        "DAFRA": "ITVA - COMERCIO MATRIZ",
        "HYUNDAI": "HYUNDAI - CAMPO GRANDE",
        "GEELY": "GEELY - GASTAO MATRIZ",
        "BYD": "BYD - RECREIO",
    }

    TOOLBAR_EMPRESA = (
        "(//div[contains(@class,'x-toolbar-layout-ct') "
        "and contains(@class,'x-small-editor')])[2]"
        "/table/tbody/tr/td[2]/table/tbody/tr/td[1]/table/tbody/tr/td[4]"
    )

    def __init__(self):
        self._browser = Browser()
        self._page = self._browser.page
        self._url = 'http://10.14.73.231/Portal/default.html'
        

    def obter_browser(self) -> Browser:
        """Obter instancia do browser"""
        return self._browser

    def logar(self, user: str, password:str):
        """Login no portal."""
        print("[PgtoDia] Realizando login")

        self._browser.start(url=self._url)

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
        print("[PgtoDia] Login realizado")

    def navegar_empresa(self, marca: str):
        empresa_full = self.DEPARA_EMPRESA.get(marca)
        if not empresa_full:
            raise Exception(f"Empresa '{marca}' nao encontrada no depara")

        try:
            if self._page.locator(f"//button[text()='{empresa_full}']").first.is_visible():
                print(f"[Bordero] Ja esta na empresa {empresa_full}")
                return
        except Exception:
            pass

        self._browser.wait_for_element(self.TOOLBAR_EMPRESA, state="visible")
        time.sleep(2)
        self._browser.click(self.TOOLBAR_EMPRESA)
        time.sleep(2)
        self._browser.hover(f"//a[.//span[text()='{marca}']]")
        time.sleep(1)
        self._browser.click(f"//a[.//span[text()='{empresa_full}']]")
        time.sleep(1)

    def fechar_todas_janelas(self):
        """Fecha todas as janelas abertas no portal."""
        seletor = "(//div[@class='x-window-tl']//div[@class='x-tool x-tool-close'])[1]"
        while True:
            try:
                btn = self._page.locator(seletor)
                if btn.is_visible(timeout=1000):
                    btn.click()
                    time.sleep(1)
                    print("[Bordero] Janela fechada")
                else:
                    break
            except Exception:
                break

    def esperar_pagina(self):
        self._browser.wait_for_load_state("domcontentloaded")