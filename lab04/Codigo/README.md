# Starting project

* First step

prepare your computer running the bash bellow

```bash
docker pull mongo:latest
docker-compose up -d
```

To connect and view the mongoDB database on Visual Studio use the plugin *MongoDB for VS Code*

install npm and nestjs

```bash
npm i @nestjs/cli
```

run the search game
```bash
npm run sync-games
npm run sync-news
```

intall python dependencies - Codigo\requirements.txt
```bash
pip install -r requirements.txt
```

run search reviews - Codigo\steam-review
```bash
python main_review.py
```

run reviews process and add sentiment + topic - Codigo\topics_lda_reviews
```bash
python main_topics.py
```

run import metrics to MongoDB - Codigo\STEAMDB\import_all_csv_to_mongo.py
```bash
python import_all_csv_to_mongo.py
```