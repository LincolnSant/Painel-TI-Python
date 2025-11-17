from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.columns import Columns
from rich.table import Table
import os
import psutil
import shutil
import time
import datetime
import wmi
import socket
import json

console = Console()

# --- ARQUIVO DE CONFIGURAÇÃO DO MAPA ---
ARQUIVO_MAPA = 'devices.json'  # Onde os IPs serão salvos
DISPOSITIVOS = {}  # A memória global que vai guardar o mapa

# --- Gaveta 0 (Carrega o mapa de rede do JSON para a memória) ---#


def carregar_mapa_rede():
    """Tenta carregar o mapa de dispositivos do JSON para a memória."""
    global DISPOSITIVOS  # Avisa que vamos mexer na variável global
    if not os.path.exists(ARQUIVO_MAPA):
        console.print(
            f"[bold red]AVISO:[/bold red] Arquivo '{ARQUIVO_MAPA}' não encontrado. Criando um novo.")
        console.print("[dim]Use a Opção 14 para adicionar dispositivos.[/dim]")
        DISPOSITIVOS = {}
        time.sleep(2.5)
        return

    try:
        with open(ARQUIVO_MAPA, 'r') as f:
            DISPOSITIVOS = json.load(f)
        console.print(
            f"[green]Mapa de rede '{ARQUIVO_MAPA}' carregado com {len(DISPOSITIVOS)} dispositivos![/green]")
        time.sleep(1.5)
    except Exception as e:
        console.print(
            f"[bold red]ERRO CRÍTICO ao carregar mapa:[/bold red] {e}")
        DISPOSITIVOS = {}
# --- Fim da gaveta 0 ---#

# --- Gaveta 1 (Salva o mapa da memória de volta para o JSON) ---#


def salvar_mapa_rede():
    """Salva o mapa de dispositivos atual (da memória) no arquivo JSON."""
    try:
        with open(ARQUIVO_MAPA, 'w') as f:
            # Salva o dicionário global DISPOSITIVOS
            json.dump(DISPOSITIVOS, f, indent=4)
        console.print(
            "\n[bold green]>>> Mapa de rede salvo com sucesso! <<<[/bold green]")
    except Exception as e:
        console.print(f"[bold red]ERRO AO SALVAR MAPA:[/bold red] {e}")
# --- Fim da gaveta 1 ---#


# --- Gaveta 2 (Desenha o menu principal na tela) ---#
def desenhar_menu():
    os.system('cls' if os.name == 'nt' else 'clear')

    console.print(
        Rule("[bold cyan]SysAdmin Helper 3.0[/bold cyan]", style="cyan"))
    console.print(
        Rule("[bold white]Painel Rápido - Auxiliar de TI (Atacado/Varejo)[/bold white]"))

    menu_verificacao = (
        "[dim]--- Verificação Rápida ---\n"
        "[bold cyan]0) CHECK-UP GERAL DA LOJA[/bold cyan]\n"
        "[yellow]1)[/yellow] Pingar Servidor Principal\n"
        "[yellow]2)[/yellow] Pingar uma Impressora (Específica)\n"
        "[yellow]3)[/yellow] Pingar um PDV (Específico)\n"
        "[yellow]4)[/yellow] Status do Meu PC (IP/CPU/RAM)\n"
        "[yellow]5)[/yellow] Testar Porta Específica (Firewall)\n"
        "[yellow]6)[/yellow] Monitor de Processos Ativos"
    )

    menu_manutencao = (
        "[dim]--- Manutenção ---\n"
        "[yellow]7)[/yellow] Verificar Espaço em Disco\n"
        "[yellow]8)[/yellow] Limpar Arquivos Temporários\n"
        "[yellow]9)[/yellow] Limpar Cache DNS (flushdns)\n"
        "[yellow]10)[/yellow] Renovar IP (release/renew)\n"
        "[yellow]11)[/yellow] Gerenciar Spooler de Impressão\n"
        "[yellow]12)[/yellow] Ver Conexões Ativas (Rápido)\n"
        "[yellow]13)[/yellow] Ver Conexões (com Nomes) (Lento)\n"
        "[bold yellow]14) Gerenciar Mapa de Rede (Add/Rem)[/bold yellow]\n\n"
        "[yellow]15)[/yellow] Sair"
    )

    console.print(Columns([
        Panel(menu_verificacao, title="VERIFICAR",
              border_style="green", padding=1),
        Panel(menu_manutencao, title="MANUTENÇÃO",
              border_style="red", padding=1)
    ], expand=True, equal=True))

    return console.input("\n[bold]Escolha uma opção: [/bold]")
