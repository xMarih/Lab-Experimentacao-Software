
# SteamDB Importer

Este projeto contém um conjunto de arquivos `.csv` com dados relacionados ao jogo Counter-Strike 2 (AppID 730), bem como um script `.bat` que automatiza a importação dessas tabelas para um banco de dados MongoDB rodando em Docker.

---

## 📂 Estrutura da pasta

```
STEAMDB/
├── Players_730.csv
├── PriceHistory_730.csv
├── SteamHubFollowers_730.csv
├── Twitch_730.csv
├── UserReviewsHistory_730.csv
└── importar_steamdb.bat
```

---

## ⚙️ Pré-requisitos

- [Docker](https://www.docker.com/)
- Um container MongoDB rodando com o nome `meu-mongo`
- Os arquivos `.csv` e o script `.bat` nesta pasta

---

## 🚀 Como executar

1. **Clone o repositório ou copie a pasta para seu ambiente local**
2. **Abra o terminal (CMD ou PowerShell) como administrador**
3. **Execute o script:**

```bash
importar_steamdb.bat
```

O script irá:

- Copiar os arquivos CSV para o container Docker
- Importar os dados para o banco `cs2`
- Criar automaticamente as seguintes coleções:
  - `players`
  - `price_history`
  - `steam_hub_followers`
  - `twitch`
  - `user_reviews_history`

---

## 🔎 Verificando os dados no MongoDB

1. **Acesse o shell do MongoDB**:

```bash
docker exec -it meu-mongo mongosh
```

2. **Use o banco de dados**:

```javascript
use cs2
```

3. **Verifique as coleções disponíveis**:

```javascript
show collections
```

4. **Conte os documentos em cada coleção**:

```javascript
db.players.countDocuments()
db.price_history.countDocuments()
db.steam_hub_followers.countDocuments()
db.twitch.countDocuments()
db.user_reviews_history.countDocuments()
```

5. **Visualize amostras dos dados**:

```javascript
db.players.find().limit(3).pretty()
db.price_history.find().limit(3).pretty()
```

---

## 🧾 Observações

- Cada tabela inclui uma coluna adicional `AppID` com valor `730`, identificando que os dados referem-se ao jogo Counter-Strike 2.
- O script não remove dados anteriores. Caso deseje limpar o banco antes da importação, adicione ao script:

```bash
docker exec -it meu-mongo mongosh --eval "use cs2; db.getCollectionNames().forEach(c => db[c].drop());"
```

---

## 🛠 Autor

Este projeto foi desenvolvido como parte de atividades da disciplina **TIS6 - Engenharia de Software**, PUC.
