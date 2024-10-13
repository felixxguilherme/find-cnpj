FROM docker.elastic.co/elasticsearch/elasticsearch:7.14.0

# Instalar plugin de análise ICU
RUN elasticsearch-plugin install --batch analysis-icu

# Copiar arquivo de configuração personalizado
COPY elasticsearch.yml /usr/share/elasticsearch/config/

# Definir permissões corretas
RUN chown elasticsearch:elasticsearch config/elasticsearch.yml

# Expor as portas necessárias
EXPOSE 9200 9300

# Executar o Elasticsearch como usuário elasticsearch
USER elasticsearch