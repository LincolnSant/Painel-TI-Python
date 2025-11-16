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

console = Console()

# --- MAPA DE REDE (A "agenda" de IPs) ---
DISPOSITIVOS = {
    "servidor": {"ip": "8.8.8.8", "nome": "Servidor Principal (ERP)"},
    "imp_fiscal1": {"ip": "192.168.0.100", "nome": "Impressora Fiscal 1 (Frente Loja)"},
    "imp_padaria": {"ip": "192.168.0.105", "nome": "Impressora 2 (Padaria)"},
    "pdv1": {"ip": "192.168.0.101", "nome": "PDV 01 (Caixa)"},
    "pdv2": {"ip": "192.168.0.102", "nome": "PDV 02 (Caixa)"},
    "pdv_padaria": {"ip": "192.168.0.120", "nome": "PDV (Padaria)"},
}
# ----------------------------------------

# --- GAVETA DO MENU (ATUALIZADA) ---
def desenhar_menu():
    os.system('cls' if os.name == 'nt' else 'clear') 
    
    console.print(Rule("[bold cyan]SysAdmin Helper 2.1[/bold cyan]", style="cyan"))
    console.print(Rule("[bold white]Painel Rápido - Auxiliar de TI (Atacado/Varejo)[/bold white]"))

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
        "[yellow]7)[/yellow] Limpar Arquivos Temporários\n"
        "[yellow]8)[/yellow] Limpar Cache DNS (flushdns)\n"
        "[yellow]9)[/yellow] Renovar IP (release/renew)\n"
        "[yellow]10)[/yellow] Gerenciar Spooler de Impressão\n"
        "[yellow]11)[/yellow] Ver Conexões Ativas (Rápido)\n" 
        "[yellow]12)[/yellow] Ver Conexões (com Nomes) (Lento)\n\n"
        "[yellow]13)[/yellow] Sair" 
    )

    console.print(Columns([
        Panel(menu_verificacao, title="VERIFICAR", border_style="green", padding=1),
        Panel(menu_manutencao, title="MANUTENÇÃO", border_style="red", padding=1)
    ], expand=True, equal=True)) 

    return console.input("\n[bold]Escolha uma opção: [/bold]")
# --- Fim do Menu ---

# --- GAVETA 0: Check-up Geral ---
def checkup_geral():
    """Roda um ping em TODOS os dispositivos cadastrados no MAPA DE REDE."""
    console.print(Rule("[bold cyan]Iniciando Check-up Geral da Loja[/bold cyan]"))
    
    tabela_status = Table(title="Status da Rede", border_style="dim")
    tabela_status.add_column("Dispositivo", style="cyan", width=30)
    tabela_status.add_column("IP", style="magenta", width=15)
    tabela_status.add_column("Status", style="white")

    falhas = 0
    
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
        console.print(f"\n[bold red]ATENÇÃO:[/bold red] {falhas} dispositivo(s) estão offline!")
    else:
        console.print(f"\n[bold green]Tudo Certo![/bold green] Todos os dispositivos críticos estão online.")
# --- Fim da Gaveta 0 ---

# --- Gaveta 1: Pingar Servidor ---
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
# --- Fim da Gaveta 1 ---

# --- GAVETA MESTRA: Pingar por Tipo ---
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
        f"\nDigite a Chave do {tipo_nome} (ex: {list(lista_filtrada.keys())[0]}): ").strip()
    
    if chave_escolhida in lista_filtrada:
        dispositivo = lista_filtrada[chave_escolhida]
        pingar_servidor(dispositivo['ip'], dispositivo['nome'])
    else:
        console.print(
            f"\n[bold red]ERRO: Chave '{chave_escolhida}' não encontrada![/bold red]")
# --- Fim da Gaveta Mestra ---

# --- GAVETA 5: Testar Porta ---
def testar_porta():
    """Tenta conectar a uma porta TCP específica em um host."""
    console.print(
        Rule("[bold cyan]Teste de Conexão de Porta (TCP)[/bold cyan]"))
    
    host = console.input("Digite o IP do alvo (ex: 192.168.0.10): ").strip()
    
    try:
        porta = int(console.input(
            "Digite a Porta TCP (ex: 1433 para SQL, 3389 para RDP): ").strip())
        if not (1 <= porta <= 65535):
            raise ValueError
    except ValueError:
        console.print(
            "[red]ERRO: Porta inválida. Digite um número de 1 a 65535.[/red]")
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
            f"\n[bold red]FALHA (Timeout).[/bold red] O host {host} não respondeu na porta {porta} (provavelmente bloqueada).")
    except socket.error as e:
        console.print(
            f"\n[bold red]FALHA (Erro).[/bold red] A conexão foi recusada.")
        console.print(f"[dim]Erro: {e}[/dim]")
    finally:
        s.close()
