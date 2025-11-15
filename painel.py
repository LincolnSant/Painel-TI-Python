from rich.console import Console
from rich.panel import Panel # Vamos usar 'Panel' para fazer as caixas!
import os # Vamos usar para limpar a tela
import psutil
import shutil

console = Console()

def desenhar_menu():
    os.system('cls' if os.name == 'nt' else 'clear') # Limpa a tela
    
    console.print(Panel("[bold cyan]Painel Rápido - Auxiliar de TI (Atacado/Varejo)[/bold cyan]", 
                      title="SysAdmin Helper 1.0", 
                      style="bold white", 
                      border_style="cyan"))

    console.print("--- Verificação Rápida ---", style="dim")
    console.print("[yellow]1)[/yellow] Pingar Servidor Principal (ERP)")
    console.print("[yellow]2)[/yellow] Pingar Impressora Fiscal (Rede)")
    console.print("[yellow]3)[/yellow] Pingar PDV 01 (Caixa)")
    
    console.print("\n--- Manutenção ---", style="dim")
    console.print("[yellow]4)[/yellow] Verificar Espaço em Disco (Servidor)")
    console.print("[yellow]5)[/yellow] Limpar Arquivos Temporários (Local)")
    
    console.print("\n[yellow]6)[/yellow] Sair")
    
    return console.input("\n[bold]Escolha uma opção: [/bold]")


# --- Gaveta 1: Pingar Servidor ---
def pingar_servidor(host, nome_amigavel):
    """Função para pingar um host e mostrar o status."""
    console.print(f"\n[bold yellow]Pingando {nome_amigavel} ({host})...[/bold yellow]")
    
    # Prepara o comando 'ping'
    # -n 2: Envia 2 pacotes (em vez de 4, para ser mais rápido)
    if os.name == 'nt':
        # Comando para Windows
        comando = f"ping -n 2 {host}"
    else:
        # Comando para Linux/macOS
        comando = f"ping -c 2 {host}"
    
    # Executa o comando no terminal e esconde a saída
    resultado = os.system(comando)
    
    # Verifica o código de saída
    if resultado == 0:
        console.print(f"\n[bold green]SUCESSO![/bold green] O {nome_amigavel} ({host}) está respondendo.")
    else:
        console.print(f"\n[bold red]FALHA![/bold red] O {nome_amigavel} ({host}) está INACESSÍVEL.")
# --- Fim da Gaveta 1 ---

# --- Gaveta 3: Verificar Espaço em Disco ---
def verificar_espaco_disco(caminho):
    """Verifica o espaço em disco de um caminho (ex: 'C:' ou '\\Servidor\Backup')"""
    console.print(f"\n[bold yellow]Verificando espaço em disco de '{caminho}'...[/bold yellow]")
    
    try:
        uso = psutil.disk_usage(caminho)
        
        # psutil retorna valores em bytes, vamos converter para Gigabytes (GB)
        total_gb = uso.total / (1024**3)
        usado_gb = uso.used / (1024**3)
        livre_gb = uso.free / (1024**3)
        percentual_uso = uso.percent
        
        # Mostra o resultado formatado
        console.print(f"\nCaminho: [bold cyan]{caminho}[/bold cyan]")
        console.print(f"Total: {total_gb:.2f} GB")
        console.print(f"Usado: {usado_gb:.2f} GB")
        console.print(f"Livre: {livre_gb:.2f} GB")
        
        # Adiciona uma cor de alerta se o uso estiver alto
        if percentual_uso > 85:
            console.print(f"Percentual de Uso: [bold red]{percentual_uso}% (ALERTA!)[/bold red]")
        else:
            console.print(f"Percentual de Uso: [bold green]{percentual_uso}%[/bold green]")
            
    except FileNotFoundError:
        console.print(f"\n[bold red]ERRO![/bold red] Caminho não encontrado: '{caminho}'")
    except Exception as e:
        console.print(f"\n[bold red]ERRO INESPERADO![/bold red] {e}")
# --- Fim da Gaveta 3 ---


# --- Gaveta 4: Limpar Arquivos Temporários ---
def limpar_temporarios():
    """Apaga os arquivos das pastas temporárias do Windows."""
    console.print("\n[bold yellow]Iniciando limpeza de arquivos temporários...[/bold yellow]")
    
    # Pega o nome de usuário do PC atual (ex: 'linco')
    usuario = os.getlogin()
    
    # Define os caminhos das pastas temporárias
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
        # os.listdir() lista tudo (arquivos e subpastas)
        for nome_item in os.listdir(pasta):
            caminho_completo = os.path.join(pasta, nome_item)
            
            try:
                # Se for um arquivo, apaga
                if os.path.isfile(caminho_completo):
                    os.remove(caminho_completo)
                    arquivos_apagados += 1
                # Se for uma pasta, apaga a pasta inteira
                elif os.path.isdir(caminho_completo):
                    shutil.rmtree(caminho_completo)
                    arquivos_apagados += 1
                    
            except PermissionError:
                console.print(f"[dim] - Não foi possível apagar '{nome_item}' (em uso).[/dim]")
            except Exception as e:
                console.print(f"[red] - Erro ao apagar '{nome_item}': {e}[/red]")
        
        console.print(f"[green]>>> {arquivos_apagados} itens removidos de '{pasta}'.[/green]")
        total_arquivos_apagados += arquivos_apagados

    console.print(f"\n[bold green]LIMPEZA CONCLUÍDA![/bold green] Total de {total_arquivos_apagados} itens removidos.")
# --- Fim da Gaveta 4 ---


# --- Loop Principal ---
while True:
    opcao = desenhar_menu()
    
    if opcao == '1':
        # Você pode trocar '192.168.0.1' pelo IP real do seu servidor
        pingar_servidor('8.8.8.8', 'Servidor Principal (ERP)')
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")
    
    elif opcao == '2':
        # Vamos fazer o mesmo para a impressora
        pingar_servidor('192.168.0.100', 'Impressora Fiscal') # Troque pelo IP da impressora
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '3':
        pingar_servidor('192.168.0.101', 'PDV 01 (Caixa)') # Troque pelo IP do PDV
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")

    elif opcao == '4':
        # Você pode checar o C: local ou o caminho do servidor (ex: '\\Servidor\Dados')
        verificar_espaco_disco('C:') 
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")
        
    elif opcao == '5':
        limpar_temporarios()
        console.input("\n[dim]Pressione Enter para voltar...[/dim]")
        
    elif opcao == '6':
        break
        
    else:
        console.print("\n[red]Opção inválida![/red]")
        console.input("Pressione Enter para voltar...")

print("Programa finalizado!")