import requests
import time
import random
from tqdm import tqdm

def get_steam_news(appid, total_news=5000):
    url = "http://api.steampowered.com/ISteamNews/GetNewsForApp/v2"
    all_news = []
    start = 0
    count = 100

    with tqdm(total=total_news, desc=f"Coletando news (appid={appid})", unit="notícia") as pbar:
        while len(all_news) < total_news:
            remaining = total_news - len(all_news)
            num_to_fetch = min(count, remaining)

            params = {
                "appid": appid,
                "format": "json",
                "count": num_to_fetch,
                "start": start
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Erro na requisição: {e}")
                break

            data = response.json()

            if "appnews" in data and "newsitems" in data["appnews"]:
                news = data["appnews"]["newsitems"]
                if not news:
                    print("Nenhuma notícia retornada. Encerrando.")
                    break

                all_news.extend(news)
                pbar.update(len(news))

                if len(news) < count:
                    break  # Fim da paginação

                start += count
            else:
                print("Estrutura inesperada na resposta da API.")
                break

            time.sleep(random.uniform(0.5, 1.5))

    print(f"Total de news coletadas: {len(all_news)}")
    return all_news