# --- Fim da Gaveta 5 ---

# --- Gaveta 6: Verificar Espaço em Disco ---
def verificar_espaco_disco(caminho):
    """Verifica o espaço em disco de um caminho (ex: 'C:' ou '\\Servidor\Backup')"""
    console.print(
        f"\n[bold yellow]Verificando espaço em disco de '{caminho}'...[/bold yellow]")
    try:
        uso = psutil.disk_usage(caminho)
        total_gb = uso.total / (1024**3)
        usado_gb = uso.used / (1024**3)
        livre_gb = uso.free / (1024**3)
        percentual_uso = uso.percent

        console.print(f"\nCaminho: [bold cyan]{caminho}[/bold cyan]")
        console.print(f"Total: {total_gb:.2f} GB")
        console.print(f"Usado: {usado_gb:.2f} GB")
        console.print(f"Livre: {livre_gb:.2f} GB")

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
# --- Fim da Gaveta 6 ---


# --- Gaveta 7: Limpar Arquivos Temporários ---
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
                "[red]Nome de usuário é necessário para limpar a pasta de perfil. Pulando...[/red]")
            caminhos_temp = [
                os.path.join(caminho_base, 'Windows', 'Temp')
            ]
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
            except Exception as e:
                console.print(
                    f"[red] - Erro ao apagar '{nome_item}': {e}[/red]")
        if arquivos_apagados > 0:
            console.print(
                f"[green]>>> {arquivos_apagados} itens removidos de '{pasta}'.[/green]")
        else:
            console.print(
                f"[yellow]Nenhum item removido (ou pasta já estava limpa).[/yellow]")
        total_arquivos_apagados += arquivos_apagados
    console.print(
        f"\n[bold green]LIMPEZA CONCLUÍDA![/bold green] Total de {total_arquivos_apagados} itens removidos.")
# --- Fim da Gaveta 7 ---


# --- Gaveta 4: Ver Status do PC Local ---
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
        cpu_uso = psutil.cpu_percent(interval=1)
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
# --- Fim da Gaveta 4 ---


# --- Gaveta 8: Limpar DNS ---
def limpar_cache_dns():
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
# --- Fim da Gaveta 8 ---


# --- Gaveta 9: Renovar IP ---
def renovar_ip():
    if os.name == 'nt':
        console.print(
            "\n[bold yellow]Liberando o IP (release)...[/bold yellow]")
        os.system("ipconfig /release")
        console.print("\n[bold yellow]Renovando o IP (renew)...[/bold yellow]")
        os.system("ipconfig /renew")
        console.print(
            "\n[bold green]SUCESSO![/bold green] Processo de renovação de IP concluído.")
        console.print("Verifique sua conexão.")
    else:
        console.print(
            "\n[bold red]ERRO:[/bold red] Este comando só funciona no Windows.")
# --- Fim da Gaveta 9 ---


# --- Gaveta 10: Limpar Fila de Impressão ---
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
# --- Fim da Gaveta 10 ---


# --- Gaveta 11: Gerenciar Spooler de Impressão ---
def gerenciar_spooler():
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
# --- Fim da Gaveta 11 ---

# --- Gaveta 12: Ver Conexões Ativas (Netstat) ---
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
        console.print(
            "[dim]É necessário rodar como Administrador para ver todas as conexões.[/dim]")
    except Exception as e:
        console.print(f"\n[bold red]ERRO INESPERADO:[/bold red] {e}")
# --- Fim da Gaveta 12 ---

