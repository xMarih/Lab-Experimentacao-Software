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
        existing_dirs = os.listdir(base_dir)
        for dir_name in existing_dirs:
            if dir_name == repo_name:
                full_path = os.path.join(base_dir, dir_name)
                if os.path.exists(os.path.join(full_path, '.git')):
                    return full_path
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
        existing_dirs = os.listdir(base_dir)
        for dir_name in existing_dirs:
            if dir_name.lower() == repo_name.lower() and dir_name != repo_name:
                conflicts.append(dir_name)
        return conflicts
    except Exception:
        return []

def save_urls_to_file(urls, filename, description):
    """Salva uma lista de URLs em arquivo texto separados por ponto e vírgula na pasta txtFiles"""
    try:
        if not urls:
            print(f"[INFO] Lista vazia para {description}, arquivo não será criado.")
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        base_dir = os.getcwd()
        txt_files_dir = os.path.join(base_dir, '..', 'txtFiles')
        os.makedirs(txt_files_dir, exist_ok=True)
        
        filepath = os.path.join(txt_files_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {description} - {timestamp}\n")
            f.write(f"# Total: {len(urls)}\n")
            f.write("# URLs separadas por ponto e vírgula:\n\n")
            f.write(';'.join(urls))
        
        print(f"{description} ({len(urls)} itens) salvo em '{filepath}'")
        return True
    except Exception as e:
        print(f"[ERROR] Falha ao salvar arquivo {filename}: {e}")
        return False

def is_path_too_long_error(error_message):
    """Detecta se o erro é relacionado a caminho longo no Windows"""
    keywords = ["unable to create file", "filename too long", "file name too long", "path too long"]
    return any(keyword.lower() in error_message.lower() for keyword in keywords)

def configure_git_for_windows():
    """Configura Git para lidar melhor com caminhos longos"""
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
                    'name_with_owner': row['name_with_owner'],
                    'size_kb': int(row['disk_usage_kb']) if row['disk_usage_kb'].isdigit() else 0
                })
        print(f"{len(repos)} repositórios carregados do CSV")
        return repos
    except Exception as e:
        print(f"[ERROR] Falha ao carregar CSV {csv_file_path}: {e}")
        return []

successful_repos = []
skipped_repos_log = []

def git_clone_case_sensitive(repo_info, base_dir="./cloned_repos", retries=3):
    """Clone case-sensitive que detecta e registra conflitos de maiúscula/minúscula"""
    global successful_repos, skipped_repos_log
    
    repo_url = repo_info['url']
    repo_name = repo_info['name']
    size_kb = repo_info['size_kb']
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    target_path = os.path.join(base_dir, repo_name)
    
    exact_match = find_exact_case_match(base_dir, repo_name)
    case_conflicts = find_case_insensitive_conflicts(base_dir, repo_name)
    
    if exact_match:
        print(f"[SKIP-EXACT] {repo_name} já existe com case exato")
        skipped_repos_log.append({
            'url': repo_url,
            'name': repo_name,
            'name_with_owner': repo_info['name_with_owner'],
            'reason': 'EXACT_MATCH',
            'existing_path': exact_match
        })
        successful_repos.append(repo_url)
        return None
    
    if case_conflicts:
        conflicts_str = ', '.join(case_conflicts)
        print(f"[CASE-CONFLICT] {repo_name} vs existente(s): {conflicts_str}")
        skipped_repos_log.append({
            'url': repo_url,
            'name': repo_name,
            'name_with_owner': repo_info['name_with_owner'],
            'reason': 'CASE_CONFLICT',
            'conflicts': case_conflicts
        })
        return repo_url
    
    use_shallow_for_path = False
    
    for attempt in range(1, retries + 1):
        if os.path.exists(target_path):
            print(f"[CLEANUP] Removendo {repo_name} incompleto (tentativa {attempt})")
            if not safe_rmtree(target_path):
                return repo_url
            time.sleep(0.2)
        
        try:
            if size_kb > 50000 or use_shallow_for_path:
                cmd = ["git", "clone", "--depth", "1", "--single-branch", repo_url, target_path]
                timeout = 180
                clone_type = "[SHALLOW]"
            else:
                cmd = ["git", "clone", repo_url, target_path]
                timeout = 30
                clone_type = "[NORMAL]"
            
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, timeout=timeout)
            
            if os.path.exists(os.path.join(target_path, '.git')):
                print(f"[SUCCESS] {clone_type} {repo_name}")
                successful_repos.append(repo_url)
                return None
                
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] {repo_name} - Tentativa {attempt}/{retries}")
            if attempt == retries:
                return repo_url
                
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.decode().strip()
            if is_path_too_long_error(err_msg):
                print(f"[LONGPATH] {repo_name} - Erro de caminho longo, tentando clone shallow")
                use_shallow_for_path = True
                if attempt < retries:
                    continue
            
            print(f"[ERROR] {repo_name} - Tentativa {attempt}/{retries}: {err_msg[:80]}...")
            if attempt == retries:
                return repo_url
        
        if attempt < retries:
            backoff_time = 2 ** (attempt - 1)
            if backoff_time > 1:
                print(f"[WAIT] Aguardando {backoff_time}s...")
                time.sleep(backoff_time)
    
    return repo_url

