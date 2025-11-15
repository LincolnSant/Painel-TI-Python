from rich.console import Console
from rich.panel import Panel
import os
from rich.rule import Rule
from rich.columns import Columns
from rich.text import Text
import psutil
import shutil
import time

console = Console()


def desenhar_menu():
    os.system('cls' if os.name == 'nt' else 'clear')

    console.print(
        Rule("[bold cyan]SysAdmin Helper 1.0[/bold cyan]", style="cyan"))
    console.print(
        Rule("[bold white]Painel Rápido - Auxiliar de TI (Atacado/Varejo)[/bold white]"))

    # --- CONTEÚDO DA COLUNA 1 ---
    menu_verificacao = (
        "[dim]--- Verificação Rápida ---\n"
        "[yellow]1)[/yellow] Pingar Servidor Principal (ERP)\n"
        "[yellow]2)[/yellow] Pingar Impressora Fiscal (Rede)\n"
        "[yellow]3)[/yellow] Pingar PDV 01 (Caixa)\n"
        "[yellow]4)[/yellow] Ver Meu IP Local"  # <--- NOVO
    )

    # --- CONTEÚDO DA COLUNA 2 ---
    menu_manutencao = (
        "[dim]--- Manutenção ---\n"
        "[yellow]5)[/yellow] Verificar Espaço em Disco (Servidor)\n"
        "[yellow]6)[/yellow] Limpar Arquivos Temporários (Local)\n"
        "[yellow]7)[/yellow] Limpar Cache DNS (flushdns)\n"
        "[yellow]8)[/yellow] Renovar IP (release/renew)\n"
        "[yellow]9)[/yellow] Gerenciar Spooler de Impressão\n\n"  # <--- NOVO
        "[yellow]10)[/yellow] Sair"
    )

    # --- DESENHA AS COLUNAS ---
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

# --- Gaveta 3: Verificar Espaço em Disco ---


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
# --- Fim da Gaveta 3 ---


# --- Gaveta 4: Limpar Arquivos Temporários ---
def limpar_temporarios():
    """Apaga os arquivos das pastas temporárias do Windows."""
    console.print(
        "\n[bold yellow]Iniciando limpeza de arquivos temporários...[/bold yellow]")

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

        # --- CORREÇÃO 2: Linhas de título coladas aqui foram REMOVIDAS ---

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
# --- Fim da Gaveta 4 ---


# --- Gaveta 5: Ver IP Local ---
def ver_meu_ip():
    """Mostra os endereços IPv4 locais usando psutil."""
    console.print(
        "\n[bold yellow]Verificando Endereços IP Locais...[/bold yellow]")

    try:
        # Pega todas as interfaces de rede
        interfaces = psutil.net_if_addrs()
        encontrou = False

        for nome_iface, addrs in interfaces.items():
            # Pula interfaces de "mentira" (Loopback e virtuais)
            if "Loopback" in nome_iface or "VMware" in nome_iface or "VirtualBox" in nome_iface:
                continue

            # Procura pelos endereços IPv4 (cujo 'family' é 2)
            ipv4_addrs = [addr for addr in addrs if addr.family == 2]

            if ipv4_addrs:
                encontrou = True
                console.print(
                    f"\nInterface: [bold cyan]{nome_iface}[/bold cyan]")
                for addr in ipv4_addrs:
                    console.print(
                        f"  [green]IPv4:[/green] {addr.address} (Máscara: {addr.netmask})")

        if not encontrou:
            console.print(
                "\n[red]Nenhum adaptador de rede IPv4 ativo encontrado.[/red]")

    except Exception as e:
        console.print(f"\n[bold red]ERRO AO LER IPS:[/bold red] {e}")

# --- Fim da gaveta 5 ---


# --- Gaveta 6: Limpar DNS ---
def limpar_cache_dns():
    """Roda 'ipconfig /flushdns' no Windows."""
    console.print("\n[bold yellow]Limpando o cache DNS...[/bold yellow]")

    if os.name == 'nt':  # 'nt' é o Windows
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
# --- Fim da gaveta 6 ---


# --- Gaveta 7: Renovar IP ---
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

# --- Fim da gaveta 7 ---


