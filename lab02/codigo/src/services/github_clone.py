import subprocess
import time
import os
import shutil
import stat
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


def find_exact_case_match(base_dir, repo_name):
    """
    Procura por uma pasta que corresponda EXATAMENTE ao nome (case-sensitive)
    Retorna o caminho se encontrar, None caso contrário
    """
    try:
        if not os.path.exists(base_dir):
            return None
        for dirname in os.listdir(base_dir):
            if dirname == repo_name:
                fullpath = os.path.join(base_dir, dirname)
                if os.path.exists(os.path.join(fullpath, '.git')):
                    return fullpath
        return None
    except Exception as e:
        print(f"[WARNING] Erro ao verificar diretórios em {base_dir}: {e}")
        return None

def find_case_insensitive_conflicts(base_dir, repo_name):
    """
    Encontra pastas que diferem apenas por case (maiúscula/minúscula)
    Retorna lista de conflitos encontrados
    """
    try:
        if not os.path.exists(base_dir):
            return []
        conflicts = []
        for dirname in os.listdir(base_dir):
            if dirname.lower() == repo_name.lower() and dirname != repo_name:
                conflicts.append(dirname)
        return conflicts
    except Exception as e:
        print(f"[WARNING] Erro ao verificar conflitos em {base_dir}: {e}")
        return []

def is_path_too_long_error(error_message):
    """Detecta se o erro é relacionado a caminho longo no Windows"""
    keywords = ["unable to create file", "filename too long", "file name too long", "path too long"]
    return any(keyword.lower() in error_message.lower() for keyword in keywords)

