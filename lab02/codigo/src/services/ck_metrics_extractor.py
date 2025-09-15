import os
import shutil
import subprocess
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Protocol
from abc import abstractmethod
import json
from git import Repo


class MetricsExtractor(Protocol):
    """Interface para extrator de métricas."""
    
    @abstractmethod
    def extract(self, repo_path: str) -> Dict[str, Any]:
        """
        Extrai métricas do repositório.
        
        Args:
            repo_path (str): Caminho para o repositório
            
        Returns:
            Dict[str, Any]: Dicionário com as métricas extraídas
        """
        pass


class MetricsStorage(Protocol):
    """Interface para armazenamento de métricas."""
    
    @abstractmethod
    def save(self, metrics: Dict[str, Any], filename: str) -> None:
        """
        Salva as métricas em arquivo.
        
        Args:
            metrics (Dict[str, Any]): Métricas a salvar
            filename (str): Nome do arquivo para salvar
        """
        pass


class ProcessMetricsExtractor:
    """Extrai métricas de processo do repositório."""
    
    def extract(self, repo_path: str) -> Dict[str, Any]:
        """
        Extrai métricas de processo: popularidade, tamanho, atividade e maturidade.
        
        Args:
            repo_path (str): Caminho para o repositório Git local
            
        Returns:
            Dict[str, Any]: Dicionário contendo métricas de processo
        """
        try:
            repo = Repo(repo_path)
            
            metrics = {
                'repository_path': repo_path,
                'repository_name': os.path.basename(repo_path)
            }
            
            metrics['popularity_stars'] = self._get_github_stars(repo_path)
            metrics['activity_releases'] = len(list(repo.tags))
            
            try:
                commits = list(repo.iter_commits())
                if commits:
                    first_commit = commits[-1]
                    creation_date = datetime.fromtimestamp(first_commit.committed_date)
                    age_years = (datetime.now() - creation_date).days / 365.25
                    metrics['maturity_years'] = round(age_years, 2)
                else:
                    metrics['maturity_years'] = 0
            except:
                metrics['maturity_years'] = 0
            
            loc_metrics = self._count_lines_of_code(repo_path)
            metrics.update(loc_metrics)
            
            return metrics
            
        except Exception as e:
            print(f"Erro ao extrair métricas de processo: {e}")
            return self._get_default_process_metrics(repo_path)
    
    def _get_github_stars(self, repo_path: str) -> int:
        """
        Placeholder para obter stars do GitHub via API.
        
        Args:
            repo_path (str): Caminho do repositório
            
        Returns:
            int: Número de estrelas (sempre 0 nesta implementação)
        """
        return 0
    
    def _count_lines_of_code(self, repo_path: str) -> Dict[str, int]:
        """
        Conta linhas de código Java no repositório.
        
        Args:
            repo_path (str): Caminho do repositório
            
        Returns:
            Dict[str, int]: Dicionário com contadores de linhas
        """
        java_files = list(Path(repo_path).rglob("*.java"))
        
        total_loc = 0
        total_comment_lines = 0
        
        for java_file in java_files:
            try:
                with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                loc = 0
                comment_lines = 0
                in_block_comment = False
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if '/*' in line:
                        in_block_comment = True
                        comment_lines += 1
                    elif '*/' in line:
                        in_block_comment = False
                        comment_lines += 1
                    elif in_block_comment:
                        comment_lines += 1
                    elif line.startswith('//'):
                        comment_lines += 1
                    else:
                        loc += 1
                
                total_loc += loc
                total_comment_lines += comment_lines
                
            except Exception as e:
                print(f"Aviso: Erro ao processar arquivo {java_file}: {e}")
                continue
        
        return {
            'size_loc': total_loc,
            'size_comments_loc': total_comment_lines
        }
    
    def _get_default_process_metrics(self, repo_path: str) -> Dict[str, Any]:
        """
        Retorna métricas padrão em caso de erro.
        
        Args:
            repo_path (str): Caminho do repositório
            
        Returns:
            Dict[str, Any]: Métricas com valores padrão (zeros)
        """
        return {
            'repository_path': repo_path,
            'repository_name': os.path.basename(repo_path),
            'popularity_stars': 0,
            'activity_releases': 0,
            'maturity_years': 0,
            'size_loc': 0,
            'size_comments_loc': 0
        }


