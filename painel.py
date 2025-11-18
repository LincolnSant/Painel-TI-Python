import os
import psutil
import shutil
import time
import datetime
import wmi
import socket
import json
import asyncio
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.columns import Columns
from rich.table import Table
from rich.tree import Tree
from rich.text import Text 

#--- Gaveta Auxiliar (Ping Assíncrono) ---#
# (Sem alterações)
async def pingar_host_async(ip, payload_info):
    """
    Função auxiliar que pinga UM host de forma assíncrona.
    Recebe: (ip, payload_info) onde payload_info pode ser qualquer coisa.
    Retorna: (payload_info, ip, status)
    """
    comando_ping = f"ping -n 2 {ip}" if os.name == 'nt' else f"ping -c 2 {ip}"

    processo = await asyncio.create_subprocess_shell(
        f"{comando_ping} > {os.devnull} 2>&1",
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await processo.wait()

    if processo.returncode == 0:
        return (payload_info, ip, "[bold green]ONLINE[/bold green]")
    else:
        return (payload_info, ip, "[bold red]FALHA[/bold red]")
#--- Fim da Gaveta Auxiliar ---#


# ==============================================================================
# --- CLASSE PRINCIPAL DO PROGRAMA ---
# ==============================================================================

class SysAdminHelper:

    #--- Gaveta Init (Construtor da Classe) ---#
    # (Sem alterações)
    def __init__(self, arquivo_mapa):
        """Construtor da classe: inicializa o console e o mapa."""
        self.console = Console()
        self.ARQUIVO_MAPA = arquivo_mapa
        self.DISPOSITIVOS = {}
    #--- Fim da Gaveta Init ---#

    #--- Gaveta 0 (Carrega o mapa de rede) ---#
    # (Sem alterações)
    def carregar_mapa_rede(self):
        """Tenta carregar o mapa de dispositivos do JSON para self.DISPOSITIVOS."""
        if not os.path.exists(self.ARQUIVO_MAPA):
            self.console.print(
                f"[bold red]AVISO:[/bold red] Arquivo '{self.ARQUIVO_MAPA}' não encontrado. Criando um novo.")
            self.DISPOSITIVOS = {}
            time.sleep(2.5)
            return

        try:
            with open(self.ARQUIVO_MAPA, 'r') as f:
                self.DISPOSITIVOS = json.load(f)
            self.console.print(
                f"[green]Mapa de rede '{self.ARQUIVO_MAPA}' carregado com {len(self.DISPOSITIVOS)} dispositivos![/green]")
            time.sleep(1.5)
        except Exception as e:
            self.console.print(
                f"[bold red]ERRO CRÍTICO ao carregar mapa:[/bold red] {e}")
            self.DISPOSITIVOS = {}
    #--- Fim da Gaveta 0 ---#

    #--- Gaveta 1 (Salva o mapa de rede) ---#
    # (Sem alterações)
    def salvar_mapa_rede(self):
        """Salva o mapa de self.DISPOSITIVOS no arquivo JSON."""
        try:
            with open(self.ARQUIVO_MAPA, 'w') as f:
                json.dump(self.DISPOSITIVOS, f, indent=4)
            self.console.print(
                "\n[bold green]>>> Mapa de rede salvo com sucesso! <<<[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]ERRO AO SALVAR MAPA:[/bold red] {e}")
    #--- Fim da Gaveta 1 ---#

    #--- Gaveta 2 (Desenha o menu principal) ---#
    # CORRIGIDO: Itens do menu REBALANCEADOS (8 vs 7) para alinhamento
    def desenhar_menu(self):
        """Limpa a tela e desenha o menu de opções principal."""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.console.print(
            Rule("[bold cyan]SysAdmin Helper 1.0[/bold cyan]", style="cyan"))
        
        # --- MUDANÇA AQUI: Opções 6 E 7 na esquerda ---
        menu_verificacao = (
            "[dim]--- Verificação Rápida ---\n"
            "[bold cyan]0) CHECK-UP GERAL (ÁRVORE)[/bold cyan]\n"
            "[yellow]1)[/yellow] Pingar Servidor Principal\n"
            "[bold yellow]2) Pingar um Grupo Específico[/bold yellow]\n"
            "[yellow]3)[/yellow] Status do Meu PC (IP/CPU/RAM)\n"
            "[yellow]4)[/yellow] Testar Porta Específica (Firewall)\n"
            "[yellow]5)[/yellow] Monitor de Processos Ativos\n"
            "[yellow]6)[/yellow] Verificar Espaço em Disco\n"
            "[yellow]7)[/yellow] Limpar Arquivos Temporários" # <- Item 7 movido
        )
        
        # --- MUDANÇA AQUI: Começa na Opção 8 ---
        menu_manutencao = (
            "[dim]--- Manutenção ---\n"
            "[yellow]8)[/yellow] Limpar Cache DNS (flushdns)\n"
            "[yellow]9)[/yellow] Renovar IP (release/renew)\n"
            "[yellow]10)[/yellow] Gerenciar Spooler de Impressão\n"
            "[yellow]11)[/yellow] Ver Conexões Ativas (Rápido)\n"
            "[yellow]12)[/yellow] Ver Conexões (com Nomes) (Lento)\n"
            "[bold yellow]13) Gerenciar Mapa de Rede (Add/Rem)[/bold yellow]\n\n"
            "[yellow]14)[/yellow] Sair"
        )
        
        self.console.print(Columns([
            Panel(menu_verificacao, title="VERIFICAR",
                  border_style="green", padding=1),
            Panel(menu_manutencao, title="MANUTENÇÃO",
                  border_style="red", padding=1)
        ], expand=True, equal=True))
        
        return self.console.input("\n[bold]Escolha uma opção: [/bold]")
    #--- Fim da Gaveta 2 ---#

#--- Gaveta 3 (Gerenciar Mapa de Rede) ---#
    # CORREÇÃO: Adicionada alocação automática de grupo com base no prefixo da chave.
    def gerenciar_mapa(self):
        """Sub-menu para Adicionar, Remover e Listar dispositivos em tabelas por grupo."""
        while True:
            os.system('cls')
            self.console.print(
                Rule("[bold cyan]Gerenciador do Mapa de Rede[/bold cyan]"))

            if not self.DISPOSITIVOS:
                self.console.print("[yellow]O mapa de rede está vazio.[/yellow]")
            else:
                # 1. Agrupa os dispositivos em um dicionário
                grupos = {}
                for chave, dados in self.DISPOSITIVOS.items():
                    grupo_nome = dados.get('grupo', 'GERAL').upper()
                    if grupo_nome not in grupos:
                        grupos[grupo_nome] = []
                    grupos[grupo_nome].append((chave, dados))
                
                # 2. Ordena os grupos
                grupos_ordenados = sorted(grupos.items())
                
                # 3. Imprime uma tabela separada para cada grupo
                for grupo_nome, dispositivos_do_grupo in grupos_ordenados:
                    
                    exemplo_chave = "ex: pdv1" # Padrão
                    if grupo_nome == "IMPRESSORA" or grupo_nome == "FISCAIS": 
                        exemplo_chave = "ex: impressora_acougue"
                    elif grupo_nome == "CAIXAS":
                        exemplo_chave = "ex: pdv1"
                    elif grupo_nome.startswith("SERVIDOR"):
                        exemplo_chave = "ex: servidor_principal"
                    
                    tabela_grupo = Table(
                        title=f"--- {grupo_nome} ---", 
                        title_style="bold yellow", 
                        border_style="dim"
                    )
                    
                    tabela_grupo.add_column(f"Chave ({exemplo_chave})", style="cyan", width=30)
                    tabela_grupo.add_column("Apelido", style="white", width=25)
                    tabela_grupo.add_column("Endereço IP", style="magenta", width=16)

                    dispositivos_do_grupo.sort(key=lambda item: item[0])
                    
                    for chave, dados in dispositivos_do_grupo:
                        tabela_grupo.add_row(
                            chave, 
                            dados.get('nome', '[SEM APELIDO]'),
                            dados.get('ip', '[SEM IP]')
                        )
                    
                    self.console.print(tabela_grupo)
                    self.console.print("\n") # Espaço entre tabelas

            self.console.print("\n[1] Adicionar/Atualizar Dispositivo")
            self.console.print("[2] Remover Dispositivo")
            self.console.print("[3] Voltar ao Menu Principal (Salva mudanças)")

            sub_opcao = self.console.input("\nEscolha uma opção: ").strip()

            if sub_opcao == '1':
                self.console.print("\n--- Adicionar/Atualizar Dispositivo ---")
                
                # Validação em loop (Chave)
                while True:
                    # Atualizei o exemplo para mostrar os prefixos mágicos
                    chave = self.console.input(
                        "Digite a [bold]Chave[/bold] (ex: pdv_03, impressora_01, servidor_db): ").strip()
                    if chave: break
                    self.console.print("[bold red]ERRO: A Chave não pode ser vazia. Tente novamente.[/bold red]")

                # Validação em loop (Apelido)
                while True:
                    nome = self.console.input(
                        f"Digite o [bold]Apelido[/bold] para '{chave}': ").strip()
                    if nome: break
                    self.console.print("[bold red]ERRO: O Apelido não pode ser vazio. Tente novamente.[/bold red]")

                # Validação em loop (IP + Duplicidade)
                while True:
                    ip = self.console.input(
                        f"Digite o [bold]IP[/bold] para '{chave}': ").strip()
                    
                    if not ip:
                        self.console.print("[bold red]ERRO: O Endereço IP não pode ser vazio. Tente novamente.[/bold red]")
                        continue

                    ip_duplicado = False
                    for chave_existente, dados_existentes in self.DISPOSITIVOS.items():
                        if dados_existentes.get('ip') == ip and chave_existente != chave:
                            self.console.print(
                                f"[bold red]ERRO: O IP {ip} já está sendo usado por '{dados_existentes.get('nome')}' (Chave: {chave_existente}).[/bold red]")
                            ip_duplicado = True
                            break 
                    
                    if ip_duplicado:
                        continue 
                    break

                # --- MUDANÇA PRINCIPAL AQUI ---
                # Bloco de alocação automática de grupo
                grupo = "GERAL" # Padrão
                chave_lower = chave.lower()

                if chave_lower.startswith("pdv"):
                    grupo = "CAIXAS"
                elif chave_lower.startswith("impressora"):
                    grupo = "IMPRESSORA"
                elif chave_lower.startswith("servidor"):
                    grupo = "SERVIDORES"
                else:
                    # Se não reconhecer o prefixo, aí sim ele pergunta
                    grupo_input = self.console.input(
                        f"Não reconheci o prefixo. Digite o [bold]Grupo[/bold] para '{chave}' [GERAL]: ").strip().upper()
                    grupo = grupo_input if grupo_input else 'GERAL'
                # --- FIM DA MUDANÇA ---
                
                self.DISPOSITIVOS[chave] = {"ip": ip, "nome": nome, "grupo": grupo}
                self.console.print(f"\n[green]Dispositivo '{chave}' salvo automaticamente no grupo '{grupo}'![/green]")
                time.sleep(2) # Pausa um pouco maior para ler a mensagem

            elif sub_opcao == '2':
                self.console.print("\n--- Remover Dispositivo ---")
                chave = self.console.input(
                    "Digite a [bold]Chave[/bold] do dispositivo a remover: ").strip()

                if chave in self.DISPOSITIVOS:
                    removido = self.DISPOSITIVOS.pop(chave)
                    self.console.print(
                        f"\n[green]Dispositivo '{chave}' ({removido.get('nome', '')}) removido![/green]")
                else:
                    self.console.print(
                        f"\n[red]ERRO: Chave '{chave}' não encontrada no mapa.[/red]")
                time.sleep(1.5)

            elif sub_opcao == '3':
                self.salvar_mapa_rede()
                time.sleep(1.5)
                break
            
            else:
                self.console.print("\n[red]Opção inválida.[/red]")
                time.sleep(1)
    #--- Fim da Gaveta 3 ---#



    #--- Gaveta 0.1 (Check-up Geral Assíncrono) ---#
    # (Sem alterações - revertido para Emojis como solicitado)
    async def checkup_geral(self):
        """Roda um ping em TODOS os dispositivos SIMULTANEAMENTE e mostra em uma árvore."""
        self.console.print(
            Rule("[bold cyan]Iniciando Check-up Geral Assíncrono[/bold cyan]"))
        self.console.print(
            "[yellow]Aguarde, pingando todos os dispositivos ao mesmo tempo...[/yellow]")

        if not self.DISPOSITIVOS:
            self.console.print(
                "[yellow]O mapa de rede está vazio. Adicione dispositivos na Opção 13.[/yellow]")
            return

        # 1. Cria a lista de tarefas
        tarefas = []
        for chave, dispositivo in self.DISPOSITIVOS.items():
            tarefas.append(pingar_host_async(
                dispositivo.get('ip', '0.0.0.0'),
                (dispositivo.get('nome', '[SEM NOME]'), dispositivo.get('grupo', 'GERAL'), chave) 
            ))

        # 2. Executa as tarefas
        resultados_brutos = await asyncio.gather(*tarefas)
        
        self.console.print(Rule("[bold cyan]Relatório do Check-up[/bold cyan]"))
        
        # 3. Processa e exibe na Árvore
        arvore = Tree("🌳 [bold]MATRIZ[/bold]")
        grupos_na_arvore = {}
        falhas = 0
        
        resultados_ordenados = sorted(
            resultados_brutos, 
            key=lambda r: (r[0][1], r[0][0]) # Ordena por grupo, depois por nome
        )

        for (nome, grupo, chave), ip, status in resultados_ordenados:
            if grupo not in grupos_na_arvore:
                grupos_na_arvore[grupo] = arvore.add(f"📁 [yellow]{grupo}[/yellow]")
            
            icone = "💻"
            if "imp" in chave.lower(): icone = "🖨️"
            if "pdv" in chave.lower(): icone = "🛒"
            if "servidor" in chave.lower(): icone = "🗄️"
            
            grupos_na_arvore[grupo].add(
                f"{icone} {nome} ({ip})..... {status}"
            )
            
            if "FALHA" in status:
                falhas += 1

        self.console.print(arvore)

        if falhas > 0:
            self.console.print(
                f"\n[bold red]ATENÇÃO:[/bold red] {falhas} dispositivo(s) estão offline!")
        else:
            self.console.print(
                f"\n[bold green]Tudo Certo![/bold green] Todos os dispositivos críticos estão online.")
    #--- Fim da Gaveta 0.1 ---#

    #--- Gaveta 5 (Pingar Servidor) ---#
    # (Sem alterações)
    def pingar_servidor(self, host, nome_amigavel):
        """Função para pingar um host e mostrar o status (mostrando a saída do ping)."""
        self.console.print(
            f"\n[bold yellow]Pingando {nome_amigavel} ({host})...[/bold yellow]")

        if os.name == 'nt':
            comando = f"ping -n 2 {host}"
        else:
            comando = f"ping -c 2 {host}"
        
        resultado = os.system(comando) 

        if resultado == 0:
            self.console.print(
                f"\n[bold green]SUCESSO![/bold green] O {nome_amigavel} ({host}) está respondendo.")
        else:
            self.console.print(
                f"\n[bold red]FALHA![/bold red] O {nome_amigavel} ({host}) está INACESSÍVEL.")
    #--- Fim da Gaveta 5 ---#

    #--- Gaveta 7 (Testar Porta) ---#
    # CORREÇÃO: Adicionado loop 'while True' para validar a porta.
    def testar_porta(self):
        """Tenta conectar a uma porta TCP específica em um host."""
        self.console.print(
            Rule("[bold cyan]Teste de Conexão de Porta (TCP)[/bold cyan]"))
        
        # Este loop já existia na Gaveta 3, mas é bom ter aqui também
        while True:
            host = self.console.input("Digite o IP do alvo (ou 's' para sair): ").strip()
            if host.lower() == 's':
                self.console.print("[yellow]Operação cancelada.[/yellow]")
                return
            if host:
                break
            self.console.print("[bold red]ERRO: O IP não pode ser vazio. Tente novamente.[/bold red]")

        # --- MUDANÇA AQUI ---
        # Adicionado 'while True' para validar a porta
        while True: 
            try:
                porta_str = self.console.input(f"Digite a Porta TCP para {host} (ou 's' para sair): ").strip()
                if porta_str.lower() == 's':
                    self.console.print("[yellow]Operação cancelada.[/yellow]")
                    return

                porta = int(porta_str)
                if not (1 <= porta <= 65535):
                    raise ValueError # Força o erro abaixo
                
                break # Se a porta for válida, sai do loop
                
            except ValueError:
                self.console.print(f"[bold red]ERRO: '{porta_str}' não é uma porta válida (1-65535). Tente novamente.[/bold red]")
        # --- Fim da Mudança ---

        self.console.print(
            f"\n[yellow]Testando conexão com {host} na porta {porta}...[/yellow]")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)

        try:
            s.connect((host, porta))
            self.console.print(
                f"\n[bold green]SUCESSO![/bold green] A porta {porta} está ABERTA em {host}.")
        except socket.timeout:
            self.console.print(
                f"\n[bold red]FALHA (Timeout).[/bold red] (Porta bloqueada ou host offline)")
        except socket.error:
            self.console.print(
                f"\n[bold red]FALHA (Erro).[/bold red] A conexão foi recusada.")
        finally:
            s.close()
    #--- Fim da Gaveta 7 ---#

    #--- Gaveta 8 (Verificar Espaço em Disco) ---#
    # (Esta função não pede input, a mudança será na Gaveta Principal 'run')
    def verificar_espaco_disco(self, caminho):
        r"""Verifica o espaço em disco de um caminho (ex: 'C:' ou '\\Servidor\Backup')"""
        self.console.print(
            f"\n[bold yellow]Verificando espaço em disco de '{caminho}'...[/bold yellow]")
        try:
            uso = psutil.disk_usage(caminho)
            total_gb = uso.total / (1024**3)
            usado_gb = uso.used / (1024**3)
            livre_gb = uso.free / (1024**3)
            percentual_uso = uso.percent

            self.console.print(f"\nCaminho: [bold cyan]{caminho}[/bold cyan]")
            self.console.print(
                f"Total: {total_gb:.2f} GB | Usado: {usado_gb:.2f} GB | Livre: {livre_gb:.2f} GB")

            if percentual_uso > 85:
                self.console.print(
                    f"Percentual de Uso: [bold red]{percentual_uso}% (ALERTA!)[/bold red]")
            else:
                self.console.print(
                    f"Percentual de Uso: [bold green]{percentual_uso}%[/bold green]")
            return True # Retorna sucesso
        except FileNotFoundError:
            self.console.print(
                f"\n[bold red]ERRO![/bold red] Caminho não encontrado: '{caminho}'")
            return False # Retorna falha
        except Exception as e:
            self.console.print(f"\n[bold red]ERRO INESPERADO![/bold red] {e}")
            return False # Retorna falha
    #--- Fim da Gaveta 8 ---#

    #--- Gaveta 9 (Limpar Arquivos Temporários) ---#
    # (Esta função às vezes pede input, vamos adicionar um loop nela)
    # CORREÇÃO: Adicionado loop para 'caminho_base' e 'usuario'
    def limpar_temporarios(self):
        """Apaga os arquivos temporários de um caminho base (local ou remoto)."""
        
        while True:
            caminho_base = self.console.input(
                "\nDigite o caminho base (ex: C: ou \\\\PC-01\\C$) (ou 's' para sair): ").strip()
            if caminho_base.lower() == 's':
                self.console.print("[yellow]Operação cancelada.[/yellow]")
                return
            if not caminho_base:
                caminho_base = 'C:'
                
            self.console.print(
                f"\n[bold yellow]Iniciando limpeza em '{caminho_base}'...[/bold yellow]")

            if caminho_base.startswith(r'\\'):
                while True:
                    usuario = self.console.input(
                        "Qual o nome da pasta de usuário nessa máquina? (ex: Beatriz) (ou 's' para sair): ").strip()
                    if usuario.lower() == 's':
                        self.console.print("[yellow]Operação cancelada.[/yellow]")
                        return
                    if not usuario:
                        self.console.print("[red]Nome de usuário é necessário para limpar a pasta de usuário.[/red]")
                        caminhos_temp = [os.path.join(caminho_base, 'Windows', 'Temp')]
                        break # Continua só com a pasta do Windows
                    else:
                        caminhos_temp = [
                            os.path.join(caminho_base, 'Windows', 'Temp'),
                            os.path.join(caminho_base, 'Users', usuario,
                                        'AppData', 'Local', 'Temp')
                        ]
                        break
            else:
                try:
                    usuario = os.getlogin()
                    caminhos_temp = [
                        r'C:\Windows\Temp',
                        rf'C:\Users\{usuario}\AppData\Local\Temp'
                    ]
                except Exception:
                    caminhos_temp = [r'C:\Windows\Temp'] # Fallback
            
            total_arquivos_apagados = 0
            pasta_valida_encontrada = False
            for pasta in caminhos_temp:
                self.console.print(f"\nVerificando pasta: [cyan]{pasta}[/cyan]")
                if not os.path.exists(pasta):
                    self.console.print(f"[dim]Caminho não existe. Pulando...[/dim]")
                    continue
                
                pasta_valida_encontrada = True
                arquivos_apagados = 0
                # ... (resto do código de limpeza é o mesmo) ...
                for nome_item in os.listdir(pasta):
                    caminho_completo = os.path.join(pasta, nome_item)
                    try:
                        if os.path.isfile(caminho_completo) or os.path.islink(caminho_completo):
                            os.remove(caminho_completo)
                            arquivos_apagados += 1
                        elif os.path.isdir(caminho_completo):
                            shutil.rmtree(caminho_completo)
                            arquivos_apagados += 1
                    except PermissionError:
                        self.console.print(
                            f"[dim] - Não foi possível apagar '{nome_item}' (em uso).[/dim]")
                    except Exception:
                        pass
                
                if arquivos_apagados > 0:
                    self.console.print(
                        f"[green]>>> {arquivos_apagados} itens removidos de '{pasta}'.[/green]")
                else:
                    self.console.print(
                        f"[yellow]Pasta já estava limpa.[/yellow]")
                total_arquivos_apagados += arquivos_apagados
            
            if not pasta_valida_encontrada:
                self.console.print(f"[bold red]ERRO: Nenhum caminho de limpeza válido foi encontrado para '{caminho_base}'.[/bold red]")
                time.sleep(1)
                # O loop 'while True' principal vai rodar de novo, pedindo o 'caminho_base'
            else:
                self.console.print(
                    f"\n[bold green]LIMPEZA CONCLUÍDA![/bold green] Total de {total_arquivos_apagados} itens removidos.")
                break # Sucesso, sai do loop 'while True'
    #--- Fim da Gaveta 9 ---#

    #--- Gaveta 10 (Status do PC Local) ---#
    # (Sem alterações, esta função já está 100% revertida para TUI)
    def verificar_sistema_local(self):
        """Mostra IP, Gateway, CPU e RAM da máquina local."""
        self.console.print(
            "\n[bold yellow]Verificando Status do Sistema Local...[/bold yellow]")
        try:
            c = wmi.WMI()
            query = "SELECT * FROM Win32_IP4RouteTable WHERE Destination = '0.0.0.0' AND Mask = '0.0.0.0'"
            gateways = c.query(query)
            gateway_ip = gateways[0].NextHop if gateways else None
            if gateway_ip:
                self.console.print(
                    f"\n[bold green]Gateway Padrão (Roteador):[/bold green] {gateway_ip}")
            else:
                self.console.print(
                    "\n[bold red]Gateway Padrão NÃO ENCONTRADO.[/bold red]")
            self.console.print("---")
            
            interfaces = psutil.net_if_addrs()
            encontrou_ip = False
            for nome_iface, addrs in interfaces.items():
                if "Loopback" in nome_iface or "VMware" in nome_iface or "VirtualBox" in nome_iface:
                    continue
                # AF_INET = 2 (IPv4)
                ipv4_addrs = [addr for addr in addrs if addr.family == socket.AF_INET]
                if ipv4_addrs:
                    encontrou_ip = True
                    self.console.print(
                        f"Interface: [bold cyan]{nome_iface}[/bold cyan]")
                    for addr in ipv4_addrs:
                        self.console.print(
                            f"  [green]IPv4:[/green] {addr.address} (Máscara: {addr.netmask})")
            if not encontrou_ip:
                self.console.print(
                    "\n[red]Nenhum adaptador de rede IPv4 ativo encontrado.[/red]")
        except Exception:
            self.console.print(f"\n[bold red]ERRO AO LER REDE:[/bold red] (WMI ou PSUtil falhou)")

        try:
            self.console.print(Rule(style="dim"))
            self.console.print("[bold yellow]Verificando CPU e RAM...[/bold yellow]")
            psutil.cpu_percent(interval=None)
            time.sleep(0.1)
            cpu_uso = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            ram_total_gb = ram.total / (1024**3)
            ram_usada_gb = ram.used / (1024**3)
            ram_percent = ram.percent
            
            self.console.print(f"Uso da CPU: [bold {'red' if cpu_uso > 85 else 'green'}]{cpu_uso}%[/bold {'red' if cpu_uso > 85 else 'green'}]")
            self.console.print(
                f"Uso de RAM: [bold cyan]{ram_usada_gb:.2f} GB[/bold cyan] / {ram_total_gb:.2f} GB ({ram_percent}%)")
            if ram_percent > 85:
                self.console.print("[bold red](ALERTA: Memória RAM alta!)[/bold red]")
        except Exception as e:
            self.console.print(f"\n[bold red]ERRO AO LER CPU/RAM:[/bold red] {e}")
    #--- Fim da Gaveta 10 ---#

    #--- Gaveta 11 (Limpar Cache DNS) ---#
    # (Sem alterações)
    def limpar_cache_dns(self):
        """Roda 'ipconfig /flushdns' no Windows (modo silencioso)."""
        self.console.print("\n[bold yellow]Limpando o cache DNS...[/bold yellow]")
        if os.name == 'nt':
            try:
                subprocess.run(
                    ["ipconfig", "/flushdns"],
                    capture_output=True, text=True, check=True, shell=True
                )
                self.console.print(
                    "\n[bold green]SUCESSO![/bold green] O cache DNS foi limpo.")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.console.print(
                    "\n[bold red]FALHA![/bold red] Não foi possível executar o 'ipconfig /flushdns'.")
        else:
            self.console.print(
                "\n[bold red]ERRO:[/bold red] Este comando só funciona no Windows.")
    #--- Fim da Gaveta 11 ---#

    #--- Gaveta 12 (Renovar IP) ---#
    # (Sem alterações)
    def renovar_ip(self):
        """Roda 'ipconfig /release' e '/renew' no Windows (modo silencioso)."""
        if os.name == 'nt':
            try:
                self.console.print(
                    "\n[bold yellow]Liberando o IP (release)...[/bold yellow]")
                subprocess.run(
                    ["ipconfig", "/release"],
                    capture_output=True, text=True, check=True, shell=True
                )
                self.console.print(
                    "\n[bold yellow]Renovando o IP (renew)...[/bold yellow]")
                subprocess.run(
                    ["ipconfig", "/renew"],
                    capture_output=True, text=True, check=True, shell=True
                )
                self.console.print(
                    "\n[bold green]SUCESSO![/bold green] Processo de renovação de IP concluído.")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.console.print(
                    "\n[bold red]FALHA![/bold red] Não foi possível executar os comandos de IP.")
        else:
            self.console.print(
                "\n[bold red]ERRO:[/bold red] Este comando só funciona no Windows.")
    #--- Fim da Gaveta 12 ---#

    #--- Gaveta 13 (Limpar Fila de Impressão) ---#
    # (Sem alterações)
    def limpar_fila_impressao(self):
        r"""Apaga os arquivos na pasta C:\Windows\System32\spool\PRINTERS"""
        self.console.print(
            "\n[bold yellow]Tentando limpar a fila de impressão (pasta PRINTERS)...[/bold yellow]")
        caminho_spool = r'C:\Windows\System32\spool\PRINTERS'
        
        if not os.path.exists(caminho_spool):
            self.console.print(
                f"[red]ERRO: Caminho '{caminho_spool}' não encontrado.[/red]")
            return
        
        try:
            arquivos_na_fila = os.listdir(caminho_spool)
            if not arquivos_na_fila:
                self.console.print(
                    "[green]A fila de impressão já está limpa (pasta vazia).[/green]")
                return
            
            apagados = 0
            for arquivo in arquivos_na_fila:
                caminho_arquivo = os.path.join(caminho_spool, arquivo)
                try:
                    os.remove(caminho_arquivo)
                    apagados += 1
                except Exception:
                    self.console.print(
                        f"[dim] - Não foi possível apagar '{arquivo}' (em uso/permissão).[/dim]")
            
            if apagados > 0:
                self.console.print(
                    f"\n[bold green]SUCESSO![/bold green] {apagados} trabalhos removidos da fila.")
            else:
                self.console.print(
                    "\n[yellow]Não foi possível apagar nenhum arquivo (podem estar em uso).[/yellow]")
        except PermissionError:
            self.console.print("\n[bold red]ERRO: Acesso Negado![/bold red]")
        except Exception as e:
            self.console.print(f"\n[bold red]ERRO INESPERADO:[/bold red] {e}")
    #--- Fim da Gaveta 13 ---#

    #--- Gaveta 14 (Gerenciar Spooler de Impressão) ---#
    # CORREÇÃO: Adicionado 'time.sleep(1)' no 'else' de opção inválida.
    def gerenciar_spooler(self):
        """Mostra um sub-menu para Iniciar, Parar, Reiniciar ou Habilitar o Spooler."""
        if os.name != 'nt':
            self.console.print(
                "\n[bold red]ERRO:[/bold red] Esta função está disponível apenas no Windows.")
            return

        while True:
            os.system('cls')
            self.console.print(
                Rule("[bold cyan]Gerenciador de Spooler de Impressão[/bold cyan]"))
            status = ""
            startup_type = ""
            
            try:
                service = psutil.win_service_get('spooler')
                status = service.status()
                startup_type = service.start_type()
            except psutil.NoSuchProcess:
                self.console.print(
                    "\n[bold red]ERRO:[/bold red] Serviço 'spooler' não encontrado neste PC.")
                time.sleep(3)
                return
            except Exception as e:
                self.console.print(f"\n[bold red]ERRO INESPERADO ao ler serviço:[/bold red] {e}")
                time.sleep(3)
                return

            self.console.print("\nStatus Atual: ", end="")
            if status == 'running':
                self.console.print(
                    f"[bold green]Rodando[/bold green] (Inicialização: {startup_type})")
            elif startup_type == 'disabled':
                self.console.print(f"[bold red]DESATIVADO[/bold red]")
            else:
                self.console.print(
                    f"[bold yellow]Parado[/bold yellow] (Inicialização: {startup_type})")

            self.console.print("\n[1] Iniciar Serviço")
            self.console.print("[2] Parar Serviço (Manutenção)")
            self.console.print("[3] Reiniciar Serviço (Limpar fila)")
            self.console.print("[4] Habilitar (Definir como Automático)")
            self.console.print("[5] Desativar (Proibir inicialização)")
            self.console.print("[6] Voltar ao Menu Principal")
            sub_opcao = self.console.input("\nEscolha uma opção: ").strip()

            try:
                if sub_opcao == '1':
                    # ... (código da opção 1) ...
                    if status == 'running':
                        self.console.print("\n[yellow]O serviço já está rodando.[/yellow]")
                    elif startup_type == 'disabled':
                        self.console.print(
                            "\n[bold red]ERRO:[/bold red] O serviço está Desativado. Use a Opção 4 para Habilitar primeiro.")
                    else:
                        self.console.print("\n[yellow]Iniciando spooler...[/yellow]")
                        subprocess.run(["net", "start", "spooler"], check=True, 
                                    capture_output=True, text=True, shell=True)
                        self.console.print("[bold green]Serviço iniciado![/bold green]")

                elif sub_opcao == '2':
                    # ... (código da opção 2) ...
                    if status == 'stopped':
                        self.console.print("\n[yellow]O serviço já está parado.[/yellow]")
                    else:
                        self.console.print("\n[yellow]Parando spooler...[/yellow]")
                        subprocess.run(["net", "stop", "spooler"], check=True, 
                                    capture_output=True, text=True, shell=True)
                        self.console.print("[bold green]Serviço parado![/bold green]")
                elif sub_opcao == '3':
                    # ... (código da opção 3) ...
                    if startup_type == 'disabled':
                        self.console.print(
                            "\n[bold red]ERRO:[/bold red] O serviço está Desativado. Use a Opção 4 para Habilitar primeiro.")
                    else:
                        self.console.print("\n[yellow]Reiniciando spooler...[/yellow]")
                        self.console.print("[dim] - Parando o serviço...[/dim]")
                        subprocess.run(["net", "stop", "spooler"], check=True, 
                                    capture_output=True, text=True, shell=True)
                        
                        limpar = self.console.input(
                            "Deseja também limpar a fila de trabalhos presos? (S/N): ").upper().strip()
                        if limpar == 'S' or limpar == 'SIM':
                            self.limpar_fila_impressao() # Chama a Gaveta 13
                        
                        self.console.print("[dim] - Iniciando o serviço...[/dim]")
                        subprocess.run(["net", "start", "spooler"], check=True, 
                                    capture_output=True, text=True, shell=True)
                        self.console.print("[bold green]Serviço reiniciado![/bold green]")

                elif sub_opcao == '4':
                    # ... (código da opção 4) ...
                    self.console.print("\n[yellow]Habilitando o serviço (start= auto)...[/yellow]")
                    subprocess.run(["sc", "config", "spooler", "start=", "auto"], 
                                check=True, capture_output=True, text=True, shell=True)
                    self.console.print("[bold green]Serviço definido como Automático![/bold green]")

                elif sub_opcao == '5':
                    # ... (código da opção 5) ...
                    self.console.print("\n[yellow]Desativando o serviço (start= disabled)...[/yellow]")
                    if status == 'running':
                        self.console.print("[dim] - Serviço está rodando. Parando ele primeiro...[/dim]")
                        subprocess.run(["net", "stop", "spooler"], check=True, 
                                    capture_output=True, text=True, shell=True)
                    
                    subprocess.run(["sc", "config", "spooler", "start=", "disabled"], 
                                check=True, capture_output=True, text=True, shell=True)
                    self.console.print("[bold red]Serviço Desativado com sucesso![/bold red]")
                
                elif sub_opcao == '6':
                    break
                
                else:
                    self.console.print("\n[red]Opção inválida.[/red]")
                    time.sleep(1) # <-- MUDANÇA AQUI (Pausa no erro)

            except subprocess.CalledProcessError:
                self.console.print("[bold red]Falha ao executar comando. Tente como Administrador.[/bold red]")
            except Exception as e:
                self.console.print(f"[bold red]ERRO INESPERADO: {e}[/bold red]")

            if sub_opcao in ['1', '2', '3', '4', '5']:
                time.sleep(3)
    #--- Fim da Gaveta 14 ---#

    #--- Gaveta 15 (Ver Conexões Ativas - Rápido) ---#
    # (Sem alterações)
    def ver_conexoes_rede(self):
        """Mostra as conexões de rede ativas (como 'netstat')"""
        self.console.print(
            Rule("[bold cyan]Conexões de Rede Ativas (netstat)[/bold cyan]"))
        try:
            conexoes = psutil.net_connections(kind='tcp')
            tabela = Table(title="Conexões TCP Ativas", border_style="dim")
            tabela.add_column("Endereço Local", style="cyan")
            tabela.add_column("Porta Local", style="yellow")
            tabela.add_column("Endereço Remoto", style="magenta")
            tabela.add_column("Porta Remota", style="yellow")
            tabela.add_column("Status", style="green")
            
            if not conexoes:
                self.console.print("[dim]Nenhuma conexão TCP ativa encontrada.[/dim]")
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
            self.console.print(tabela)
        except psutil.AccessDenied:
            self.console.print("\n[bold red]ERRO: Acesso Negado![/bold red]")
        except Exception as e:
            self.console.print(f"\n[bold red]ERRO INESPERADO:[/bold red] {e}")
    #--- Fim da Gaveta 15 ---#

    #--- Gaveta 16 (Ver Conexões Ativas - Lento) ---#
    # (Sem alterações)
    def ver_conexoes_com_nomes(self):
        """Mostra conexões ativas, tentando resolver o IP para nome."""
        self.console.print(
            Rule("[bold cyan]Conexões de Rede Ativas (com Resolução de Nomes)[/bold cyan]"))
        self.console.print(
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
                self.console.print("[dim]Nenhuma conexão TCP ativa encontrada.[/dim]")
                return

            for conn in conexoes:
                ip_local, porta_local = conn.laddr if conn.laddr else ("*", "*")
                ip_remoto, porta_remota = conn.raddr if conn.raddr else ("*", "*")
                
                nome_remoto_final = str(ip_remoto)
                
                if ip_remoto not in ("*", "127.0.0.1", ""):
                    try:
                        socket.setdefaulttimeout(0.5) # Timeout rápido
                        nome_host = socket.gethostbyaddr(ip_remoto)[0]
                        nome_remoto_final = f"{nome_host} ({ip_remoto})"
                    except (socket.gaierror, socket.timeout, OSError):
                        pass
                    finally:
                        socket.setdefaulttimeout(None) # Reseta o timeout

                tabela.add_row(
                    f"{ip_local}:{porta_local}",
                    nome_remoto_final,
                    str(porta_remota),
                    str(conn.status)
                )
            self.console.print(tabela)
        except psutil.AccessDenied:
            self.console.print("\n[bold red]ERRO: Acesso Negado![/bold red]")
        except Exception as e:
            self.console.print(f"\n[bold red]ERRO INESPERADO:[/bold red] {e}")
    #--- Fim da Gaveta 16 ---#

    #--- Gaveta 17 (Monitor de Processos) ---#
    # (Sem alterações, este já estava em loop)
    def verificar_processos_top(self):
        """Lista os 5 processos que mais consomem CPU ou RAM localmente."""
        while True:
            self.console.print(
                Rule("[bold yellow]Opções de Monitoramento de Processos[/bold yellow]"))
            self.console.print("[1] Ordenar por CPU (Processador)")
            self.console.print("[2] Ordenar por RAM (Memória)")
            self.console.print("[bold red][3] Matar Processo (Kill)[/bold red]")
            self.console.print("[4] Voltar ao Menu Principal")

            sub_opcao = self.console.input("\nEscolha a ordem: ").strip()

            ordenar_por = None
            if sub_opcao == '1':
                ordenar_por = 'cpu'
            elif sub_opcao == '2':
                ordenar_por = 'ram'
            elif sub_opcao == '3':
                self._matar_processo() # Chama a Sub-Gaveta
                time.sleep(2)
                continue
            elif sub_opcao == '4':
                return
            else:
                self.console.print("[red]Opção inválida![/red]")
                time.sleep(1)
                continue

            if ordenar_por:
                self.console.print(
                    Rule(f"[bold cyan]Top 5 Processos por Uso de {ordenar_por.upper()}[/bold cyan]"))
                try:
                    # ... (código de listar processos) ...
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
                        tabela.add_row(
                            f"{p['pid']}",
                            f"{p['cpu']:.1f}",
                            f"{p['rss_mb']:.0f}",
                            p['name'],
                        )
                    self.console.print(tabela)
                except Exception as e:
                    self.console.print(
                        f"\n[bold red]ERRO INESPERADO AO LER PROCESSOS:[/bold red] {e}")

                self.console.input(
                    "\n[dim]Pressione Enter para voltar...[/dim]")
    #--- Fim da Gaveta 17 ---#

    #--- Sub-Gaveta 17.1 (Matar Processo) ---#
    # (Sem alterações)
    def _matar_processo(self):
        r"""Função interna para forçar a finalização de um processo."""
        self.console.print(
            Rule("[bold red]Forçar Finalização de Processo (Kill)[/bold red]"))
        
        # --- MUDANÇA AQUI: Loop para validar o input ---
        while True:
            pid_ou_nome = self.console.input(
                "Digite o NOME (ex: chrome.exe) ou o PID (ex: 1234) (ou 's' para sair): ").strip()

            if pid_ou_nome.lower() == 's':
                self.console.print("[yellow]Operação cancelada.[/yellow]")
                return
            
            if not pid_ou_nome:
                self.console.print("[bold red]ERRO: Você precisa digitar um Nome ou PID. Tente novamente.[/bold red]")
                continue # Pede de novo

            try:
                # Tenta matar por PID
                pid = int(pid_ou_nome)
                processo = psutil.Process(pid)
                nome_processo = processo.name()
                processo.kill()
                self.console.print(
                    f"\n[bold green]SUCESSO![/bold green] Processo '{nome_processo}' (PID: {pid}) foi encerrado.")
                return # Sucesso, sai da função
            
            except ValueError:
                # Se não for número, tenta matar por Nome
                nome_alvo = pid_ou_nome.lower()
                processos_encerrados = 0
                for p in psutil.process_iter(['name', 'pid']):
                    if p.name().lower() == nome_alvo:
                        try:
                            processo_para_matar = psutil.Process(p.pid)
                            processo_para_matar.kill()
                            self.console.print(
                                f"Encerrando: [cyan]{p.name()} (PID: {p.pid})[/cyan]...")
                            processos_encerrados += 1
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            self.console.print(
                                f"[red]Falha ao encerrar {p.name()} (PID: {p.pid}).[/red]")
                
                if processos_encerrados > 0:
                    self.console.print(
                        f"\n[bold green]SUCESSO![/bold green] {processos_encerrados} processo(s) com nome '{nome_alvo}' foram encerrados.")
                    return # Sucesso, sai da função
                else:
                    self.console.print(
                        f"[bold red]ERRO:[/bold red] Nenhum processo encontrado com o nome '{nome_alvo}'. Tente novamente.[/bold red]")
                    # O loop 'while True' vai rodar de novo
            
            except psutil.NoSuchProcess:
                self.console.print(
                    f"[bold red]ERRO:[/bold red] Processo com PID {pid} não encontrado. Tente novamente.[/bold red]")
            except psutil.AccessDenied:
                self.console.print("\n[bold red]ERRO: Acesso Negado! Tente novamente.[/bold red]")
            except Exception as e:
                self.console.print(f"\n[bold red]ERRO INESPERADO:[/bold red] {e}. Tente novamente.[/bold red]")
    #--- Fim da Sub-Gaveta 17.1 ---#


    #--- Gaveta 18 (Pingar por Grupo) ---#
    # CORREÇÃO: Adicionado loop 'while True' para validar o grupo.
    async def pingar_grupo_especifico(self):
        """Pingar todos os dispositivos de um grupo específico de forma assíncrona."""
        self.console.print(Rule("[bold cyan]Ping por Grupo[/bold cyan]"))
        
        grupos_existentes_set = set(
            dados.get('grupo', 'GERAL').upper() for dados in self.DISPOSITIVOS.values()
        )
        grupos_existentes = sorted(list(grupos_existentes_set))
        
        self.console.print("[dim]Grupos disponíveis:[/dim] " + ", ".join(grupos_existentes))

        # --- MUDANÇA AQUI: Loop de validação ---
        while True:
            grupo_alvo = self.console.input("\nDigite o nome do Grupo a pingar (ou 's' para sair): ").strip().upper()

            if grupo_alvo.lower() == 's':
                self.console.print("[yellow]Operação cancelada.[/yellow]")
                return

            if not grupo_alvo:
                self.console.print("[bold red]ERRO: O nome do grupo não pode ser vazio. Tente novamente.[/bold red]")
                continue # Pede de novo
            
            if grupo_alvo not in grupos_existentes_set:
                 self.console.print(f"[bold red]ERRO: Grupo '{grupo_alvo}' não encontrado. Tente novamente.[/bold red]")
                 continue # Pede de novo

            # Filtra os dispositivos que pertencem a esse grupo
            dispositivos_no_grupo = []
            for chave, dados in self.DISPOSITIVOS.items():
                if dados.get('grupo', 'GERAL').upper() == grupo_alvo:
                    dispositivos_no_grupo.append((chave, dados))
            
            # Esta verificação é redundante se o grupo existe, mas é segura
            if not dispositivos_no_grupo:
                self.console.print(f"[red]Nenhum dispositivo encontrado no grupo '{grupo_alvo}'.[/red]")
                return
            
            break # Grupo é válido, sai do loop
        # --- Fim da Mudança ---

        self.console.print(f"\n[yellow]Pingando {len(dispositivos_no_grupo)} dispositivos do grupo '{grupo_alvo}'...[/yellow]")
        
        # ... (código de ping e tabela) ...
        tarefas = []
        for chave, dados in dispositivos_no_grupo:
            tarefas.append(pingar_host_async(
                dados.get('ip', '0.0.0.0'),
                (dados.get('nome', '[SEM NOME]'), dados.get('grupo', 'GERAL'), chave)
            ))
        
        resultados_brutos = await asyncio.gather(*tarefas)
        tabela_status = Table(title=f"Status do Grupo: {grupo_alvo}", border_style="dim")
        tabela_status.add_column("Apelido", style="cyan", width=30)
        tabela_status.add_column("IP", style="magenta", width=15)
        tabela_status.add_column("Status", style="white")

        falhas = 0
        resultados_ordenados = sorted(resultados_brutos, key=lambda r: r[0][0])
        
        for (nome, grupo, chave), ip, status in resultados_ordenados:
            tabela_status.add_row(nome, ip, status)
            if "FALHA" in status:
                falhas += 1
        
        self.console.print(tabela_status)
        if falhas > 0:
            self.console.print(f"\n[bold red]ATENÇÃO:[/bold red] {falhas} dispositivo(s) offline no grupo.")
        else:
            self.console.print(f"\n[bold green]Tudo Certo![/bold green] Todos os dispositivos do grupo estão online.")
    #--- Fim da Gaveta 18 ---#

  # ==========================================================================
    # --- GAVETA PRINCIPAL (Loop do Programa) ---
    # CORREÇÃO: Opção 1 agora busca por 'servidor_principal'
    # ==========================================================================
    def run(self):
        """Inicia o programa, carrega o mapa e entra no loop principal."""
        
        self.carregar_mapa_rede() # Chama a Gaveta 0

        while True:
            opcao = self.desenhar_menu() # Chama a Gaveta 2

            try:
                if opcao == '0':
                    asyncio.run(self.checkup_geral()) # Chama a Gaveta 0.1
                
                # --- MUDANÇA AQUI ---
                elif opcao == '1':
                    if 'servidor_principal' in self.DISPOSITIVOS: # <-- MUDADO
                        dispositivo = self.DISPOSITIVOS['servidor_principal'] # <-- MUDADO
                        self.pingar_servidor(dispositivo['ip'], dispositivo['nome']) # Chama a Gaveta 5
                    else:
                        self.console.print(
                            "\n[bold red]ERRO: 'servidor_principal' não cadastrado no mapa.[/bold red]") # <-- MUDADO
                # --- Fim da Mudança ---
                
                elif opcao == '2':
                    asyncio.run(self.pingar_grupo_especifico()) # Chama a Gaveta 18
                
                elif opcao == '3':
                    self.verificar_sistema_local() # Chama a Gaveta 10
                
                elif opcao == '4':
                    self.testar_porta() # Chama a Gaveta 7
                
                elif opcao == '5':
                    self.verificar_processos_top() # Chama a Gaveta 17
                    continue 

                elif opcao == '6':
                    while True:
                        caminho = self.console.input(
                            "\nDigite o caminho a verificar (ex: C: ou \\\\Servidor\\C$) (ou 's' para sair): ").strip()
                        if caminho.lower() == 's':
                            self.console.print("[yellow]Operação cancelada.[/yellow]")
                            break
                        if not caminho:
                            caminho = 'C:'
                            
                        if self.verificar_espaco_disco(caminho):
                            break
                        else:
                            self.console.print("[dim]Tente novamente ou digite 's' para sair.[/dim]")
                
                elif opcao == '7':
                    self.limpar_temporarios() # Chama a Gaveta 9
                
                elif opcao == '8':
                    self.limpar_cache_dns() # Chama a Gaveta 11
                
                elif opcao == '9':
                    self.renovar_ip() # Chama a Gaveta 12
                
                elif opcao == '10':
                    self.gerenciar_spooler() # Chama a Gaveta 14
                    continue 

                elif opcao == '11':
                    self.ver_conexoes_rede() # Chama a Gaveta 15
                
                elif opcao == '12':
                    self.ver_conexoes_com_nomes() # Chama a Gaveta 16
                
                elif opcao == '13':
                    self.gerenciar_mapa() # Chama a Gaveta 3
                    continue 

                elif opcao == '14':
                    self.console.print("\nObrigado por usar o SysAdmin Helper!")
                    break
                
                else:
                    self.console.print("\n[red]Opção inválida![/red]")
                    time.sleep(1) 

                # Pausa padrão
                if opcao not in ['0', '2', '5', '7', '10', '13', '14']:
                    self.console.input("\n[dim]Pressione Enter para voltar...[/dim]")
                elif opcao in ['0', '2', '7']: 
                     self.console.input("\n[dim]Operação concluída. Pressione Enter para voltar...[/dim]")

            except Exception as e:
                self.console.print(f"\n[bold red]ERRO CRÍTICO NO LOOP PRINCIPAL:[/bold red] {e}")
                self.console.print("\n[dim]Pressione Enter para tentar continuar...[/dim]")

        self.console.print("\nPrograma finalizado!")
    #--- Fim da GAVETA PRINCIPAL ---#


# ==============================================================================
# --- PONTO DE ENTRADA DO PROGRAMA ---
# (Sem alterações)
# ==============================================================================
if __name__ == "__main__":
    ARQUIVO_CONFIG = 'devices.json'
    
    # 1. Cria uma 'instância' da nossa classe
    app = SysAdminHelper(arquivo_mapa=ARQUIVO_CONFIG)
    
    # 2. Chama o 'cérebro' (a Gaveta Principal)
    app.run()