# --- Fim da gaveta 2 ---#

# --- Gaveta 3 (Sub-menu para gerenciar o mapa de rede) ---#


def gerenciar_mapa():
    """Sub-menu para Adicionar ou Remover dispositivos do mapa (JSON)."""
    while True:
        os.system('cls')
        console.print(
            Rule("[bold cyan]Gerenciador do Mapa de Rede[/bold cyan]"))

        tabela = Table(title="Dispositivos Atuais no Mapa", border_style="dim")
        tabela.add_column("Chave (ex: pdv1)", style="cyan", width=20)
        tabela.add_column("Nome Amigável", style="white", width=30)
        tabela.add_column("Endereço IP", style="magenta", width=15)

        if not DISPOSITIVOS:
            console.print("[yellow]O mapa de rede está vazio.[/yellow]")
        else:
            for chave, dados in DISPOSITIVOS.items():
                tabela.add_row(chave, dados['nome'], dados['ip'])
            console.print(tabela)

        console.print("\n[1] Adicionar/Atualizar Dispositivo")
        console.print("[2] Remover Dispositivo")
        console.print("[3] Voltar ao Menu Principal (Salva mudanças)")

        sub_opcao = console.input("\nEscolha uma opção: ").strip()

        if sub_opcao == '1':
            console.print("\n--- Adicionar/Atualizar Dispositivo ---")
            chave = console.input(
                "Digite a [bold]Chave[/bold] (ex: pdv3, imp_acougue): ").strip()
            if not chave:
                console.print("[red]Chave não pode ser vazia.[/red]")
            else:
                nome = console.input(
                    f"Digite o [bold]Nome Amigável[/bold] para '{chave}': ").strip()
                ip = console.input(
                    f"Digite o [bold]IP[/bold] para '{chave}': ").strip()

                DISPOSITIVOS[chave] = {"ip": ip, "nome": nome}
                console.print(f"\n[green]Dispositivo '{chave}' salvo![/green]")
            time.sleep(1.5)

        elif sub_opcao == '2':
            console.print("\n--- Remover Dispositivo ---")
            chave = console.input(
                "Digite a [bold]Chave[/bold] do dispositivo a remover: ").strip()

            if chave in DISPOSITIVOS:
                removido = DISPOSITIVOS.pop(chave)
                console.print(
                    f"\n[green]Dispositivo '{chave}' ({removido['nome']}) removido![/green]")
            else:
                console.print(
                    f"\n[red]ERRO: Chave '{chave}' não encontrada no mapa.[/red]")
            time.sleep(1.5)

        elif sub_opcao == '3':
            salvar_mapa_rede()  # Salva as mudanças feitas
            time.sleep(1.5)  # Pausa para ler a mensagem de "salvo"
            break

        else:
            console.print("\n[red]Opção inválida.[/red]")
            time.sleep(1)
# --- Fim da gaveta 3 ---#

# --- Gaveta 4 (Pinga todos os dispositivos do mapa de rede) ---#


def checkup_geral():
    """Roda um ping em TODOS os dispositivos cadastrados no MAPA DE REDE."""
    console.print(
        Rule("[bold cyan]Iniciando Check-up Geral da Loja[/bold cyan]"))

    tabela_status = Table(title="Status da Rede", border_style="dim")
    tabela_status.add_column("Dispositivo", style="cyan", width=30)
    tabela_status.add_column("IP", style="magenta", width=15)
    tabela_status.add_column("Status", style="white")

    falhas = 0

    if not DISPOSITIVOS:
        console.print(
            "[yellow]O mapa de rede está vazio. Adicione dispositivos na Opção 14.[/yellow]")
        return

    for chave, dispositivo in DISPOSITIVOS.items():
        ip = dispositivo['ip']
        nome = dispositivo['nome']

        console.print(f"\n[yellow]Testando:[/yellow] {nome} ({ip})...")

        comando_ping = f"ping -n 2 {ip}" if os.name == 'nt' else f"ping -c 2 {ip}"

        resultado = os.system(f"{comando_ping} > {os.devnull} 2>&1")

        if resultado == 0:
            tabela_status.add_row(nome, ip, "[bold green]ONLINE[/bold green]")
        else:
            tabela_status.add_row(nome, ip, "[bold red]FALHA[/bold red]")
            falhas += 1

    console.print(Rule("[bold cyan]Relatório do Check-up[/bold cyan]"))
    console.print(tabela_status)

    if falhas > 0:
        console.print(
            f"\n[bold red]ATENÇÃO:[/bold red] {falhas} dispositivo(s) estão offline!")
    else:
        console.print(
            f"\n[bold green]Tudo Certo![/bold green] Todos os dispositivos críticos estão online.")
