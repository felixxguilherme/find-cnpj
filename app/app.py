import csv
import logging
import chardet
from elasticsearch import Elasticsearch, helpers
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do Elasticsearch
es_host = os.environ.get('ELASTICSEARCH_HOST', 'localhost')
es = Elasticsearch([f"http://{es_host}:9200"])

def format_cnpj(cnpj_basico, cnpj_ordem, cnpj_dv):
    return f"{cnpj_basico}{cnpj_ordem.zfill(4)}{cnpj_dv}"

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read(10000)
    result = chardet.detect(raw_data)
    return result['encoding']

def index_data_to_elasticsearch(csv_file_path):
    logger.info("Iniciando o processo de indexação")    
    es.indices.delete(index='estabelecimentos', ignore=[400, 404])
    
    es.indices.create(index='estabelecimentos', ignore=400, body={
        "settings": {
            "analysis": {
                "analyzer": {
                    "custom_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "asciifolding"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "cnpj_completo": {"type": "keyword"},
                "cnpj_basico": {"type": "keyword"},
                "nome_fantasia": {
                    "type": "text",
                    "analyzer": "custom_analyzer"
                },
                "municipio_codigo": {"type": "keyword"},
                "uf": {"type": "keyword"}
            }
        }
    })
    logger.info("Índice 'estabelecimentos' criado")
    
    file_encoding = detect_encoding(csv_file_path)

    def generate_actions():
        total_rows = 0
        with open(csv_file_path, 'r', encoding=file_encoding, errors='replace') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            next(reader)
            for i, row in enumerate(reader):
                if i % 10000 == 0:
                    logger.info(f"Processando linha {i}")
                total_rows = i + 1
                try:
                    cnpj_completo = format_cnpj(row[0], row[1], row[2])
                    yield {
                        "_index": "estabelecimentos",
                        "_id": cnpj_completo,
                        "_source": {
                            "cnpj_completo": cnpj_completo,
                            "cnpj_basico": row[0],
                            "nome_fantasia": row[4] if row[4] else None,
                            "municipio_codigo": row[20],
                            "uf": row[19]
                        }
                    }
                except Exception as e:
                    logger.error(f"Erro ao processar linha {i}: {str(e)}")
                    continue
        logger.info(f"Total de linhas processadas: {total_rows}")

    try:
        logger.info("Iniciando a indexação em massa")
        success, failed = helpers.bulk(es, generate_actions())
        logger.info(f"Indexação concluída. Documentos indexados com sucesso: {success}. Falhas: {failed}")
    except Exception as e:
        logger.error(f"Erro durante a indexação: {str(e)}")
        logger.exception("Detalhes do erro:")

    try:
        index_stats = es.indices.stats(index='estabelecimentos')
        doc_count = index_stats['indices']['estabelecimentos']['total']['docs']['count']
        logger.info(f"Número de documentos no índice 'estabelecimentos': {doc_count}")
    except Exception as e:
        logger.error(f"Erro ao verificar estatísticas do índice: {str(e)}")

if __name__ == '__main__':
    logger.info("Script iniciado")
    csv_file_path = '/app/data/estabelecimentos.csv'
    if os.path.exists(csv_file_path):
        logger.info(f"Arquivo CSV encontrado. Tamanho: {os.path.getsize(csv_file_path)} bytes")
        file_encoding = detect_encoding(csv_file_path)
        logger.info(f"Codificação detectada: {file_encoding}")
        with open(csv_file_path, 'r', encoding=file_encoding, errors='replace') as f:
            logger.info(f"Primeiras 5 linhas do arquivo:")
            for i, line in enumerate(f):
                if i < 5:
                    logger.info(line.strip())
                else:
                    break
        logger.info("Chamando a função de indexação")
        index_data_to_elasticsearch(csv_file_path)
    else:
        logger.warning(f"Arquivo CSV não encontrado em {csv_file_path}")
    logger.info("Script finalizado")