class QualityMetricsExtractor:
    """Extrai métricas de qualidade CK do repositório com detecção robusta de Java."""
    
    def __init__(self, ck_jar_path: str):
        """
        Inicializa o extrator de métricas CK.
        
        Args:
            ck_jar_path (str): Caminho para o arquivo JAR da ferramenta CK
            
        Raises:
            FileNotFoundError: Se o JAR não for encontrado
            EnvironmentError: Se Java não for encontrado
        """
        self.ck_jar_path = os.path.abspath(ck_jar_path)
        self.java_executable = self._find_java_executable()
        
        if not os.path.exists(self.ck_jar_path):
            raise FileNotFoundError(f"CK JAR não encontrado: {self.ck_jar_path}")
        
        if not self.java_executable:
            raise EnvironmentError("Java não encontrado. Instale Java e configure no PATH ou JAVA_HOME")
    
    def _find_java_executable(self) -> Optional[str]:
        """
        Tenta encontrar o executável Java de várias formas.
        
        Returns:
            Optional[str]: Caminho para executável Java ou None se não encontrado
        """
        print("[+] Procurando executável Java...")
        
        java_path = shutil.which('java')
        if java_path and self._test_java(java_path):
            print(f"[+] Java encontrado via PATH: {java_path}")
            return java_path
        
        java_home = os.environ.get('JAVA_HOME')
        if java_home:
            java_exe = 'java.exe' if os.name == 'nt' else 'java'
            java_path = os.path.join(java_home, 'bin', java_exe)
            if os.path.exists(java_path) and self._test_java(java_path):
                print(f"[+] Java encontrado via JAVA_HOME: {java_path}")
                return java_path
        
        if os.name == 'nt':
            common_paths = [
                r"C:\Program Files\Java\jdk-17\bin\java.exe",
                r"C:\Program Files\Java\jre-17\bin\java.exe",
                r"C:\Program Files\Oracle\Java\jdk-17\bin\java.exe",
                r"C:\Program Files\Eclipse Adoptium\jdk-17.0.12.8-hotspot\bin\java.exe",
                r"C:\Program Files\Amazon Corretto\jdk17.0.12_8\bin\java.exe",
                r"C:\Program Files\OpenJDK\jdk-17\bin\java.exe",
                r"C:\Program Files\Microsoft\jdk-17.0.12.8-hotspot\bin\java.exe",
                r"C:\Program Files (x86)\Java\jdk-17\bin\java.exe",
                r"C:\Program Files (x86)\Eclipse Adoptium\jdk-17.0.12.8-hotspot\bin\java.exe",
            ]
            
            for version in ['17', '11', '8']:
                common_paths.extend([
                    rf"C:\Program Files\Java\jdk-{version}\bin\java.exe",
                    rf"C:\Program Files\Java\jre-{version}\bin\java.exe",
                    rf"C:\Program Files\Oracle\Java\jdk-{version}\bin\java.exe",
                ])
            
            for java_path in common_paths:
                if os.path.exists(java_path) and self._test_java(java_path):
                    print(f"[+] Java encontrado em local comum: {java_path}")
                    return java_path
        
        if os.name == 'nt':
            java_path = self._find_java_in_registry()
            if java_path and self._test_java(java_path):
                print(f"[+] Java encontrado via registro: {java_path}")
                return java_path
        
        if os.name == 'nt':
            java_path = self._find_java_recursive()
            if java_path and self._test_java(java_path):
                print(f"[+] Java encontrado via busca recursiva: {java_path}")
                return java_path
        
        print("[!] Java não encontrado automaticamente.")
        print("    Soluções:")
        print("    1. Instale Java JDK 8, 11 ou 17")
        print("    2. Configure JAVA_HOME")
        print("    3. Adicione Java ao PATH")
        return None
    
    def _test_java(self, java_path: str) -> bool:
        """
        Testa se o executável Java funciona.
        
        Args:
            java_path (str): Caminho para executável Java
            
        Returns:
            bool: True se Java funciona, False caso contrário
        """
        try:
            result = subprocess.run([java_path, '-version'],
                                  capture_output=True,
                                  text=True,
                                  timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def _find_java_in_registry(self) -> Optional[str]:
        """
        Tenta encontrar Java no registro do Windows.
        
        Returns:
            Optional[str]: Caminho para Java ou None se não encontrado
        """
        try:
            import winreg
            
            registry_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\Java Runtime Environment"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\Java Development Kit"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\JDK"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Eclipse Adoptium\JDK"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\JDK"),
            ]
            
            for hive, key_path in registry_keys:
                try:
                    with winreg.OpenKey(hive, key_path) as key:
                        current_version, _ = winreg.QueryValueEx(key, "CurrentVersion")
                        with winreg.OpenKey(key, current_version) as version_key:
                            java_home, _ = winreg.QueryValueEx(version_key, "JavaHome")
                            java_exe = os.path.join(java_home, "bin", "java.exe")
                            if os.path.exists(java_exe):
                                return java_exe
                except:
                    continue
        except ImportError:
            pass
        except:
            pass
        
        return None
    
    def _find_java_recursive(self) -> Optional[str]:
        """
        Busca recursiva por java.exe em Program Files.
        
        Returns:
            Optional[str]: Caminho para java.exe ou None se não encontrado
        """
        try:
            search_paths = [
                r"C:\Program Files",
                r"C:\Program Files (x86)"
            ]
            
            for base_path in search_paths:
                if not os.path.exists(base_path):
                    continue
                    
                for root, dirs, files in os.walk(base_path):
                    if 'java.exe' in files:
                        java_path = os.path.join(root, 'java.exe')
                        if 'bin' in root.lower() and ('java' in root.lower() or 'jdk' in root.lower()):
                            return java_path
        except:
            pass
        
        return None
    
    def extract(self, repo_path: str) -> Dict[str, Any]:
        """
        Extrai métricas CK: CBO, DIT, LCOM.
        
        Args:
            repo_path (str): Caminho para o repositório
            
        Returns:
            Dict[str, Any]: Métricas de qualidade extraídas ou valores padrão em caso de erro
        """
        try:
            ck_output_dir = self._run_ck_tool(repo_path)
            class_csv_path = os.path.join(ck_output_dir, 'class.csv')
            
            if not os.path.exists(class_csv_path):
                print(f"Aviso: class.csv não encontrado em {ck_output_dir}")
                if os.path.exists(ck_output_dir):
                    files = os.listdir(ck_output_dir)
                    print(f"Arquivos disponíveis: {files}")
                return self._get_default_quality_metrics()
            
            return self._extract_ck_metrics_from_csv(class_csv_path)
            
        except Exception as e:
            print(f"Erro ao extrair métricas de qualidade: {e}")
            return self._get_default_quality_metrics()
    
    def _run_ck_tool(self, repo_path: str) -> str:
        """
        Executa a ferramenta CK com parâmetros corrigidos.
        
        Args:
            repo_path (str): Caminho do repositório a ser analisado
            
        Returns:
            str: Caminho do diretório onde os resultados foram salvos
            
        Raises:
            Exception: Se a execução da ferramenta CK falhar
        """
        repo_path = os.path.abspath(repo_path)
        ck_output_dir = os.path.abspath(os.path.join('temp_ck_output', os.path.basename(repo_path)))
        
        if os.path.exists(ck_output_dir):
            shutil.rmtree(ck_output_dir)
        os.makedirs(ck_output_dir, exist_ok=True)
        
        java_files = self._find_java_files(repo_path)
        print(f"[DEBUG] Arquivos .java encontrados: {len(java_files)}")
        if len(java_files) > 0:
            print(f"[DEBUG] Exemplos: {java_files[:3]}")
        
        print(f"[DEBUG] Java executável: {self.java_executable}")
        print(f"[DEBUG] JAR path: {self.ck_jar_path}")
        print(f"[DEBUG] Repo path: {repo_path}")
        print(f"[DEBUG] Output dir: {ck_output_dir}")
        
        cmd = [
            self.java_executable,
            '-jar', self.ck_jar_path,
            repo_path,
            'false',
            '0',
            'false',
            ck_output_dir + os.sep
        ]
        
        print(f"[+] Executando CK Tool...")
        print(f"[DEBUG] Comando: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            print(f"[+] CK Tool executado com sucesso")
            if result.stdout.strip():
                print(f"[+] STDOUT: {result.stdout}")
            if result.stderr.strip():
                print(f"[+] STDERR: {result.stderr}")
            
            files_generated = os.listdir(ck_output_dir) if os.path.exists(ck_output_dir) else []
            print(f"[DEBUG] Arquivos gerados: {files_generated}")
            
            if 'class.csv' in files_generated:
                class_csv_size = os.path.getsize(os.path.join(ck_output_dir, 'class.csv'))
                print(f"[+] class.csv gerado com {class_csv_size} bytes")
                
        except subprocess.TimeoutExpired:
            raise Exception("CK Tool excedeu tempo limite de 5 minutos")
        except subprocess.CalledProcessError as e:
            error_msg = f"CK Tool falhou com código {e.returncode}"
            if e.stderr:
                error_msg += f"\nSTDERR: {e.stderr}"
            if e.stdout:
                error_msg += f"\nSTDOUT: {e.stdout}"
            raise Exception(error_msg)
        
        return ck_output_dir
    
    def _find_java_files(self, repo_path: str) -> List[str]:
        """
        Encontra todos os arquivos .java no repositório.
        
        Args:
            repo_path (str): Caminho do repositório
            
        Returns:
            List[str]: Lista de caminhos para arquivos Java encontrados
        """
        java_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))
        return java_files
    
    def _extract_ck_metrics_from_csv(self, class_csv_path: str) -> Dict[str, Any]:
        """
        Extrai métricas CBO, DIT e LCOM do CSV gerado pela ferramenta CK.
        
        Args:
            class_csv_path (str): Caminho para o arquivo class.csv
            
        Returns:
            Dict[str, Any]: Métricas extraídas com estatísticas (média, max, min, std)
        """
        try:
            df_class = pd.read_csv(class_csv_path)
            print(f"[+] Carregadas {len(df_class)} classes do CSV")
            print(f"[+] Colunas disponíveis: {list(df_class.columns)}")
            
            metrics = {}
            for metric in ['cbo', 'dit', 'lcom']:
                if metric in df_class.columns:
                    values = df_class[metric].dropna()
                    if len(values) > 0:
                        metrics[f'quality_{metric}_mean'] = round(values.mean(), 2)
                        metrics[f'quality_{metric}_max'] = round(values.max(), 2)
                        metrics[f'quality_{metric}_min'] = round(values.min(), 2)
                        metrics[f'quality_{metric}_std'] = round(values.std(), 2)
                        print(f"[+] {metric.upper()}: min={metrics[f'quality_{metric}_min']}, "
                              f"mean={metrics[f'quality_{metric}_mean']}, "
                              f"max={metrics[f'quality_{metric}_max']}")
                    else:
                        metrics[f'quality_{metric}_mean'] = 0
                        metrics[f'quality_{metric}_max'] = 0
                        metrics[f'quality_{metric}_min'] = 0
                        metrics[f'quality_{metric}_std'] = 0
                else:
                    print(f"[!] Métrica {metric} não encontrada no CSV")
                    metrics[f'quality_{metric}_mean'] = 0
                    metrics[f'quality_{metric}_max'] = 0
                    metrics[f'quality_{metric}_min'] = 0
                    metrics[f'quality_{metric}_std'] = 0
            
            metrics['total_classes_analyzed'] = len(df_class)
            return metrics
            
        except Exception as e:
            print(f"Erro ao processar CSV: {e}")
            return self._get_default_quality_metrics()
    
    def _get_default_quality_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas de qualidade padrão em caso de erro.
        
        Returns:
            Dict[str, Any]: Métricas com valores padrão (zeros)
        """
        return {
            'quality_cbo_mean': 0, 'quality_cbo_max': 0, 'quality_cbo_min': 0, 'quality_cbo_std': 0,
            'quality_dit_mean': 0, 'quality_dit_max': 0, 'quality_dit_min': 0, 'quality_dit_std': 0,
            'quality_lcom_mean': 0, 'quality_lcom_max': 0, 'quality_lcom_min': 0, 'quality_lcom_std': 0,
            'total_classes_analyzed': 0
        }


class CSVMetricsStorage:
    """Armazena métricas em formato CSV."""
    
    def __init__(self, output_dir: str = 'ck_metrics'):
        """
        Inicializa o armazenador de métricas.
        
        Args:
            output_dir (str): Diretório onde salvar os arquivos CSV
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save(self, metrics: Dict[str, Any], filename: str) -> None:
        """
        Salva métricas em arquivo CSV.
        
        Args:
            metrics (Dict[str, Any]): Métricas a serem salvas
            filename (str): Nome do arquivo CSV
        """
        try:
            df = pd.DataFrame([metrics])
            output_path = self.output_dir / filename
            df.to_csv(output_path, index=False, encoding='utf-8')
            print(f"[+] Métricas salvas em {output_path}")
            
            print(f"[+] Resumo das métricas:")
            print(f"    - LOC: {metrics.get('size_loc', 0)}")
            print(f"    - Classes analisadas: {metrics.get('total_classes_analyzed', 0)}")
            print(f"    - CBO médio: {metrics.get('quality_cbo_mean', 0)}")
            print(f"    - DIT médio: {metrics.get('quality_dit_mean', 0)}")
            print(f"    - LCOM médio: {metrics.get('quality_lcom_mean', 0)}")
            
        except Exception as e:
            print(f"Erro ao salvar métricas: {e}")


