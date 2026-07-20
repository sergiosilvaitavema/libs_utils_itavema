import os
import time
from datetime import datetime, timedelta

from rpaflow.browser import Browser
from rpaflow.log import Log


class ItauUtils:

    URL = "https://www.itau.com.br/empresas"
    _TIMEOUT_LOADING = 60

    # --- Seletores XPath ---
    _MENU_LOGIN = "//div[@class='idl-menu-right-wrap']//div[@class='idl-more-acess-open-desktop']"
    _SELECT_TIPO_LOGIN = "//select[@id='idl-more-access-select-login']"
    _INPUT_OPERADOR = "//input[@id='idl-more-access-input-operator']"
    _BTN_ENVIAR_OPERADOR = "//button[@id='idl-more-access-submit-button' and normalize-space()='Acessar']"
    _LOADING = "//img[@alt='Carregando']"
    _BTN_ACESSAR = "//a[@id='acessar']"
    _TECLADO_DIGITO = "//form[@id='frmTecladoPessoJuridica']//a[@id='campoTeclado' and contains(text(),'{digito}')]"
    _RADIO_BASICO = "//input[@id='rdBasico']"
    _BTN_CONTINUAR = "//a[@data-dd-context='continuar_basico']"
    _BTN_USER_MENU = "//button[@id='user-menu-button']"
    _INPUT_SEARCH_ACCOUNT = "//input[@name='search-account']"
    _BTN_COBRANCA = "//button[@aria-label='Cobrança botão']"
    _BTN_IR_PARA_COBRANCA = "//button[@aria-label='Ir para Cobrança botão']"
    _BTN_EXTRATO_FRANCESINHA = "//a[aria-label='Extrato de movimentação (Francesinha) Você está em Consultar']"
    _BTN_EXTRATO_TITULOS = "//a[@aria-label='Extrato de movimentação de títulos Você está em Consultar']"
    _BTN_DETALHADA = "//button[normalize-space()='Detalhada']"

    def __init__(self, log:Log):
        self._browser = Browser()
        self._page = self._browser.page
        self._url = 'https://www.itau.com.br/empresas/abra-sua-conta?utm_source=google&utm_medium=search&utm_campaign=gl-midia_paga-aquisicao_pj-conversao-search_marca_verde&utm_content=google-1st-cpa-cross-audience-abra_sua_conta_empre-paid_search-rob_abra_sua_conta_empresarial-ga6163634234&gclsrc=aw.ds&gad_source=1&gad_campaignid=20427249292&gbraid=0AAAAADOnqr6OypH_SuslATox8ysL2Sufr&gclid=CjwKCAjwx7LSBhB3EiwAjcodxDU_cThLrmISSfKm2xJ_4xH5xFzwNGt9s-pDvGHJNI0tXtXeeNDXaxoClgkQAvD_BwE'
        self._log = Log("PortalItau")

    def _login(self, cod_operador:str, senha:str):
        self._log.info("=== INICIANDO AUTOMACAO ===")
        self.__abrir_portal()
        self.__selecionar_tipo_login()
        self.__informar_operador(cod_operador)
        self.__enviar_operador()
        self.__digitar_senha(senha)
        self.__clicar_acessar()
        self.__selecionar_perfil()
        self.__clicar_continuar()

        

    # ---- portal ----

    def __abrir_portal(self):
        self._log.info(f"Abrindo portal: {self.URL}")
        self._browser.start(self.URL)
        self._browser.maximize()
        self._log.success("Portal aberto.")

    def __selecionar_tipo_login(self):
        self._log.info("Abrindo menu de login...")
        self._browser.click(self._MENU_LOGIN, recursive=True)
        self._log.info("Selecionando 'Codigo do operador'...")
        self._browser.select_in_frames(
            self._SELECT_TIPO_LOGIN,
            "Código do operador",
        )
        self._log.success("Tipo de login selecionado.")

    def __informar_operador(self, operador:str):
        self._log.info(f"Informando operador: {operador}")
        self._browser.type_text(
            self._INPUT_OPERADOR,
            operador,
            recursive=True,
        )
        self._log.success("Operador informado.")

    def __enviar_operador(self):
        self._log.info("Enviando operador...")
        self._browser.click(self._BTN_ENVIAR_OPERADOR, recursive=True)
        self._aguardar_loading()
        self._log.success("Operador enviado.")

    def __digitar_senha(self, senha:str):
        self._log.info("Aguardando tela de senha...")
        time.sleep(30)
        self._log.info("Digitando senha no teclado virtual...")
        for i, digito in enumerate(senha, 1):
            xpath = self._TECLADO_DIGITO.format(digito=digito)
            self._browser.click(xpath, recursive=True)
            self._log.info(f"Digito {i}/{len(senha)} digitado.")
            time.sleep(0.5)
        self._log.success("Senha digitada.")

    def __clicar_acessar(self):
        self._log.info("Clicando em 'Acessar'...")
        self._browser.click(self._BTN_ACESSAR, recursive=True)
        time.sleep(3)
        self._log.success("Acessando...")

    def __selecionar_perfil(self):
        self._log.info("Selecionando perfil 'Basico'...")
        self._browser.click(self._RADIO_BASICO, recursive=True)
        time.sleep(1)
        self._log.success("Perfil selecionado.")

    def __clicar_continuar(self):
        self._log.info("Clicando em 'Continuar'...")
        self._browser.click(self._BTN_CONTINUAR, recursive=True)
        self._browser.wait_for_element("body", timeout=15000)
        time.sleep(15)
        self._log.success("Perfil confirmado.")

    # ---- loading / estabilidade ----

    def _aguardar_loading(self):
        tempo_inicial = time.time()
        while time.time() - tempo_inicial < self._TIMEOUT_LOADING:
            try:
                if not self._browser.is_visible(self._LOADING, timeout=2000):
                    return
            except Exception:
                return
            time.sleep(2)
        print("Aviso: loading nao desapareceu dentro do tempo limite.")

    def _aguardar_pagina_estavel(self, timeout=60, intervalo=2):
        tempo_inicial = time.time()
        while time.time() - tempo_inicial < timeout:
            try:
                self._browser.wait_for_load_state("networkidle", timeout=10000)
                print("Pagina estavel, sem requisicoes pendentes.")
                return
            except Exception:
                time.sleep(intervalo)
        print("Aviso: pagina nao estabilizou no tempo limite.")

    # ---- trocar conta (shadow DOM) ----

    def _trocar_conta(self, numero_conta: str) -> bool:
        self._browser.click(self._BTN_USER_MENU, recursive=True)

        self._log.info(f"Digitando conta: {numero_conta}")
        self._limpar_e_digitar(self._INPUT_SEARCH_ACCOUNT, numero_conta)
        time.sleep(4)

        self._log.info("Verificando se item da conta apareceu...")
        try:
            locator = self._browser.page.locator(f"text={numero_conta}").first
            locator.wait_for(state="visible", timeout=8000)

            self._log.info("Conta encontrada! Clicando...")
            locator.click(force=True)

            self._log.info("Aguardando troca de conta...")
            self._aguardar_pagina_estavel()
            time.sleep(20)
            self._log.success("Conta trocada.")
            return True
        except Exception:
            return False

    def _navegar_cobranca(self):
        self._log.info("Navegando para Cobranca...")
        self._aguardar_pagina_estavel()
        self._log.info("Passando mouse sobre 'Cobranca'...")
        self._hover_em_shadow(self._BTN_COBRANCA)
        time.sleep(1)
        self._aguardar_pagina_estavel()
        self._log.info("Clicando em 'Ir para Cobranca'...")
        time.sleep(3)
        self._clicar_em_shadow(self._BTN_IR_PARA_COBRANCA)
        self._aguardar_pagina_estavel()
        time.sleep(2)
        self._log.success("Cobranca acessada.")

    def _navegar_consultas(self, cfg: dict):
        frame = self._browser.page.frame_locator("iframe#iframe-nf2-")

        self._log.info("Aguardando pagina estavel...")
        self._aguardar_pagina_estavel()

        self._log.info("Clicando em 'Extrato de movimentacao (Francesinha)'...")
        frame.locator("a[aria-label='Extrato de movimentação (Francesinha) Você está em Consultar']").click(force=True)

        self._log.info("Aguardando pagina estavel...")
        self._aguardar_pagina_estavel()
        time.sleep(1)

        self._log.info("Clicando em 'Extrato de movimentacao de titulos'...")
        frame.locator("a:has-text('Extrato de movimentação de títulos')").click(force=True)

        self._log.info("Aguardando pagina estavel...")
        self._aguardar_pagina_estavel()
        time.sleep(1)

        self._log.info("Clicando em 'Detalhada'...")
        frame.locator("button:has-text('Detalhada')").click(force=True)

        self._log.info("Aguardando pagina estavel...")
        self._aguardar_pagina_estavel()
        time.sleep(1)

        

        self._log.info("Abrindo combo 'Filtrar movimentacoes por'...")
        frame.locator("xpath=//label[starts-with(text(),' Filtrar movimentações por')]/ancestor::div[1]//voxel-select").click(force=True)
        time.sleep(1)

        self._log.info("Selecionando 'Liquidacoes'...")
        frame.locator("xpath=//voxel-option[./span[normalize-space()='Liquidações']]").click(force=True)

        self._log.info("Aguardando pagina estavel...")
        self._aguardar_pagina_estavel()
        time.sleep(1)

        data_ontem = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")

        self._log.info(f"Preenchendo data movimentação: {data_ontem}...")
        frame.locator('xpath=//app-datepicker[@datelabel="Data de movimentação"]//input[@formcontrolname="date"]').fill(data_ontem, force=True)

        self._log.info(f"Preenchendo data inicial: {data_ontem}...")
        frame.locator("xpath=//label[normalize-space()='Data inicial']/ancestor::div[1]//input[@voxelmask='date']").fill(data_ontem, force=True)

        self._log.info(f"Preenchendo data final: {data_ontem}...")
        frame.locator("xpath=//label[normalize-space()='Data final']/ancestor::div[1]//input[@voxelmask='date']").fill(data_ontem, force=True)

        self._log.info("Aguardando pagina estavel...")
        self._aguardar_pagina_estavel()
        time.sleep(1)

        self._log.info("Abrindo combo 'Formato do arquivo'...")
        frame.locator("xpath=//label[starts-with(text(),' Formato do arquivo')]/ancestor::div[1]//voxel-select").click(force=True)
        time.sleep(1)

        self._log.info("Selecionando 'Excel'...")
        frame.locator("xpath=//voxel-option/span[normalize-space()='Excel']").click(force=True)

        self._log.info("Aguardando pagina estavel...")
        self._aguardar_pagina_estavel()
        time.sleep(2)

        self._log.info("Clicando em 'Solicitar'...")
        frame.locator("xpath=//button[normalize-space()='Solicitar']").click(force=True)

        self._log.info("Aguardando resposta do servidor...")
        self._aguardar_pagina_estavel()
        time.sleep(5)

        self._tratar_resposta_solicitacao(frame, data_ontem, cfg)

    def _tratar_resposta_solicitacao(self, frame, data_ontem, cfg: dict):
        """Verifica se extrato ja foi solicitado e trata o cenario."""
        self._log.info("Verificando resposta da solicitacao...")
        self._aguardar_pagina_estavel()
        time.sleep(5)

        msg_ja_solicitado = frame.locator("xpath=//section[contains(text(),'Extrato já solicitado para este período.')]")

        try:
            if msg_ja_solicitado.is_visible(timeout=8000):
                self._log.warning("Extrato ja solicitado para este periodo. Verificando disponibilidade...")
                self._aguardar_baixar_extrato(frame, data_ontem, cfg)
                return
        except Exception:
            pass

        msg_sucesso = frame.locator("xpath=//section[contains(text(),'Solicitação enviada com sucesso')]")
        try:
            if msg_sucesso.is_visible(timeout=5000):
                self._log.success("Solicitacao enviada com sucesso!")
                self._aguardar_pagina_estavel()
                return
        except Exception:
            pass

        self._log.info("Mensagem de confirmacao nao detectada. Verificando disponibilidade do extrato...")
        self._aguardar_baixar_extrato(frame, data_ontem, cfg)

    def _aguardar_baixar_extrato(self, frame, data_ontem, cfg: dict, max_tentativas=10, intervalo=10):
        """Loop para aguardar e baixar o extrato, atualizando a tabela ate encontrar."""
        pasta = cfg["download_pasta"]
        arquivo = cfg["download_arquivo"]
        self._preparar_pasta(pasta, arquivo)

        self._log.info("Clicando em 'Consultar solicitacoes de extrato de titulos'...")
        link_consultar = frame.locator("xpath=(//a[starts-with(normalize-space(),'consultar solicitações de extrato de títulos')])[last()]")
        if not self._clique_com_retry(link_consultar, "Consultar solicitacoes de extrato"):
            self._log.error("Nao foi possivel acessar as solicitacoes de extrato.")
            return
        self._aguardar_pagina_estavel()
        time.sleep(5)

        for tentativa in range(1, max_tentativas + 1):
            self._log.info(f"Tentativa {tentativa}/{max_tentativas}: Verificando extrato para {data_ontem}...")

            btn_baixar = frame.locator(
                f"xpath=//table[@aria-label='Tabela históricos das solicitações']"
                f"/tbody/tr/td[1][contains(text(),'{data_ontem}')]"
                f"/ancestor::tr[1]/td[last()]//button[@content='Baixar Excel']"
            )

            try:
                if btn_baixar.is_visible(timeout=5000):
                    self._log.success(f"Extrato encontrado! Iniciando download...")

                    page = self._browser.page
                    with page.expect_download(timeout=60000) as download_info:
                        btn_baixar.click(force=True)

                    download = download_info.value
                    caminho = os.path.join(pasta, arquivo)
                    download.save_as(caminho)

                    self._log.success(f"Download concluido: {caminho}")
                    self._aguardar_pagina_estavel()
                    return
            except Exception as e:
                self._log.warning(f"Erro no download: {e}")

            self._log.info(f"Extrato ainda nao disponivel. Clicando em 'Atualizar tabela'...")
            btn_atualizar = frame.locator("xpath=//button[./span[normalize-space()='atualizar tabela']]")
            self._clique_com_retry(btn_atualizar, "Atualizar tabela")
            self._aguardar_pagina_estavel()
            time.sleep(intervalo)

        self._log.error(f"Extrato para {data_ontem} nao disponivel apos {max_tentativas} tentativas.")

    def _preparar_pasta(self, pasta: str, arquivo: str):
        """Cria a pasta se nao existir e remove o arquivo anterior se existir."""
        os.makedirs(pasta, exist_ok=True)
        caminho = os.path.join(pasta, arquivo)
        if os.path.exists(caminho):
            self._log.info(f"Removendo arquivo anterior: {caminho}")
            os.remove(caminho)

    def _encontrar_locator(self, xpath: str):
        """Busca elemento no main frame (CSS) e depois recursivamente em todos os iframes (XPath)."""
        css = self._xpath_para_css(xpath)
        try:
            loc = self._browser.page.locator(f"css={css}")
            if loc.count() > 0:
                return loc.first
        except Exception:
            pass
        for frame in self._browser.page.frames:
            try:
                loc = frame.locator(f"xpath={xpath}")
                if loc.count() > 0:
                    return loc.first
            except Exception:
                continue
        raise Exception(f"Elemento nao encontrado em nenhum frame: {xpath}")

    def _clicar_em_shadow(self, xpath: str, first: bool = False):
        """Clica em elemento dentro de shadow DOM ou iframe via busca recursiva."""
        self._encontrar_locator(xpath).click()

    def _hover_em_shadow(self, xpath: str):
        """Passa mouse sobre elemento dentro de shadow DOM ou iframe via busca recursiva."""
        self._encontrar_locator(xpath).hover()

    @staticmethod
    def _xpath_para_css(xpath: str) -> str:
        """Converte XPath simples para CSS selector para uso em shadow DOM."""
        import re
        s = xpath.lstrip("/")
        # //tag[@attr-name='val']  →  tag[attr-name='val']
        m = re.match(r"^(\w+)\[@([\w-]+)='([^']+)'\]$", s)
        if m:
            tag, attr, val = m.groups()
            return f"{tag}[{attr}='{val}']"
        # //tag  →  tag
        m = re.match(r"^(\w+)$", s)
        if m:
            return m.group(1)
        return s

    def _digitar_em_shadow(self, xpath: str, texto: str):
        """Digita em input dentro de shadow DOM ou iframe via busca recursiva."""
        locator = self._encontrar_locator(xpath)
        locator.wait_for(state="visible", timeout=10000)
        locator.fill(texto)
        
    def _digitar_em_shadow_nature(self, xpath: str, texto: str):
        """Digita em input dentro de shadow DOM ou iframe via busca recursiva."""
        locator = self._encontrar_locator(xpath)
        locator.wait_for(state="visible", timeout=10000)
        locator.type(texto)        

    def _limpar_e_digitar(self, xpath: str, texto: str):
        """Limpa o campo e digita o texto dentro de shadow DOM ou iframe via busca recursiva."""
        locator = self._encontrar_locator(xpath)
        locator.clear()
        time.sleep(0.5)
        locator.fill(texto)

    def _clicar_btn_conta_em_shadow(self, texto_span: str):
        """Clica no botao cujo span contem o texto da conta via Playwright locator."""
        self._browser.page.locator(f"text={texto_span}").first.click()

    def _clique_com_retry(self, locator, descricao: str, max_tentativas=3, intervalo=2):
        """Tenta clicar em um elemento varias vezes ate ter sucesso."""
        for tentativa in range(1, max_tentativas + 1):
            try:
                self._log.info(f"Tentativa {tentativa}/{max_tentativas}: Clicando em '{descricao}'...")
                locator.wait_for(state="visible", timeout=10000)
                locator.click(force=True)
                self._log.success(f"Clique em '{descricao}' realizado.")
                return True
            except Exception as e:
                self._log.warning(f"Falha no clique '{descricao}': {e}")
                if tentativa < max_tentativas:
                    time.sleep(intervalo)
        self._log.error(f"Nao foi possivel clicar em '{descricao}' apos {max_tentativas} tentativas.")
        return False

    def _obter_browser(self) -> Browser:
        return self._browser