# --- Fim da gaveta 4 ---#

# --- Gaveta 5 (Função que executa o ping individual) ---#


def pingar_servidor(host, nome_amigavel):
    """Função para pingar um host e mostrar o status."""
    console.print(
        f"\n[bold yellow]Pingando {nome_amigavel} ({host})...[/bold yellow]")

    if os.name == 'nt':
        comando = f"ping -n 2 {host}"
    else:
        comando = f"ping -c 2 {host}"
    resultado = os.system(comando)

    if resultado == 0:
        console.print(
            f"\n[bold green]SUCESSO![/bold green] O {nome_amigavel} ({host}) está respondendo.")
    else:
        console.print(
            f"\n[bold red]FALHA![/bold red] O {nome_amigavel} ({host}) está INACESSÍVEL.")
# --- Fim da gaveta 5 ---#

# --- Gaveta 6 (Função que filtra o mapa para pingar por tipo) ---#


def pingar_dispositivo_por_tipo(prefixo_chave, tipo_nome):
    """Filtra o mapa DISPOSITIVOS e mostra um sub-menu para pingar."""
    console.print(f"\n--- Pingar {tipo_nome} Específico ---")

    lista_filtrada = {}
    for chave, dispositivo in DISPOSITIVOS.items():
        if chave.startswith(prefixo_chave):
            lista_filtrada[chave] = dispositivo

    if not lista_filtrada:
        console.print(
            f"[red]Nenhum dispositivo do tipo '{tipo_nome}' cadastrado no mapa.[/red]")
        return

    console.print(f"[dim]Dispositivos '{tipo_nome}' disponíveis:[/dim]")
    for chave, dev in lista_filtrada.items():
        console.print(
            f"  - [bold cyan]{chave}[/bold cyan]: {dev['nome']} ({dev['ip']})")

    chave_escolhida = console.input(
        f"\nDigite a Chave do {tipo_nome} (ex: {list(lista_filtrada.keys())[0] if lista_filtrada else ''}): ").strip()

    if chave_escolhida in lista_filtrada:
        dispositivo = lista_filtrada[chave_escolhida]
        pingar_servidor(dispositivo['ip'], dispositivo['nome'])
    else:
        console.print(
            f"\n[bold red]ERRO: Chave '{chave_escolhida}' não encontrada![/bold red]")
# --- Fim da gaveta 6 ---#

# --- Gaveta 7 (Testa se uma porta TCP específica está aberta) ---#


def testar_porta():
    """Tenta conectar a uma porta TCP específica em um host."""
    console.print(
        Rule("[bold cyan]Teste de Conexão de Porta (TCP)[/bold cyan]"))

    host = console.input("Digite o IP do alvo (ex: 192.168.0.10): ").strip()

    try:
        porta = int(console.input(
            "Digite a Porta TCP (ex: 1433 para SQL): ").strip())
        if not (1 <= porta <= 65535):
            raise ValueError
    except ValueError:
        console.print("[red]ERRO: Porta inválida.[/red]")
        return

    console.print(
        f"\n[yellow]Testando conexão com {host} na porta {porta}...[/yellow]")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)

    try:
        s.connect((host, porta))
        console.print(
            f"\n[bold green]SUCESSO![/bold green] A porta {porta} está ABERTA em {host}.")
    except socket.timeout:
        console.print(
            f"\n[bold red]FALHA (Timeout).[/bold red] (Porta bloqueada ou host offline)")
    except socket.error as e:
        console.print(
            f"\n[bold red]FALHA (Erro).[/bold red] A conexão foi recusada.")
    finally:
        s.close()
# --- Fim da gaveta 7 ---#

# --- Gaveta 8 (Verifica o espaço em disco local ou remoto) ---#


def verificar_espaco_disco(caminho):
    r"""Verifica o espaço em disco de um caminho (ex: 'C:' ou '\\Servidor\Backup')"""
    console.print(
        f"\n[bold yellow]Verificando espaço em disco de '{caminho}'...[/bold yellow]")
    try:
        uso = psutil.disk_usage(caminho)
        total_gb = uso.total / (1024**3)
        usado_gb = uso.used / (1024**3)
        livre_gb = uso.free / (1024**3)
        percentual_uso = uso.percent

        console.print(f"\nCaminho: [bold cyan]{caminho}[/bold cyan]")
        console.print(
            f"Total: {total_gb:.2f} GB | Usado: {usado_gb:.2f} GB | Livre: {livre_gb:.2f} GB")

        if percentual_uso > 85:
            console.print(
                f"Percentual de Uso: [bold red]{percentual_uso}% (ALERTA!)[/bold red]")
        else:
            console.print(
                f"Percentual de Uso: [bold green]{percentual_uso}%[/bold green]")
    except FileNotFoundError:
        console.print(
            f"\n[bold red]ERRO![/bold red] Caminho não encontrado: '{caminho}'")
    except Exception as e:
        console.print(f"\n[bold red]ERRO INESPERADO![/bold red] {e}")