class RepositoryMetricsAnalyzer:
    """Classe principal que orquestra a extração de métricas."""
    
    def __init__(self,
                 process_extractor: ProcessMetricsExtractor,
                 quality_extractor: QualityMetricsExtractor,
                 storage: CSVMetricsStorage):
        """
        Inicializa o analisador de métricas.
        
        Args:
            process_extractor: Extrator de métricas de processo
            quality_extractor: Extrator de métricas de qualidade
            storage: Sistema de armazenamento
        """
        self.process_extractor = process_extractor
        self.quality_extractor = quality_extractor
        self.storage = storage
    
    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """
        Analisa um repositório e extrai todas as métricas especificadas.
        
        Args:
            repo_path (str): Caminho para o repositório
            
        Returns:
            Dict[str, Any]: Todas as métricas combinadas
            
        Raises:
            FileNotFoundError: Se repositório não for encontrado
        """
        if not os.path.exists(repo_path):
            raise FileNotFoundError(f"Repositório não encontrado: {repo_path}")
        
        print(f"\n{'='*60}")
        print(f"[+] Analisando repositório: {repo_path}")
        print(f"{'='*60}")
        
        print(f"\n[+] Extraindo métricas de processo...")
        process_metrics = self.process_extractor.extract(repo_path)
        
        print(f"\n[+] Extraindo métricas de qualidade...")
        quality_metrics = self.quality_extractor.extract(repo_path)
        
        all_metrics = {
            **process_metrics,
            **quality_metrics,
            'analysis_timestamp': datetime.now().isoformat(),
            'java_version': self._get_java_version(self.quality_extractor.java_executable)
        }
        
        repo_name = os.path.basename(repo_path)
        filename = f"metrics_{repo_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.storage.save(all_metrics, filename)
        
        return all_metrics
    
    def _get_java_version(self, java_executable: str) -> str:
        """
        Obtém a versão do Java usado.
        
        Args:
            java_executable (str): Caminho do executável Java
            
        Returns:
            str: Versão do Java ou "Desconhecida"
        """
        try:
            result = subprocess.run([java_executable, '-version'],
                                  capture_output=True, text=True, timeout=5)
            if result.stderr:
                version_line = result.stderr.split('\n')[0]
                return version_line.strip()
            return "Desconhecida"
        except:
            return "Desconhecida"


