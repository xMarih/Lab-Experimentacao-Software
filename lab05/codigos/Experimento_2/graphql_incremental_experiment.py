from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Dict, Iterable, Tuple

import requests

BASE_DIR = Path(__file__).resolve().parent
LAB_ROOT = BASE_DIR.parents[1]
PROJECT_ROOT = BASE_DIR.parents[2]
RELATORIOS_DIR = LAB_ROOT / "relatorios" / "Experimento_2"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config_token import configurar_token  # type: ignore  # noqa: E402

GITHUB_TOKEN = configurar_token()[0]


def configure_logger(log_file: Path) -> logging.Logger:
    logger = logging.getLogger("lab05.experimento_2")
    if logger.handlers:
        return logger

    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console_handler)

    return logger


def _normalize_block(block: str) -> str:
    return " ".join(dedent(block).split())


LEVEL_DEFINITIONS: Dict[str, str] = {
    "1campos": _normalize_block(
        """
        name
        """
    ),
    "2campos": _normalize_block(
        """
        name
        createdAt
        """
    ),
    "3campos": _normalize_block(
        """
        name
        createdAt
        updatedAt
        """
    ),
    "4campos": _normalize_block(
        """
        name
        createdAt
        updatedAt
        stargazerCount
        """
    ),
    "5campos": _normalize_block(
        """
        name
        createdAt
        updatedAt
        stargazerCount
        forkCount
        """
    ),
    "6campos": _normalize_block(
        """
        name
        createdAt
        updatedAt
        stargazerCount
        forkCount
        watchers { totalCount }
        """
    ),
    "7campos": _normalize_block(
        """
        name
        createdAt
        updatedAt
        stargazerCount
        forkCount
        watchers { totalCount }
        issues { totalCount }
        """
    ),
    "8campos": _normalize_block(
        """
        name
        createdAt
        updatedAt
        stargazerCount
        forkCount
        watchers { totalCount }
        issues { totalCount }
        pullRequests { totalCount }
        """
    ),
    "9campos": _normalize_block(
        """
        name
        createdAt
        updatedAt
        stargazerCount
        forkCount
        watchers { totalCount }
        issues { totalCount }
        pullRequests { totalCount }
        languages(first: 5) { edges { size node { name } } }
        """
    ),
    "10campos": _normalize_block(
        """
        name
        createdAt
        updatedAt
        stargazerCount
        forkCount
        watchers { totalCount }
        issues { totalCount }
        pullRequests { totalCount }
        languages(first: 5) { edges { size node { name } } }
        repositoryTopics(first: 5) { nodes { topic { name } } }
        """
    ),
}


@dataclass(frozen=True)
class IncrementalConfig:
    owner: str
    repo: str
    trials: int
    results_file: Path = RELATORIOS_DIR / "experiment_graphql_incremental.csv"
    log_file: Path = RELATORIOS_DIR / "experiment_incremental.log"


class IncrementalExperiment:
    GRAPHQL_URL = "https://api.github.com/graphql"

    def __init__(self, token: str, fields_map: Dict[str, str], logger: logging.Logger):
        self.session = requests.Session()
        self.token = token
        self.fields_map = fields_map
        self.logger = logger

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"bearer {self.token}",
            "Accept": "application/vnd.github.v4+json",
            "Content-Type": "application/json",
        }

    def execute_trial(
        self,
        owner: str,
        repo: str,
        level_name: str,
        fields: str,
        save_json: bool,
    ) -> Tuple[float, int]:
        self.logger.info("Iniciando chamada GraphQL (%s)", level_name)
        query = (
            "query($owner: String!, $repo: String!) {"
            " repository(owner: $owner, name: $repo) {"
            f" {fields} "
            "} }"
        )
        payload = {"query": query, "variables": {"owner": owner, "repo": repo}}

        start = time.perf_counter()
        response = self.session.post(self.GRAPHQL_URL, json=payload, headers=self.headers)
        response.raise_for_status()
        elapsed = time.perf_counter() - start
        size = len(response.content)

        if save_json:
            self._persist_payload(response.json(), f"graphql_response_{level_name}.json")

        self.logger.info(
            "%s - Tempo: %.4fs - Tamanho: %d bytes",
            level_name,
            elapsed,
            size,
        )
        return elapsed, size

    def run(self, config: IncrementalConfig) -> None:
        self.logger.info(
            "Iniciando experimento incremental com %d execucoes por nivel.",
            config.trials,
        )

        config.results_file.parent.mkdir(parents=True, exist_ok=True)
        with config.results_file.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["Trial_Name", "Fields_Count", "Trial", "Response_Time", "Response_Size"])

            for level_name, fields in self.fields_map.items():
                for trial_index in range(1, config.trials + 1):
                    self.logger.info("Trial %d/%d - Campos: %s", trial_index, config.trials, level_name)
                    save_payload = trial_index == 1
                    elapsed, size = self.execute_trial(
                        config.owner,
                        config.repo,
                        level_name,
                        fields,
                        save_payload,
                    )
                    writer.writerow([level_name, len(fields.split()), trial_index, elapsed, size])

        self.logger.info("Experimento incremental concluido.")

    def _persist_payload(self, data: dict, filename: str) -> None:
        target_dir = LAB_ROOT / "Experimento_2" / "respostas_incremental"
        target_dir.mkdir(parents=True, exist_ok=True)
        output_path = target_dir / filename
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        self.logger.info("Resposta salva em: %s", output_path)


DEFAULT_OWNER = "octocat"
DEFAULT_REPO = "Hello-World"
DEFAULT_TRIALS = 30


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa experimento incremental para a API GraphQL do GitHub")
    parser.add_argument("--owner", default=DEFAULT_OWNER)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = IncrementalConfig(owner=args.owner, repo=args.repo, trials=args.trials)
    logger = configure_logger(config.log_file)
    experiment = IncrementalExperiment(GITHUB_TOKEN, LEVEL_DEFINITIONS, logger)
    experiment.run(config)


if __name__ == "__main__":
    main()