# --- Fim da gaveta 8 ---#


# --- Gaveta 9 (Limpa pastas Temp do Windows e do Usuário) ---#
def limpar_temporarios(caminho_base):
    """Apaga os arquivos temporários de um caminho base (local ou remoto)."""
    console.print(
        f"\n[bold yellow]Iniciando limpeza em '{caminho_base}'...[/bold yellow]")

    usuario = ""
    if caminho_base.startswith(r'\\'):
        usuario = console.input(
            "Qual o nome da pasta de usuário nessa máquina? (ex: Beatriz): ").strip()
        if not usuario:
            console.print(
                "[red]Nome de usuário é necessário. Pulando pasta de usuário...[/red]")
            caminhos_temp = [os.path.join(caminho_base, 'Windows', 'Temp')]
        else:
            caminhos_temp = [
                os.path.join(caminho_base, 'Windows', 'Temp'),
                os.path.join(caminho_base, 'Users', usuario,
                             'AppData', 'Local', 'Temp')
            ]
    else:
        usuario = os.getlogin()
        caminhos_temp = [
            r'C:\Windows\Temp',
            rf'C:\Users\{usuario}\AppData\Local\Temp'
        ]
    total_arquivos_apagados = 0
    for pasta in caminhos_temp:
        console.print(f"\nVerificando pasta: [cyan]{pasta}[/cyan]")
        if not os.path.exists(pasta):
            console.print(f"[dim]Caminho não existe. Pulando...[/dim]")
            continue
        arquivos_apagados = 0
        for nome_item in os.listdir(pasta):
            caminho_completo = os.path.join(pasta, nome_item)
            try:
                if os.path.isfile(caminho_completo):
                    os.remove(caminho_completo)
                    arquivos_apagados += 1
                elif os.path.isdir(caminho_completo):
                    shutil.rmtree(caminho_completo)
                    arquivos_apagados += 1
            except PermissionError:
                console.print(
                    f"[dim] - Não foi possível apagar '{nome_item}' (em uso).[/dim]")
            except Exception:
                pass
        if arquivos_apagados > 0:
            console.print(
                f"[green]>>> {arquivos_apagados} itens removidos de '{pasta}'.[/green]")
        else:
            console.print(
                f"[yellow]Nenhum item removido (ou pasta já estava limpa).[/yellow]")
        total_arquivos_apagados += arquivos_apagados
    console.print(
        f"\n[bold green]LIMPEZA CONCLUÍDA![/bold green] Total de {total_arquivos_apagados} itens removidos.")
# --- Fim da gaveta 9 ---#


# --- Gaveta 10 (Mostra IP local, Gateway, CPU e RAM) ---#
def verificar_sistema_local():
    """Mostra IP, Gateway, CPU e RAM da máquina local."""
    console.print(
        "\n[bold yellow]Verificando Status do Sistema Local...[/bold yellow]")
    try:
        c = wmi.WMI()
        query = "SELECT * FROM Win32_IP4RouteTable WHERE Destination = '0.0.0.0' AND Mask = '0.0.0.0'"
        gateways = c.query(query)
        gateway_ip = gateways[0].NextHop if gateways else None
        if gateway_ip:
            console.print(
                f"\n[bold green]Gateway Padrão (Roteador):[/bold green] {gateway_ip}")
        else:
            console.print(
                "\n[bold red]Gateway Padrão NÃO ENCONTRADO.[/bold red]")
        console.print("---")
        interfaces = psutil.net_if_addrs()
        encontrou_ip = False
        for nome_iface, addrs in interfaces.items():
            if "Loopback" in nome_iface or "VMware" in nome_iface or "VirtualBox" in nome_iface:
                continue
            ipv4_addrs = [addr for addr in addrs if addr.family == 2]
            if ipv4_addrs:
                encontrou_ip = True
                console.print(
                    f"Interface: [bold cyan]{nome_iface}[/bold cyan]")
                for addr in ipv4_addrs:
                    console.print(
                        f"  [green]IPv4:[/green] {addr.address} (Máscara: {addr.netmask})")
        if not encontrou_ip:
            console.print(
                "\n[red]Nenhum adaptador de rede IPv4 ativo encontrado.[/red]")
    except Exception as e:
        console.print(f"\n[bold red]ERRO AO LER REDE:[/bold red] {e}")
    try:
        console.print(Rule(style="dim"))
        console.print("[bold yellow]Verificando CPU e RAM...[/bold yellow]")
        psutil.cpu_percent(interval=None)
        time.sleep(0.1)
        cpu_uso = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        ram_total_gb = ram.total / (1024**3)
        ram_usada_gb = ram.used / (1024**3)
        ram_percent = ram.percent
        if cpu_uso > 85:
            console.print(
                f"Uso da CPU: [bold red]{cpu_uso}% (ALERTA!)[/bold red]")
        else:
            console.print(f"Uso da CPU: [bold green]{cpu_uso}%[/bold green]")
        console.print(
            f"Uso de RAM: [bold cyan]{ram_usada_gb:.2f} GB[/bold cyan] / {ram_total_gb:.2f} GB ({ram_percent}%)")
        if ram_percent > 85:
            console.print("[bold red](ALERTA: Memória RAM alta!)[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]ERRO AO LER CPU/RAM:[/bold red] {e}")