def setup_ck_tool():
    """
    Verifica se a ferramenta CK está disponível.
    
    Returns:
        str: Caminho para o arquivo JAR da ferramenta CK
        
    Raises:
        SystemExit: Se JAR não for encontrado
    """
    script_dir = Path(__file__).parent
    ck_jar_path = script_dir / "ck" / "target" / "ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar"
    
    print(f"[DEBUG] Procurando JAR em: {ck_jar_path}")
    print(f"[DEBUG] Diretório do script: {script_dir}")
    
    if not ck_jar_path.exists():
        print(f"Erro: {ck_jar_path} não encontrado.")
        print("Estrutura atual esperada:")
        print(f"  {script_dir}/ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar")
        
        if (script_dir / "ck").exists():
            print(f"Conteúdo de ck/: {list((script_dir / 'ck').iterdir())}")
            if (script_dir / "ck" / "target").exists():
                print(f"Conteúdo de ck/target/: {list((script_dir / 'ck' / 'target').iterdir())}")
        
        print("\nVerifique se:")
        print("1. O diretório 'ck' está na mesma pasta do script")
        print("2. A ferramenta CK foi compilada corretamente")
        print("3. Execute os seguintes comandos na pasta 'ck':")
        print("   cd ck")
        print("   mvn clean package")
        sys.exit(1)
    
    return str(ck_jar_path)


