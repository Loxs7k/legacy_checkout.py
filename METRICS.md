# Métricas – Antes x Depois

Todos os valores abaixo foram medidos com os comandos da atividade (`pytest`, `pytest-cov`, `radon`, `ruff`).

| Indicador                        | Antes        | Depois        |
|----------------------------------|--------------|---------------|
| Testes passando                  | 4 de 4       | 64 de 64      |
| Quantidade de testes             | 4            | 64            |
| Cobertura de testes              | 83%          | 100%          |
| Complexidade da função principal | E (34)       | A (1)         |
| Complexidade média               | E (34.0)     | A (3.09)      |
| Índice de manutenibilidade       | A (51.69)    | A (48.17)     |
| Problemas identificados (Ruff)   | 4            | 0             |

## Observações

- A função `process_order` deixou de concentrar todas as regras: a complexidade caiu de 34 para 1, e a maior função atual tem complexidade 6.
- O índice de manutenibilidade continua na faixa A, mas caiu um pouco (51.69 para 48.17). O motivo é que o arquivo ficou maior (mais funções, constantes e docstrings) e o Radon penaliza tamanho. É um débito a ser comentado na apresentação.
- Linhas sem cobertura antes: 27, 30, 41, 44, 48, 66, 69, 78-83. Agora todas são cobertas.

## Como reproduzir

```bash
pip install -r requirements-dev.txt
pytest -v
pytest --cov=legacy_checkout --cov-report=term-missing
radon cc src/legacy_checkout.py -s -a
radon mi src/legacy_checkout.py -s
ruff check src/legacy_checkout.py --statistics
```