# --- Fim da gaveta 10 ---#


# --- Gaveta 11 (Limpa o cache de DNS do Windows) ---#
def limpar_cache_dns():
    """Roda 'ipconfig /flushdns' no Windows."""
    console.print("\n[bold yellow]Limpando o cache DNS...[/bold yellow]")
    if os.name == 'nt':
        resultado = os.system("ipconfig /flushdns")
        if resultado == 0:
            console.print(
                "\n[bold green]SUCESSO![/bold green] O cache DNS foi limpo.")
        else:
            console.print(
                "\n[bold red]FALHA![/bold red] Não foi possível limpar o cache.")
    else:
        console.print(
            "\n[bold red]ERRO:[/bold red] Este comando só funciona no Windows.")


# --- Fim da gaveta 11 ---#


# --- Gaveta 12 (Libera e renova o IP local) ---#
def renovar_ip():
    """Roda 'ipconfig /release' e '/renew' no Windows."""
    if os.name == 'nt':
        console.print(
            "\n[bold yellow]Liberando o IP (release)...[/bold yellow]")
        os.system("ipconfig /release")
        console.print("\n[bold yellow]Renovando o IP (renew)...[/bold yellow]")
        os.system("ipconfig /renew")
        console.print(
            "\n[bold green]SUCESSO![/bold green] Processo de renovação de IP concluído.")
    else:
        console.print(
            "\n[bold red]ERRO:[/bold red] Este comando só funciona no Windows.")
# --- Fim da gaveta 12 ---#


# --- Gaveta 13 (Limpa a fila de impressão do Windows) ---#
def limpar_fila_impressao():
    console.print(
        "\n[bold yellow]Tentando limpar a fila de impressão (pasta PRINTERS)...[/bold yellow]")
    caminho_spool = r'C:\Windows\System32\spool\PRINTERS'
    if not os.path.exists(caminho_spool):
        console.print(
            f"[red]ERRO: Caminho '{caminho_spool}' não encontrado.[/red]")
        return
    try:
        arquivos_na_fila = os.listdir(caminho_spool)
        if not arquivos_na_fila:
            console.print(
                "[green]A fila de impressão já está limpa (pasta vazia).[/green]")
            return
        apagados = 0
        for arquivo in arquivos_na_fila:
            caminho_arquivo = os.path.join(caminho_spool, arquivo)
            try:
                os.remove(caminho_arquivo)
                apagados += 1
            except Exception:
                console.print(
                    f"[dim] - Não foi possível apagar '{arquivo}' (em uso/permissão).[/dim]")
        if apagados > 0:
            console.print(
                f"\n[bold green]SUCESSO![/bold green] {apagados} trabalhos removidos da fila.")
        else:
            console.print(
                "\n[yellow]Não foi possível apagar nenhum arquivo (podem estar em uso).[/yellow]")
    except PermissionError:
        console.print("\n[bold red]ERRO: Acesso Negado![/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]ERRO INESPERADO:[/bold red] {e}")
# --- Fim da gaveta 13 ---#

# --- Gaveta 14 (Sub-menu para gerenciar o Spooler de Impressão) ---#


