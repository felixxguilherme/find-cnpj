# Sistema de Indexação e Consulta de CNPJs

Este projeto indexa dados de estabelecimentos em um banco de dados Elasticsearch e permite consultas por nome fantasia e código de município.

## Pré-requisitos

- Docker
- Docker Compose
- Arquivo `estabelecimentos.csv` com os dados dos estabelecimentos

## Configuração Inicial

1. Clone este repositório:

2. Coloque o arquivo `estabelecimentos.csv` na pasta `data/` do projeto.

## Iniciando o Sistema

1. Inicie os contêineres Docker:

$ docker-compose up --build

2. Aguarde até que a mensagem de indexação concluída apareça nos logs.

## Consultando os Dados

Use os seguintes comandos curl para consultar os dados:

### Consulta Correta

```bash
curl -X GET "localhost:9200/estabelecimentos/_search" -H 'Content-Type: application/json' -d'
{
"size": 5,
"query": {
 "bool": {
   "must": [
     {"term": {"municipio_codigo": "9073"}},
     {"match": {
       "nome_fantasia": {
         "query": "S A R COMERCIO E REPRESENTACOES",
         "fuzziness": "AUTO",
         "minimum_should_match": "80%"
       }
     }}
   ]
 }
},
"_source": ["cnpj_completo", "nome_fantasia"]
}
'
```

### Consulta com erro no nome fantasia

```bash
curl -X GET "localhost:9200/estabelecimentos/_search" -H 'Content-Type: application/json' -d'
{
  "size": 5,
  "query": {
    "bool": {
      "must": [
        {"term": {"municipio_codigo": "9073"}},
        {"match": {
          "nome_fantasia": {
            "query": "S R COMRCIO E REREENCOES",
            "fuzziness": "AUTO",
            "minimum_should_match": "80%"
          }
        }}
      ]
    }
  },
  "_source": ["cnpj_completo", "nome_fantasia"]
}
'
```