# --- Gaveta 13: Ver Conexões Ativas com Nomes (Netstat Lento) ---
def ver_conexoes_com_nomes():
    """Mostra conexões ativas, tentando resolver o IP para nome."""
    console.print(
        Rule("[bold cyan]Conexões de Rede Ativas (com Resolução de Nomes)[/bold cyan]"))
    console.print("[bold yellow]Atenção: Este comando pode ser lento...[/bold yellow]")

    try:
        conexoes = psutil.net_connections(kind='tcp')
        
        tabela = Table(title="Conexões TCP Ativas (com Nomes)", border_style="dim")
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
            
            # --- A MÁGICA DA TRADUÇÃO ---
            if ip_remoto not in ("*", "127.0.0.1", ""):
                try:
                    # Tenta "traduzir" o IP.
                    nome_host = socket.gethostbyaddr(ip_remoto)[0]
                    nome_remoto_final = f"{nome_host} ({ip_remoto})"
                # A CORREÇÃO FINAL: Pegar todos os erros de socket/sistema
                except (socket.gaierror, socket.timeout, OSError): 
                    # Se falhar (host não encontrado, timeout), simplesmente pula
                    pass 
            # --- FIM DA MÁGICA ---

            tabela.add_row(
                f"{ip_local}:{porta_local}", # Juntei o local para caber mais
                nome_remoto_final,
                str(porta_remota),
                str(conn.status)
            )
        
        console.print(tabela)

    except psutil.AccessDenied:
        console.print("\n[bold red]ERRO: Acesso Negado![/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]ERRO INESPERADO:[/bold red] {e}")
# --- Fim da Gaveta 13 ---

# --- Gaveta 14: Ver Processos Gulosos ---
def verificar_processos_top(ordenar_por='cpu'):
    console.print(Rule("[bold cyan]Top 5 Processos por Uso de CPU[/bold cyan]"))
    
    try:
        # --- FIX: CRIAR A LINHA DE BASE (DELTA) ---
        # 1. Chamamos uma vez para estabelecer o "Ponto A" (Estado Inicial)
        psutil.cpu_percent(interval=None) 
        
        # 2. Esperamos um instante para que os processos usem a CPU
        time.sleep(0.1) 
        # ------------------------------------------

        processos = []
        # O resto do loop continua igual, mas agora o p.cpu_percent()
        # vai medir a diferença no último 0.1 segundo, dando um valor real.
        for p in psutil.process_iter(['name', 'cpu_percent', 'memory_info']):
            try:
                processos.append({
                    'name': p.name(),
                    'cpu': p.cpu_percent(interval=None), 
                    'rss_mb': p.memory_info().rss / (1024 * 1024) 
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        
        # Ordena a lista pelo uso da CPU (do maior para o menor)
        processos.sort(key=lambda x: x['cpu'], reverse=True)
        
        # Prepara a tabela
        tabela = Table(title="Processos Mais Ativos (Último Segundo)", border_style="dim")
        tabela.add_column("CPU %", style="red", justify="right")
        tabela.add_column("RAM (MB)", style="magenta", justify="right")
        tabela.add_column("Nome do Processo", style="cyan")
        
        # Adiciona os 5 primeiros na tabela
        for p in processos[:5]:
            cpu_style = "bold red" if p['cpu'] > 50 else "yellow"
            tabela.add_row(
                f"{p['cpu']:.1f}", 
                f"{p['rss_mb']:.0f}", 
                p['name'],
                style=cpu_style
            )
        
        console.print(tabela)

    except Exception as e:
        console.print(f"\n[bold red]ERRO INESPERADO AO LER PROCESSOS:[/bold red] {e}")
# --- Fim da Gaveta 14 ---


# --- Loop Principal (ATUALIZADO) ---
while True:
    opcao = desenhar_menu()

    if opcao == '0':
        checkup_geral()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '1':
        dispositivo = DISPOSITIVOS['servidor']
        pingar_servidor(dispositivo['ip'], dispositivo['nome'])
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '2':
        pingar_dispositivo_por_tipo(prefixo_chave="imp", tipo_nome="Impressora")
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

    elif opcao == '6': # <--- NOVO
        verificar_processos_top()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '7': # <--- MUDOU NÚMERO
        caminho = console.input("\nDigite o caminho a verificar (ex: C: ou \\\\Servidor\\C$): ").strip()
        verificar_espaco_disco(caminho if caminho else 'C:')
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '8':
        limpar_cache_dns()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '9':
        renovar_ip()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")
    
    elif opcao == '10':
        gerenciar_spooler()

    elif opcao == '11': 
        ver_conexoes_rede()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '12': 
        ver_conexoes_com_nomes()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '13': 
        break # Sair

    else:
        console.print("\n[red]Opção inválida![/red]")
        console.input("Pressione Enter para voltar...")

print("\nPrograma finalizado!")