def gerenciar_spooler():
    """Mostra um sub-menu para Iniciar, Parar, Reiniciar ou Habilitar o Spooler."""

    if os.name != 'nt':
        console.print(
            "\n[bold red]ERRO:[/bold red] Esta função está disponível apenas no Windows.")
        return
    while True:
        os.system('cls')
        console.print(
            Rule("[bold cyan]Gerenciador de Spooler de Impressão[/bold cyan]"))
        status = ""
        startup_type = ""
        try:
            service = psutil.win_service_get('spooler')
            status = service.status()
            startup_type = service.start_type()
        except psutil.NoSuchProcess:
            console.print(
                "\n[bold red]ERRO:[/bold red] Serviço 'spooler' não encontrado neste PC.")
            return
        console.print("\nStatus Atual: ", end="")
        if status == 'running':
            console.print(
                f"[bold green]Rodando[/bold green] (Inicialização: {startup_type})")
        elif startup_type == 'disabled':
            console.print(f"[bold red]DESATIVADO[/bold red]")
        else:
            console.print(
                f"[bold yellow]Parado[/bold yellow] (Inicialização: {startup_type})")
        console.print("\n[1] Iniciar Serviço")
        console.print("[2] Parar Serviço (Manutenção)")
        console.print("[3] Reiniciar Serviço (Limpar fila)")
        console.print("[4] Habilitar (Definir como Automático)")
        console.print("[5] Desativar (Proibir inicialização)")
        console.print("[6] Voltar ao Menu Principal")
        sub_opcao = console.input("\nEscolha uma opção: ").strip()
        if sub_opcao == '1':
            if status == 'running':
                console.print("\n[yellow]O serviço já está rodando.[/yellow]")
            elif startup_type == 'disabled':
                console.print(
                    "\n[bold red]ERRO:[/bold red] O serviço está Desativado. Use a Opção 4 para Habilitar primeiro.")
            else:
                console.print(
                    "\n[yellow]Iniciando spooler... (net start spooler)[/yellow]")
                os.system("net start spooler")
        elif sub_opcao == '2':
            if status == 'stopped':
                console.print("\n[yellow]O serviço já está parado.[/yellow]")
            else:
                console.print(
                    "\n[yellow]Parando spooler... (net stop spooler)[/yellow]")
                os.system("net stop spooler")
        elif sub_opcao == '3':
            if startup_type == 'disabled':
                console.print(
                    "\n[bold red]ERRO:[/bold red] O serviço está Desativado. Use a Opção 4 para Habilitar primeiro.")
            else:
                console.print("\n[yellow]Reiniciando spooler...[/yellow]")
                os.system("net stop spooler")
                time.sleep(1)
                limpar = console.input(
                    "Deseja também limpar a fila de trabalhos presos? (S/N): ").upper().strip()
                if limpar == 'S' or limpar == 'SIM':
                    limpar_fila_impressao()
                console.print("Aguardando 2 segundos...")
                time.sleep(2)
                os.system("net start spooler")
                console.print("[bold green]Serviço reiniciado![/bold green]")
        elif sub_opcao == '4':
            console.print(
                "\n[yellow]Habilitando o serviço (start= auto)...[/yellow]")
            os.system("sc config spooler start= auto")
            console.print(
                "[bold green]Serviço definido como Automático![/bold green]")
        elif sub_opcao == '5':
            console.print(
                "\n[yellow]Desativando o serviço (start= disabled)...[/yellow]")
            if status == 'running':
                console.print(
                    "[dim] - Serviço está rodando. Parando ele primeiro (net stop spooler)...[/dim]")
                os.system("net stop spooler")
                time.sleep(1)
            os.system("sc config spooler start= disabled")
            console.print(
                "[bold red]Serviço Desativado com sucesso![/bold red]")
        elif sub_opcao == '6':
            break
        else:
            console.print("\n[red]Opção inválida.[/red]")
        if sub_opcao in ['1', '2', '3', '4', '5']:
            time.sleep(3)
# --- Fim da gaveta 14 ---#

# --- Gaveta 15 (Mostra conexões TCP ativas - rápido) ---#


def ver_conexoes_rede():
    """Mostra as conexões de rede ativas (como 'netstat')"""
    console.print(
        Rule("[bold cyan]Conexões de Rede Ativas (netstat)[/bold cyan]"))
    try:
        conexoes = psutil.net_connections(
            kind='tcp')
        tabela = Table(title="Conexões TCP Ativas", border_style="dim")
        tabela.add_column("Endereço Local", style="cyan")
        tabela.add_column("Porta Local", style="yellow")
        tabela.add_column("Endereço Remoto", style="magenta")
        tabela.add_column("Porta Remota", style="yellow")
        tabela.add_column("Status", style="green")
        if not conexoes:
            console.print("[dim]Nenhuma conexão TCP ativa encontrada.[/dim]")
            return
        for conn in conexoes:
            ip_local, porta_local = conn.laddr if conn.laddr else ("*", "*")
            ip_remoto, porta_remota = conn.raddr if conn.raddr else ("*", "*")
            tabela.add_row(
                str(ip_local),
                str(porta_local),
                str(ip_remoto),
                str(porta_remota),
                str(conn.status)
            )
        console.print(tabela)
    except psutil.AccessDenied:
        console.print("\n[bold red]ERRO: Acesso Negado![/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]ERRO INESPERADO:[/bold red] {e}")