def clone_chunk_case_sensitive(chunk, chunk_id):
    """Clona chunk com verificação case-sensitive"""
    failures = []
    print(f"[THREAD-{chunk_id}] Iniciando {len(chunk)} repositórios")
    
    for i, repo_info in enumerate(chunk):
        result = git_clone_case_sensitive(repo_info)
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
    chunk_size = total // workers
    failures = []
    chunks = []
    
    for i in range(workers):
        start_idx = i * chunk_size
        end_idx = total if i == workers - 1 else (i + 1) * chunk_size
        chunks.append(repos[start_idx:end_idx])
    
    print(f"Executando com {workers} threads (case-sensitive)")
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(clone_chunk_case_sensitive, chunk, i+1)
                  for i, chunk in enumerate(chunks)]
        
        for future in as_completed(futures):
            failures.extend(future.result())
    
    return failures

def save_skip_log(skipped_log, filename):
    """Salva log detalhado dos repositórios que foram pulados na pasta txtFiles"""
    try:
        if not skipped_log:
            return False
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        base_dir = os.getcwd()
        txt_files_dir = os.path.join(base_dir, '..', 'txtFiles')
        os.makedirs(txt_files_dir, exist_ok=True)
        
        filepath = os.path.join(txt_files_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Log de Repositórios Pulados - {timestamp}\n")
            f.write(f"# Total: {len(skipped_log)}\n\n")
            
            for entry in skipped_log:
                f.write(f"URL: {entry['url']}\n")
                f.write(f"Nome: {entry['name']}\n")
                f.write(f"Nome Completo: {entry['name_with_owner']}\n")
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

def main(csv_file_path="java_maven_repos_detailed.csv"):
    """Função principal com verificação case-sensitive"""
    global successful_repos, skipped_repos_log
    successful_repos = []
    skipped_repos_log = []
    
    try:
        configure_git_for_windows()
        print("Se estiver tendo erros de unable to create file... pode ser que o seu windows não esteja configurado para arquivos com altos caracteres: rode o comando dentro de Enable-LongPaths.ps1")

        repos = load_repos_from_csv(csv_file_path)
        if not repos:
            print("Nenhum repositório encontrado no CSV")
            return {}

        print(f"{len(repos)} encontrados no CSV\n")

        failed_repos = clone_parallel_case_sensitive(repos, workers=4)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        success_repos_file = f"success_repos_{timestamp}.txt"
        failed_repos_file = f"failed_repos_{timestamp}.txt"
        skip_log_file = f"skip_log_{timestamp}.txt"
        
        save_urls_to_file(successful_repos, success_repos_file, "Repositórios clonados com sucesso")
        save_urls_to_file(failed_repos, failed_repos_file, "Repositórios que falharam no clone")
        save_skip_log(skipped_repos_log, skip_log_file)

        print(f"\n{'='*60}")
        print(f"RELATÓRIO FINAL (CASE-SENSITIVE):")
        print(f"Total no CSV: {len(repos)}")
        print(f"Clonados com sucesso: {len(successful_repos)}")
        print(f"Pulados: {len(skipped_repos_log)}")
        print(f"Falharam: {len(failed_repos)}")

        case_conflicts = [entry for entry in skipped_repos_log
                         if entry['reason'] == 'CASE_CONFLICT']
        if case_conflicts:
            print(f"\nConflitos de case detectados: {len(case_conflicts)}")
            for conflict in case_conflicts[:5]:
                print(f" • {conflict['name']} vs {', '.join(conflict['conflicts'])}")

        print(f"\nArquivos de log salvos na pasta txtFiles (fora do diretório atual):")
        print(f" • Sucessos: {success_repos_file}")
        print(f" • Falhas: {failed_repos_file}")
        print(f" • Log de skips: {skip_log_file}")

        return {
            'successful_repos': successful_repos,
            'failed_repos': failed_repos,
            'skipped_repos': skipped_repos_log
        }

    except Exception as e:
        print(f"Erro na execução: {e}")
        return {}

if __name__ == "__main__":
    # TODO adicionar um fallback melhor de erro, ler o arquivo de repositorios falhados depois e colocar para rodar novamente, fazer isso enquanto nao tiver apenas 20% dos arquivos falhados
    csv_path = os.path.join('..', 'csvFiles', 'java_maven_repos_detailed.csv')
    results = main(csv_path)
