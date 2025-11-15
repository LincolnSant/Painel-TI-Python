from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.columns import Columns
import os
import psutil
import shutil
import time
import datetime
import wmi

console = Console()

# --- MAPA DE REDE (A "agenda" de IPs) ---
# CORREÇÃO 2: Movido para fora do loop, para o topo.
DISPOSITIVOS = {
    "servidor": {"ip": "8.8.8.8", "nome": "Servidor Principal (ERP)"},
    "impressora_fiscal": {"ip": "192.168.0.100", "nome": "Impressora Fiscal"},
    "pdv1": {"ip": "192.168.0.101", "nome": "PDV 01 (Caixa)"},
    # Adicione mais PDVs aqui!
    # "pdv2": {"ip": "192.168.0.102", "nome": "PDV 02 (Padaria)"},
}
# ----------------------------------------

# --- GAVETA DO MENU (CORRIGIDA) ---


def desenhar_menu():
    os.system('cls' if os.name == 'nt' else 'clear')

    # CORREÇÃO 1: Usando o layout de Rule e Columns
    console.print(
        Rule("[bold cyan]SysAdmin Helper 1.0[/bold cyan]", style="cyan"))
    console.print(
        Rule("[bold white]Painel Rápido - Auxiliar de TI (Atacado/Varejo)[/bold white]"))

    menu_verificacao = (
        "[dim]--- Verificação Rápida ---\n"
        "[yellow]1)[/yellow] Pingar Servidor Principal (ERP)\n"
        "[yellow]2)[/yellow] Pingar Impressora Fiscal (Rede)\n"
        "[yellow]3)[/yellow] Pingar um PDV (Específico)\n"  # Nome atualizado
        "[yellow]4)[/yellow] Ver Meu IP Local"
    )

    menu_manutencao = (
        "[dim]--- Manutenção ---\n"
        "[yellow]5)[/yellow] Verificar Espaço em Disco\n"  # Nome atualizado
        "[yellow]6)[/yellow] Limpar Arquivos Temporários (Local)\n"
        "[yellow]7)[/yellow] Limpar Cache DNS (flushdns)\n"
        "[yellow]8)[/yellow] Renovar IP (release/renew)\n"
        "[yellow]9)[/yellow] Gerenciar Spooler de Impressão\n\n"
        "[yellow]10)[/yellow] Sair"
    )

    console.print(Columns([
        Panel(menu_verificacao, title="VERIFICAR",
              border_style="green", padding=1),
        Panel(menu_manutencao, title="MANUTENÇÃO",
              border_style="red", padding=1)
    ], expand=True, equal=True))

    return console.input("\n[bold]Escolha uma opção: [/bold]")
# --- Fim do Menu ---


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

# --- Gaveta 2: Verificar Espaço em Disco ---


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
# --- Fim da Gaveta 2 ---


# --- Gaveta 3: Limpar Arquivos Temporários ---
def limpar_temporarios():
    """Apaga os arquivos das pastas temporárias do Windows."""
    console.print(
        "\n[bold yellow]Iniciando limpeza de arquivos temporários...[/bold yellow]")

    if os.name != 'nt':
        console.print(
            "\n[bold red]ERRO:[/bold red] Esta função só funciona no Windows.")
        return

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
        console.print(
            f"[green]>>> {arquivos_apagados} itens removidos de '{pasta}'.[/green]")
        total_arquivos_apagados += arquivos_apagados

    console.print(
        f"\n[bold green]LIMPEZA CONCLUÍDA![/bold green] Total de {total_arquivos_apagados} itens removidos.")
# --- Fim da Gaveta 3 ---



# --- Gaveta 4: Ver IP Local (VERSÃO FINAL COM WMI) ---
def ver_meu_ip():
    """Mostra os endereços IPv4 locais e o Gateway Padrão."""
    console.print(
        "\n[bold yellow]Verificando Endereços IP Locais e Gateway...[/bold yellow]")

    try:
        # --- 1. Encontrar o Gateway Padrão (com WMI) ---
        c = wmi.WMI() # Conecta ao Windows Management Instrumentation
        
        # Procura na tabela de roteamento pelo "portão" principal (Destino 0.0.0.0)
        query = "SELECT * FROM Win32_IP4RouteTable WHERE Destination = '0.0.0.0' AND Mask = '0.0.0.0'"
        gateways = c.query(query)
        
        gateway_ip = None
        if gateways:
            gateway_ip = gateways[0].NextHop # Pega o primeiro resultado

        if gateway_ip:
            console.print(f"\n[bold green]Gateway Padrão (Roteador):[/bold green] {gateway_ip}")
        else:
            console.print("\n[bold red]Gateway Padrão NÃO ENCONTRADO.[/bold red]")
        
        console.print("---") # Linha separadora

        # --- 2. Encontrar os IPs Locais (com psutil, isso já funciona) ---
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
        # Se o WMI falhar (ex: rodando sem ser admin), ele vai dar um erro aqui
        console.print(f"\n[bold red]ERRO AO LER REDE:[/bold red] {e}")
        console.print("[dim]Dica: Tente rodar como Administrador para ver o Gateway.[/dim]")
# --- Fim da Gaveta 4 ---


# --- Gaveta 5: Limpar DNS ---
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
# --- Fim da Gaveta 5 ---


# --- Gaveta 6: Renovar IP ---
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
        console.print("Verifique sua conexão.")
    else:
        console.print(
            "\n[bold red]ERRO:[/bold red] Este comando só funciona no Windows.")
# --- Fim da Gaveta 6 ---


# --- Gaveta 7: Limpar Fila de Impressão ---
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
# --- Fim da Gaveta 7 ---


# --- Gaveta 8: Gerenciar Spooler de Impressão ---
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
        console.print("[2] Parar Serviço (Manutenção)")  # Texto atualizado
        # Texto atualizado
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

        # CORREÇÃO 3: Opção 2 NÃO limpa mais a fila
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
                # Pergunta só no Reiniciar
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
# --- Fim da Gaveta 8 ---


# --- Loop Principal ---
while True:
    opcao = desenhar_menu()

    if opcao == '1':
        dispositivo = DISPOSITIVOS['servidor']
        pingar_servidor(dispositivo['ip'], dispositivo['nome'])
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '2':
        dispositivo = DISPOSITIVOS['impressora_fiscal']
        pingar_servidor(dispositivo['ip'], dispositivo['nome'])
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '3':
        num_pdv = console.input(
            "\nQual o número do PDV? (ex: 1, 2...): ").strip()
        chave_pdv = f"pdv{num_pdv}"

        if chave_pdv in DISPOSITIVOS:
            dispositivo = DISPOSITIVOS[chave_pdv]
            pingar_servidor(dispositivo['ip'], dispositivo['nome'])
        else:
            console.print(
                f"\n[bold red]ERRO: PDV '{num_pdv}' não cadastrado![/bold red]")

        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '4':
        ver_meu_ip()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '5':
        caminho = console.input(
            "\nDigite o caminho a verificar (ex: C: ou \\\\Servidor\\C$): ").strip()
        verificar_espaco_disco(caminho if caminho else 'C:')
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '6':
        limpar_temporarios()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '7':
        limpar_cache_dns()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '8':
        renovar_ip()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '9':
        gerenciar_spooler()

    elif opcao == '10':
        break

    else:
        console.print("\n[red]Opção inválida![/red]")
        console.input("Pressione Enter para voltar...")

print("\nPrograma finalizado!")