# --- Fim da gaveta 15 ---#

# --- Gaveta 16 (Mostra conexões TCP ativas - lento, com nomes) ---#


def ver_conexoes_com_nomes():
    """Mostra conexões ativas, tentando resolver o IP para nome."""
    console.print(
        Rule("[bold cyan]Conexões de Rede Ativas (com Resolução de Nomes)[/bold cyan]"))
    console.print(
        "[bold yellow]Atenção: Este comando pode ser lento...[/bold yellow]")

    try:
        conexoes = psutil.net_connections(kind='tcp')

        tabela = Table(title="Conexões TCP Ativas (com Nomes)",
                       border_style="dim")
        tabela.add_column("Endereço Local", style="cyan")
        tabela.add_column("Endereço Remoto", style="magenta")
        tabela.add_column("Porta Remota", style="yellow")
        tabela.add_column("Status", style="green")

        if not conexoes:
            console.print("[dim]Nenhuma conexão TCP ativa encontrada.[/dim]")
            return

        for conn in conexoes:
            ip_local, porta_local = conn.laddr if conn.laddr else ("*", "*")
            ip_remoto, porta_remota = conn.raddr if conn.raddr else ("*", "*")

            nome_remoto_final = str(ip_remoto)

            if ip_remoto not in ("*", "127.0.0.1", ""):
                try:
                    nome_host = socket.gethostbyaddr(ip_remoto)[0]
                    nome_remoto_final = f"{nome_host} ({ip_remoto})"
                except (socket.gaierror, socket.timeout, OSError):
                    pass

            tabela.add_row(
                f"{ip_local}:{porta_local}",
                nome_remoto_final,
                str(porta_remota),
                str(conn.status)
            )

        console.print(tabela)

    except psutil.AccessDenied:
        console.print("\n[bold red]ERRO: Acesso Negado![/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]ERRO INESPERADO:[/bold red] {e}")
# --- Fim da gaveta 16 ---#

# --- Gaveta 17 (Mostra Top 5 processos por CPU ou RAM) ---#