def configure_git_for_windows():
    """Configura Git para lidar melhor com caminhos longos no Windows"""
    if os.name == "nt":
        try:
            subprocess.run(["git", "config", "--global", "core.longpaths", "true"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[CONFIG] Git configurado para suportar caminhos longos")
        except:
            pass

def remove_readonly(func, path, excinfo):
    """Handler para remover arquivos read-only"""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"[WARNING] Não foi possível remover {path}: {e}")

def safe_rmtree(path):
    """Remove pasta de forma segura"""
    try:
        shutil.rmtree(path, onerror=remove_readonly)
        return True
    except Exception as e:
        print(f"[ERROR] Falha ao remover {path}: {e}")
        return False

def save_urls_to_file(urls, filename, description):
    """Salva uma lista de URLs em arquivo texto separados por ponto e vírgula na pasta txtFiles"""
    try:
        if not urls:
            print(f"[INFO] Lista vazia para {description}, arquivo não será criado.")
            return False
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        base_dir = os.getcwd()
        txt_dir = os.path.join(base_dir, '..', 'txtFiles')
        os.makedirs(txt_dir, exist_ok=True)
        filepath = os.path.join(txt_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {description} - {timestamp}\n")
            f.write(f"# Total: {len(urls)}\n\n")
            f.write(';'.join(urls))
        print(f"{description} ({len(urls)} itens) salvo em '{filepath}'")
        return True
    except Exception as e:
        print(f"[ERROR] Falha ao salvar arquivo {filename}: {e}")
        return False

def save_skip_log(skipped_log, filename):
    """Salva log detalhado dos repositórios que foram pulados na pasta txtFiles"""
    try:
        if not skipped_log:
            return False
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        base_dir = os.getcwd()
        txt_dir = os.path.join(base_dir, '..', 'txtFiles')
        os.makedirs(txt_dir, exist_ok=True)
        filepath = os.path.join(txt_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Log de Repositórios Pulados - {timestamp}\n")
            f.write(f"# Total: {len(skipped_log)}\n\n")
            for entry in skipped_log:
                f.write(f"URL: {entry['url']}\n")
                f.write(f"Nome: {entry['name']}\n")
                f.write(f"Nome Completo: {entry.get('name_with_owner', entry['name'])}\n")
                f.write(f"Razão: {entry['reason']}\n")
                if 'existing_path' in entry:
                    f.write(f"Caminho Existente: {entry['existing_path']}\n")
                if 'conflicts' in entry:
                    f.write(f"Conflitos de Case: {', '.join(entry['conflicts'])}\n")
                f.write("-" * 50 + "\n")
        print(f"✓ Log de skips salvo em '{filepath}'")
        return True
    except Exception as e:
        print(f"[ERROR] Falha ao salvar log de skips: {e}")
        return False

def load_repos_from_csv(csv_file_path):
    """Carrega repositórios do arquivo CSV"""
    repos = []
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                repos.append({
                    'url': row['url'],
                    'name': row['name'],
                    'name_with_owner': row.get('name_with_owner', row['name']),
                    'size_kb': int(row.get('disk_usage_kb', '0')) if row.get('disk_usage_kb', '0').isdigit() else 0
                })
        print(f"[INFO] {len(repos)} repositórios carregados do CSV")
        return repos
    except Exception as e:
        print(f"[ERROR] Falha ao carregar CSV {csv_file_path}: {e}")
        return []

successful_repos = []
skipped_repos_log = []

def git_clone_case_sensitive(repo_info, base_dir="./cloned_repos", retries=3):
    """
    Clone case-sensitive usando name_with_owner para evitar conflitos
    entre repositórios com mesmo nome mas donos diferentes.
    """
    repo_url = repo_info['url']
    repo_name = repo_info['name']
    name_with_owner = repo_info.get('name_with_owner', repo_name)
    # Substitui "/" por "-" para nome de pasta válido
    folder_name = name_with_owner.replace('/', '-')
    target_path = os.path.join(base_dir, folder_name)
    
    # Verifica existência exata
    exact_match = find_exact_case_match(base_dir, folder_name)
    if exact_match:
        print(f"[SKIP-EXACT] {folder_name} já existe (case exato)")
        skipped_repos_log.append({
            'url': repo_url,
            'name': folder_name,
            'reason': 'EXACT_MATCH',
            'existing_path': exact_match
        })
        successful_repos.append(repo_url)
        return None

    # Conflitos de case-insensitive
    case_conflicts = find_case_insensitive_conflicts(base_dir, folder_name)
    if case_conflicts:
        print(f"[CASE-CONFLICT] {folder_name} vs existente(s): {case_conflicts}")
        skipped_repos_log.append({
            'url': repo_url,
            'name': folder_name,
            'reason': 'CASE_CONFLICT',
            'conflicts': case_conflicts
        })
        return repo_url

    # Lógica de retries e clone
    use_shallow = False
    for attempt in range(1, retries + 1):
        if os.path.exists(target_path):
            print(f"[CLEANUP] Removendo {folder_name} incompleto (tentativa {attempt})")
            if not safe_rmtree(target_path):
                return repo_url
            time.sleep(0.2)
        try:
            cmd = ["git", "clone", repo_url, target_path]
            timeout = 30
            clone_type = "[NORMAL]"
            if use_shallow:
                cmd = ["git", "clone", "--depth", "1", "--single-branch", repo_url, target_path]
                timeout = 180
                clone_type = "[SHALLOW]"

            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            if os.path.exists(os.path.join(target_path, '.git')):
                print(f"[SUCCESS] {clone_type} {folder_name}")
                successful_repos.append(repo_url)
                return None

        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] {folder_name} - tentativa {attempt}/{retries}")
            if attempt == retries:
                return repo_url

        except subprocess.CalledProcessError as e:
            err = e.stderr.decode(errors='ignore')
            if is_path_too_long_error(err) and not use_shallow:
                print(f"[LONGPATH] {folder_name} - erro de caminho longo, retry shallow")
                use_shallow = True
                continue
            print(f"[ERROR] {folder_name} - tentativa {attempt}/{retries}: {err.strip()[:80]}...")
            if attempt == retries:
                return repo_url

        backoff = 2 ** (attempt - 1)
        if backoff > 1:
            print(f"[WAIT] aguardando {backoff}s")
            time.sleep(backoff)

    return repo_url

def clone_chunk_case_sensitive(chunk, chunk_id):
    """Clona um pedaço de repositórios em uma thread"""
    failures = []
    print(f"[THREAD-{chunk_id}] Iniciando {len(chunk)} repositórios")
    for i, repo in enumerate(chunk):
        result = git_clone_case_sensitive(repo)
        if result:
            failures.append(result)
        time.sleep(0.1)
        if (i + 1) % 25 == 0:
            print(f"[THREAD-{chunk_id}] Progresso: {i+1}/{len(chunk)}")
    print(f"[THREAD-{chunk_id}] Finalizado. Falhas: {len(failures)}")
    return failures

def clone_parallel_case_sensitive(repos, workers=4):
    """Clone paralelo com verificação case-sensitive"""
    total = len(repos)
    if total == 0:
        return []
    chunk_size = total // workers
    chunks = []
    for i in range(workers):
        start = i * chunk_size
        end = total if i == workers - 1 else (i + 1) * chunk_size
        chunks.append(repos[start:end])
    print(f"[INFO] Iniciando clonagem paralela em {workers} threads")
    failures = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(clone_chunk_case_sensitive, chunk, idx+1)
                   for idx, chunk in enumerate(chunks)]
        for future in as_completed(futures):
            failures.extend(future.result())
    return failures


def escolher_repos():
    print("Selecione a opção de clonagem:")
    print(" 1) Clonar TODOS os repositórios do CSV")
    print(" 2) Clonar APENAS os repositórios que falharam na última execução")
    escolha = input("Digite 1 ou 2 e pressione Enter: ").strip()
    return escolha

def carregar_repositorios(escolha, csv_path):
    if escolha == "1":
        return load_repos_from_csv(csv_path)
    elif escolha == "2":
        txt_dir = os.path.join("..", "txtFiles")
        if not os.path.exists(txt_dir):
            print("[ERROR] Diretório txtFiles não encontrado.")
            return []
        
        falha_files = [f for f in os.listdir(txt_dir) if f.startswith("failedrepos")]
        if not falha_files:
            print("[INFO] Nenhum arquivo de falhas encontrado em txtFiles.")
            return []
        
        ultimo = max(falha_files)
        caminho = os.path.join(txt_dir, ultimo)
        falhas = []
        
        with open(caminho, "r", encoding="utf-8") as f:
            content = f.read()
            # Procura pela linha que contém URLs (não começa com #)
            for line in content.split('\n'):
                line = line.strip()
                # Ignora linhas de comentário e linhas vazias
                if line and not line.startswith('#'):
                    # Split por ponto e vírgula para separar as URLs
                    urls = line.split(';')
                    for url in urls:
                        url = url.strip()
                        if url.startswith("http"):
                            # Extrai nome do repositório da URL
                            name = url.rstrip("/").split("/")[-1]
                            # Extrai owner/repo para name_with_owner
                            url_parts = url.rstrip("/").split("/")
                            if len(url_parts) >= 2:
                                owner = url_parts[-2]
                                repo_name = url_parts[-1]
                                name_with_owner = f"{owner}/{repo_name}"
                            else:
                                name_with_owner = name
                            
                            falhas.append({
                                "url": url,
                                "name": name,
                                "name_with_owner": name_with_owner,
                                "size_kb": 0
                            })
        
        print(f"[INFO] {len(falhas)} repositórios carregados de {ultimo}")
        return falhas
    else:
        print("[ERROR] Opção inválida.")
        return []

def main(csv_filename="java_maven_repos_detailed.csv"):
    global successful_repos, skipped_repos_log
    successful_repos = []
    skipped_repos_log = []

    configure_git_for_windows()

    base_csv = os.path.join("..", "csvFiles", csv_filename)
    escolha = escolher_repos()
    repos = carregar_repositorios(escolha, base_csv)
    if not repos:
        print("[INFO] Nenhum repositório para clonar. Encerrando.")
        return

    print(f"[INFO] Iniciando clonagem de {len(repos)} repositórios...")
    failures = clone_parallel_case_sensitive(repos, workers=4)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    success_file = f"success_repos_{timestamp}.txt"
    failed_file = f"failedrepos_{timestamp}.txt"
    skip_log_file = f"skip_log_{timestamp}.txt"

    save_urls_to_file(successful_repos, success_file, "Repositórios clonados com sucesso")
    save_urls_to_file(failures, failed_file, "Repositórios que falharam no clone")
    save_skip_log(skipped_repos_log, skip_log_file)

    print("\n" + "=" * 60)
    print("RELATÓRIO FINAL:")
    print(f" Total no CSV: {len(repos)}")
    print(f" Clonados com sucesso: {len(successful_repos)}")
    print(f" Pulados: {len(skipped_repos_log)}")
    print(f" Falharam: {len(failures)}")
    print(f"\nArquivos salvos em '../txtFiles/':")
    print(f" • Sucessos: {success_file}")
    print(f" • Falhas: {failed_file}")
    print(f" • Log de skips: {skip_log_file}")

    return {
        'successful': successful_repos,
        'failed': failures,
        'skipped': skipped_repos_log
    }

if __name__ == "__main__":
    main()
