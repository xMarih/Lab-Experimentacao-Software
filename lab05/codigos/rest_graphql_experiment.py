from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import requests

BASE_DIR = Path(__file__).resolve().parent
LAB_ROOT = BASE_DIR.parent
PROJECT_ROOT = BASE_DIR.parents[1]
RELATORIOS_DIR = LAB_ROOT / "relatorios"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config_token import configurar_token  # type: ignore  # noqa: E402

GITHUB_TOKEN = configurar_token()[0]


def configure_logger(log_file: Path) -> logging.Logger:
    logger = logging.getLogger("lab05.experiment")
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


@dataclass(frozen=True)
class ExperimentConfig:
    owner: str
    repo: str
    trials: int
    results_file: Path = RELATORIOS_DIR / "experiment_results.csv"
    log_file: Path = RELATORIOS_DIR / "experiment.log"


class GitHubExperiment:
    REST_URL_TEMPLATE = "https://api.github.com/repos/{owner}/{repo}"
    GRAPHQL_URL = "https://api.github.com/graphql"

    def __init__(self, token: str, logger: logging.Logger):
        self.logger = logger
        self.session = requests.Session()
        self.token = token

    @property
    def rest_headers(self) -> dict:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    @property
    def graphql_headers(self) -> dict:
        return {
            "Authorization": f"bearer {self.token}",
            "Accept": "application/vnd.github.v4+json",
            "Content-Type": "application/json",
        }

    def measure_rest(self, owner: str, repo: str, save_json: bool = False) -> Tuple[float, int]:
        self.logger.info("Iniciando chamada REST para %s/%s", owner, repo)
        start = time.perf_counter()
        response = self.session.get(
            self.REST_URL_TEMPLATE.format(owner=owner, repo=repo),
            headers=self.rest_headers,
        )
        response.raise_for_status()
        elapsed = time.perf_counter() - start
        self.logger.info("Chamada REST concluida em %.4fs", elapsed)

        if save_json:
            self._persist_payload(response.json(), "rest_response.json")
        return elapsed, len(response.content)

    def measure_graphql(self, owner: str, repo: str, save_json: bool = False) -> Tuple[float, int]:
        self.logger.info("Iniciando chamada GraphQL para %s/%s", owner, repo)
        query = self._build_graphql_query()
        payload = {"query": query, "variables": {"owner": owner, "repo": repo}}

        start = time.perf_counter()
        response = self.session.post(self.GRAPHQL_URL, json=payload, headers=self.graphql_headers)
        response.raise_for_status()
        elapsed = time.perf_counter() - start
        self.logger.info("Chamada GraphQL concluida em %.4fs", elapsed)

        if save_json:
            self._persist_payload(response.json(), "graphql_response.json")
        return elapsed, len(response.content)

    def run(self, config: ExperimentConfig) -> None:
        self.logger.info(
            "Iniciando experimento com %d execucoes para %s/%s",
            config.trials,
            config.owner,
            config.repo,
        )

        config.results_file.parent.mkdir(parents=True, exist_ok=True)
        with config.results_file.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["API_Type", "Trial", "Response_Time", "Response_Size"])

            for trial_index in range(1, config.trials + 1):
                self.logger.info("Execucao %s/%s", trial_index, config.trials)
                save_payload = trial_index == 1

                rest_time, rest_size = self.measure_rest(config.owner, config.repo, save_payload)
                writer.writerow(["REST", trial_index, rest_time, rest_size])

                gql_time, gql_size = self.measure_graphql(config.owner, config.repo, save_payload)
                writer.writerow(["GraphQL", trial_index, gql_time, gql_size])

        self.logger.info("Experimento concluido com sucesso.")
        print(
            f"Experimento concluido ({config.trials} trials). "
            f"Resultados armazenados em '{config.results_file.name}'."
        )

    def _persist_payload(self, data: dict, filename: str) -> None:
        target_dir = LAB_ROOT / "respostas_json"
        target_dir.mkdir(parents=True, exist_ok=True)
        output_path = target_dir / filename
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        self.logger.info("Resposta salva em: %s", output_path)

    @staticmethod
    def _build_graphql_query() -> str:
        return """
        query($owner: String!, $repo: String!) {
          repository(owner: $owner, name: $repo) {
            name
            nameWithOwner
            description
            descriptionHTML
            shortDescriptionHTML(limit: 200)
            homepageUrl
            url
            resourcePath
            sshUrl
            createdAt
            updatedAt
            pushedAt
            visibility
            isPrivate
            diskUsage
            forkCount
            forks(first: 5) {
              totalCount
              nodes { nameWithOwner }
            }
            stargazerCount
            watchers {
              totalCount
            }
            issues {
              totalCount
            }
            pullRequests {
              totalCount
            }
            licenseInfo {
              key
              name
              url
            }
            languages(first: 5) {
              edges {
                size
                node {
                  name
                }
              }
            }
            repositoryTopics(first: 5) {
              nodes {
                topic {
                  name
                }
              }
            }
            defaultBranchRef {
              name
              prefix
            }
            primaryLanguage {
              name
            }
          }
        }
        """.strip()


DEFAULT_OWNER = "octocat"
DEFAULT_REPO = "Hello-World"
DEFAULT_TRIALS = 30


def build_config_from_cli(args: argparse.Namespace) -> ExperimentConfig:
    return ExperimentConfig(
        owner=args.owner,
        repo=args.repo,
        trials=args.trials,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compara performance REST x GraphQL na GitHub API"
    )
    parser.add_argument("--owner", default=DEFAULT_OWNER, help="Usuario ou organizacao alvo")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="Nome do repositorio")
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS, help="Numero de repeticoes")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = build_config_from_cli(args)
    logger = configure_logger(config.log_file)
    experiment = GitHubExperiment(GITHUB_TOKEN, logger)
    experiment.run(config)


if __name__ == "__main__":
    main()