def verificar_processos_top():
    """Lista os 5 processos que mais consomem CPU ou RAM localmente."""

    while True:
        console.print(
            Rule("[bold yellow]Opções de Monitoramento de Processos[/bold yellow]"))
        console.print("[1] Ordenar por CPU (Processador)")
        console.print("[2] Ordenar por RAM (Memória)")
        console.print("[bold red][3] Matar Processo (Kill)[/bold red]")
        console.print("[4] Voltar ao Menu Principal")

        sub_opcao = console.input("\nEscolha a ordem: ").strip()

        ordenar_por = None
        if sub_opcao == '1':
            ordenar_por = 'cpu'
        elif sub_opcao == '2':
            ordenar_por = 'ram'
        elif sub_opcao == '3':
            _matar_processo()  # Chama a sub-função
            time.sleep(2)
            continue
        elif sub_opcao == '4':
            return
        else:
            console.print("[red]Opção inválida![/red]")
            time.sleep(1)
            continue

        if ordenar_por:
            console.print(
                Rule(f"[bold cyan]Top 5 Processos por Uso de {ordenar_por.upper()}[/bold cyan]"))
            try:
                psutil.cpu_percent(interval=None)
                time.sleep(0.1)
                processos = []
                for p in psutil.process_iter(['name', 'cpu_percent', 'memory_info', 'pid']):
                    try:
                        processos.append({
                            'name': p.name(),
                            'pid': p.pid,
                            'cpu': p.cpu_percent(interval=None),
                            'rss_mb': p.memory_info().rss / (1024 * 1024)
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                if ordenar_por == 'cpu':
                    processos.sort(key=lambda x: x['cpu'], reverse=True)
                    titulo_tabela = "Processos Mais Ativos (Ordenado por CPU)"
                else:
                    processos.sort(key=lambda x: x['rss_mb'], reverse=True)
                    titulo_tabela = "Processos Mais Ativos (Ordenado por RAM)"

                tabela = Table(title=titulo_tabela, border_style="dim")
                tabela.add_column("PID", style="blue", justify="right")
                tabela.add_column("CPU %", style="red", justify="right")
                tabela.add_column("RAM (MB)", style="magenta", justify="right")
                tabela.add_column("Nome do Processo", style="cyan")

                for p in processos[:5]:
                    cpu_style = "bold red" if p['cpu'] > 50 else "yellow"
                    tabela.add_row(
                        f"{p['pid']}",
                        f"{p['cpu']:.1f}",
                        f"{p['rss_mb']:.0f}",
                        p['name'],
                        style=cpu_style
                    )
                console.print(tabela)
            except Exception as e:
                console.print(
                    f"\n[bold red]ERRO INESPERADO AO LER PROCESSOS:[/bold red] {e}")

            console.input(
                "\n[dim]Pressione Enter para voltar ao menu de monitoramento...[/dim]")

    # --- Sub-Gaveta (Matar Processo) ---


def _matar_processo():
    r"""Função interna para forçar a finalização de um processo."""
    console.print(
        Rule("[bold red]Forçar Finalização de Processo (Kill)[/bold red]"))
    pid_ou_nome = console.input(
        "Digite o NOME (ex: chrome.exe) ou o PID (ex: 1234) do processo: ").strip()

    if not pid_ou_nome:
        console.print("[yellow]Operação cancelada.[/yellow]")
        return

    try:
        pid = int(pid_ou_nome)
        processo = psutil.Process(pid)
        nome_processo = processo.name()
        processo.kill()
        console.print(
            f"\n[bold green]SUCESSO![/bold green] Processo '{nome_processo}' (PID: {pid}) foi encerrado.")

    except ValueError:
        nome_alvo = pid_ou_nome.lower()
        processos_encerrados = 0
        for p in psutil.process_iter(['name', 'pid']):
            if p.name().lower() == nome_alvo:
                try:
                    processo_para_matar = psutil.Process(p.pid)
                    processo_para_matar.kill()
                    console.print(
                        f"Encerrando: [cyan]{p.name()} (PID: {p.pid})[/cyan]...")
                    processos_encerrados += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    console.print(
                        f"[red]Falha ao encerrar {p.name()} (PID: {p.pid}). Acesso negado?[/red]")

        if processos_encerrados > 0:
            console.print(
                f"\n[bold green]SUCESSO![/bold green] {processos_encerrados} processo(s) com nome '{nome_alvo}' foram encerrados.")
        else:
            console.print(
                f"[bold red]ERRO:[/bold red] Nenhum processo encontrado com o nome '{nome_alvo}'.")

    except psutil.NoSuchProcess:
        console.print(
            f"[bold red]ERRO:[/bold red] Processo com PID {pid} não encontrado.")
    except psutil.AccessDenied:
        console.print("\n[bold red]ERRO: Acesso Negado![/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]ERRO INESPERADO:[/bold red] {e}")
# --- Fim da gaveta 17 ---#


# ==============================================================================
# --- INÍCIO DO PROGRAMA ---
carregar_mapa_rede()  # Carrega o JSON para a memória

# --- Loop Principal  ---
while True:
    opcao = desenhar_menu()

    if opcao == '0':
        checkup_geral()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '1':
        if 'servidor' in DISPOSITIVOS:
            dispositivo = DISPOSITIVOS['servidor']
            pingar_servidor(dispositivo['ip'], dispositivo['nome'])
        else:
            console.print(
                "\n[bold red]ERRO: 'servidor' não cadastrado no mapa de rede.[/bold red]")
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '2':
        pingar_dispositivo_por_tipo(
            prefixo_chave="imp", tipo_nome="Impressora")
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '3':
        pingar_dispositivo_por_tipo(prefixo_chave="pdv", tipo_nome="PDV")
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '4':
        verificar_sistema_local()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '5':
        testar_porta()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '6':
        verificar_processos_top()

    elif opcao == '7':
        caminho = console.input(
            "\nDigite o caminho a verificar (ex: C: ou \\\\Servidor\\C$): ").strip()
        verificar_espaco_disco(caminho if caminho else 'C:')
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '8':
        caminho_base = console.input(
            "\nDigite o caminho base para limpeza (ex: C: ou \\\\Beatriz\\C$): ").strip()
        if not caminho_base:
            caminho_base = 'C:'
        limpar_temporarios(caminho_base)
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '9':
        limpar_cache_dns()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '10':
        renovar_ip()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '11':
        gerenciar_spooler()

    elif opcao == '12':
        ver_conexoes_rede()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '13':
        ver_conexoes_com_nomes()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '14':
        gerenciar_mapa()

    elif opcao == '15':

        print("\nObrigado por usar o Painel de TI!")
        break

    else:
        console.print("\n[red]Opção inválida![/red]")
        console.input("Pressione Enter para voltar...")

print("\nPrograma finalizado!")
