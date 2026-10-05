# BET-AI

Sistema de análise estatística de futebol utilizando Python e API-Football.

## Versão

BET-AI V4.0

## Recursos

- Jogos reais
- Dados da API-Football
- Histórico das equipes
- Forma recente
- Gols marcados
- Gols sofridos
- Probabilidade Casa
- Probabilidade Empate
- Probabilidade Fora
- Dupla chance
- Mais de 1.5 gols
- Mais de 2.5 gols
- Classificação ALTA/MÉDIA/BAIXA
- Geração automática de seleções
- Controle de requisições
- Cache durante a execução
- Tratamento de limite da API

## API

O projeto utiliza:

https://v3.football.api-sports.io

A chave deve ser armazenada no GitHub Secrets:

API_FOOTBALL_KEY

Nunca coloque a chave diretamente no código.

## Execução

O projeto pode ser executado através do GitHub Actions.

Workflow:

.github/workflows/test.yml

## Limitação

A versão V4 utiliza estatísticas disponíveis no endpoint de fixtures.

Mercados como escanteios, chutes, cartões, faltas e desarmes serão adicionados posteriormente através dos endpoints estatísticos apropriados.

As probabilidades são estimativas estatísticas do modelo e não representam garantia de resultado.
