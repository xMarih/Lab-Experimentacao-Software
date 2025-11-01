import requests
import time
import random
from tqdm import tqdm

def get_steam_reviews(app_id, total_reviews):
    url = f"https://store.steampowered.com/appreviews/{app_id}"
    cursor = "*"
    all_reviews = []
    count_per_request = 100

    with tqdm(total=total_reviews, desc="Coletando reviews", unit="review") as pbar:
        while len(all_reviews) < total_reviews:
            remaining = total_reviews - len(all_reviews)
            num_to_fetch = min(count_per_request, remaining)

            params = {
                "json": 1,
                "num_per_page": num_to_fetch,
                "cursor": cursor,
                "language": "english",
                "purchase_type": "all",
                "filter": "all",
                "day_range": "365",
                "review_type": "all"
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Erro na requisição: {e}")
                break

            data = response.json()

            reviews = data.get("reviews", [])
            if not reviews or "cursor" not in data:
                print("Sem mais reviews ou erro na resposta.")
                break

            all_reviews.extend(reviews)
            cursor = data["cursor"]

            pbar.update(len(reviews))

            sleep_time = random.uniform(0.5, 1.5)
            time.sleep(sleep_time)

        print(f"Coletados {len(all_reviews)} reviews no total.")
        
    return all_reviews