def analyze_single_repository():
    """
    Analisa um único repositório da pasta cloned_repos.
    
    Returns:
        Dict[str, Any]: Métricas extraídas do repositório
    """
    script_dir = Path(__file__).parent
    cloned_repos_dir = script_dir / "cloned_repos"
    
    if not cloned_repos_dir.exists():
        print(f"Erro: Diretório {cloned_repos_dir} não encontrado.")
        sys.exit(1)
    
    repos = [d.name for d in cloned_repos_dir.iterdir()
             if d.is_dir() and not d.name.startswith('.')]
    
    if not repos:
        print(f"Nenhum repositório encontrado em {cloned_repos_dir}")
        sys.exit(1)
    
    selected_repo = repos[0]
    repo_path = cloned_repos_dir / selected_repo
    
    print(f"Repositórios disponíveis: {repos}")
    print(f"Selecionado para análise: {selected_repo}")
    
    ck_jar_path = setup_ck_tool()
    print(f"[+] Usando CK JAR: {ck_jar_path}")
    
    process_extractor = ProcessMetricsExtractor()
    quality_extractor = QualityMetricsExtractor(ck_jar_path)
    storage = CSVMetricsStorage(script_dir / 'ck_metrics')
    
    analyzer = RepositoryMetricsAnalyzer(
        process_extractor=process_extractor,
        quality_extractor=quality_extractor,
        storage=storage
    )
    
    try:
        metrics = analyzer.analyze_repository(str(repo_path))
        print(f"\n{'='*60}")
        print("[+] Análise concluída com sucesso!")
        print(f"{'='*60}")
        return metrics
    except Exception as e:
        print(f"Erro durante análise: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def analyze_all_repositories():
    """
    Analisa todos os repositórios da pasta cloned_repos.
    
    Returns:
        List[Dict[str, Any]]: Lista de métricas de todos os repositórios processados
    """
    script_dir = Path(__file__).parent
    cloned_repos_dir = script_dir / "cloned_repos"
    
    if not cloned_repos_dir.exists():
        print(f"Erro: Diretório {cloned_repos_dir} não encontrado.")
        sys.exit(1)
    
    repos = [d.name for d in cloned_repos_dir.iterdir()
             if d.is_dir() and not d.name.startswith('.')]
    
    if not repos:
        print(f"Nenhum repositório encontrado em {cloned_repos_dir}")
        sys.exit(1)
    
    print(f"Encontrados {len(repos)} repositórios para análise:")
    for i, repo in enumerate(repos, 1):
        print(f"  {i}. {repo}")
    
    ck_jar_path = setup_ck_tool()
    
    process_extractor = ProcessMetricsExtractor()
    quality_extractor = QualityMetricsExtractor(ck_jar_path)
    storage = CSVMetricsStorage(script_dir / 'ck_metrics')
    
    analyzer = RepositoryMetricsAnalyzer(
        process_extractor=process_extractor,
        quality_extractor=quality_extractor,
        storage=storage
    )
    
    results = []
    for i, repo_name in enumerate(repos, 1):
        try:
            print(f"\n[{i}/{len(repos)}] Processando: {repo_name}")
            repo_path = cloned_repos_dir / repo_name
            metrics = analyzer.analyze_repository(str(repo_path))
            results.append(metrics)
        except Exception as e:
            print(f"Erro ao processar {repo_name}: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"[+] Análise de {len(results)}/{len(repos)} repositórios concluída!")
    print(f"{'='*60}")
    
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("    REPOSITORY METRICS ANALYZER")
    print("    Baseado em métricas CK e processo de desenvolvimento")
    print("=" * 60)
    print("Dependências necessárias:")
    print("  pip install gitpython pandas")
    print()
    
    print("Escolha o modo:")
    print("1. Analisar um repositório")
    print("2. Analisar todos os repositórios")
    choice = input("Opção (1 ou 2): ").strip()
    
    if choice == "2":
        analyze_all_repositories()
    else:
        analyze_single_repository()