# --- Gaveta 8: Gerenciar Spooler de Impressão ---
def gerenciar_spooler():
    """Mostra um sub-menu para Iniciar, Parar, Reiniciar ou Habilitar o Spooler."""
    
    if os.name != 'nt':
        console.print("\n[bold red]ERRO:[/bold red] Esta função está disponível apenas no Windows.")
        return

    while True:
        os.system('cls')
        console.print(Rule("[bold cyan]Gerenciador de Spooler de Impressão[/bold cyan]"))
        
        status = ""
        startup_type = ""
        try:
            # Pega o serviço 'spooler'
            service = psutil.win_service_get('spooler')
            status = service.status() # 'running', 'stopped'
            # --- NOVO: Lendo o Tipo de Inicialização ---
            startup_type = service.start_type() # 'automatic', 'manual', 'disabled'
            
        except psutil.NoSuchProcess:
            console.print("\n[bold red]ERRO:[/bold red] Serviço 'spooler' não encontrado neste PC.")
            return

        # --- NOVO: Status Inteligente ---
        console.print("\nStatus Atual: ", end="")
        if status == 'running':
            console.print(f"[bold green]Rodando[/bold green] (Inicialização: {startup_type})")
        elif startup_type == 'disabled':
            console.print(f"[bold red]DESATIVADO[/bold red]") # <<< Agora ele sabe!
        else:
            console.print(f"[bold yellow]Parado[/bold yellow] (Inicialização: {startup_type})")
            
        # --- NOVO: Menu com mais opções ---
        console.print("\n[1] Iniciar Serviço")
        console.print("[2] Parar Serviço")
        console.print("[3] Reiniciar Serviço")
        console.print("[4] Habilitar (Definir como Automático)")
        console.print("[5] Desativar (Proibir inicialização)")
        console.print("[6] Voltar ao Menu Principal")
        
        sub_opcao = console.input("\nEscolha uma opção: ").strip()

        if sub_opcao == '1':
            if status == 'running':
                console.print("\n[yellow]O serviço já está rodando.[/yellow]")
            elif startup_type == 'disabled':
                console.print("\n[bold red]ERRO:[/bold red] O serviço está Desativado. Use a Opção 4 para Habilitar primeiro.")
            else:
                console.print("\n[yellow]Iniciando spooler... (net start spooler)[/yellow]")
                os.system("net start spooler")
        
        elif sub_opcao == '2':
            if status == 'stopped':
                console.print("\n[yellow]O serviço já está parado.[/yellow]")
            else:
                console.print("\n[yellow]Parando spooler... (net stop spooler)[/yellow]")
                os.system("net stop spooler")
        
        elif sub_opcao == '3':
            if startup_type == 'disabled':
                console.print("\n[bold red]ERRO:[/bold red] O serviço está Desativado. Use a Opção 4 para Habilitar primeiro.")
            else:
                console.print("\n[yellow]Reiniciando spooler...[/yellow]")
                os.system("net stop spooler")
                console.print("Aguardando 2 segundos...")
                time.sleep(2)
                os.system("net start spooler")
                console.print("[bold green]Serviço reiniciado![/bold green]")
        
        # --- NOVO: Lógica para Habilitar/Desabilitar ---
        elif sub_opcao == '4':
            console.print("\n[yellow]Habilitando o serviço (start= auto)...[/yellow]")
            # 'sc config' é o comando para alterar a configuração de um serviço
            os.system("sc config spooler start= auto")
            console.print("[bold green]Serviço definido como Automático![/bold green] (Tente iniciá-lo agora)")

        elif sub_opcao == '5':
            console.print("\n[yellow]Desativando o serviço (start= disabled)...[/yellow]")
            os.system("sc config spooler start= disabled")
            console.print("[bold red]Serviço Desativado.[/bold red]")

        elif sub_opcao == '6':
            break # Sai do sub-menu
        
        else:
            console.print("\n[red]Opção inválida.[/red]")
        
        # Pausa para o usuário ler o resultado
        if sub_opcao in ['1', '2', '3', '4', '5']:
            time.sleep(3) # Aumentei para 3s
# --- Fim da Gaveta 8 Atualizada ---


# --- Loop Principal ---
while True:
    opcao = desenhar_menu()

    if opcao == '1':
        pingar_servidor('8.8.8.8', 'Servidor Principal (ERP)')
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '2':
        pingar_servidor('192.168.0.100', 'Impressora Fiscal')  # Trocar o IP
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '3':
        pingar_servidor('192.168.0.101', 'PDV 01 (Caixa)')  # Trocar o IP
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '4':
        ver_meu_ip()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '5':
        verificar_espaco_disco('C:')
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
