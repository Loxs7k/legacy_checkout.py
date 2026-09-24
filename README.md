# REFactor Race Python

## DESCRIÇÃO

Refatoração de um sistema legado de processamento de pedidos (`src/legacy_checkout.py`), mantendo o comportamento original e comprovando a melhoria com testes e métricas.

## DIAGNÓSTICO INICIAL

1. `process_order` fazia tudo: subtotal, desconto, frete, imposto, pontos, duplicados, armazenamento e impressão (complexidade E, 34).
2. O subtotal era calculado duas vezes (`total1` e `subtotal`), e `total1` nunca era usado.
3. Condicionais aninhadas (`else: if ...`) para o desconto por tipo de cliente.
4. Números mágicos espalhados (0.15, 0.10, 800, 1000, 1.8, 0.4, 0.6...).
5. Strings mágicas repetidas ("vip", "MG", "PROMO10"...).
6. Cadeia de `if/elif` para taxas por estado e `state == "MG" or ...` para o frete.
7. Comparações `express == False` / `express == True`.
8. Busca de duplicados com dois loops (`O(n²)`) e `not in` em lista.
9. Nomes ruins e mistura de idiomas (`total1`, `taxa`, `frete`, `peso`).
10. Baixa testabilidade: regras dentro de uma função só, com `print` e estado global misturados.
11. Cobertura de 83%, com cupons, frete e impostos sem teste.

## CODE SMELLS ENCONTRADOS

| Code smell | Onde |
|---|---|
| Função longa / muitas responsabilidades | `process_order` |
| Código duplicado | cálculo do subtotal (2x) |
| Condicional complexa e aninhada | desconto por tipo de cliente |
| Números e strings mágicos | descontos, frete, impostos |
| Nomes pouco descritivos | `total1`, `taxa`, `x` |
| Estrutura de dados inadequada | duplicados com loop duplo e lista |
| Comentários explicando código confuso | "procura produtos repetidos de forma bem pouco elegante" |

## REFATORAÇÕES REALIZADAS

**1. Extract Function**
- Problema: uma função enorme com todas as regras.
- Alteração: criadas `calculate_subtotal`, `calculate_customer_discount`, `calculate_coupon_discount`, `calculate_discount`, `calculate_total_weight`, `calculate_shipping`, `calculate_tax`, `calculate_points`, `find_duplicate_products` e `print_order_summary`.
- Justificativa: cada regra fica isolada, testável e fácil de alterar. Complexidade da principal: 34 para 1.

**2. Remove Duplicate Code**
- Problema: subtotal calculado duas vezes.
- Alteração: um único `calculate_subtotal`.
- Justificativa: uma só fonte da verdade.

**3. Replace Magic Number with Constant**
- Problema: valores fixos sem significado.
- Alteração: constantes como `EXPRESS_SHIPPING_MULTIPLIER`, `MAX_DISCOUNT_RATE`, `FREE_SHIPPING_MIN_SUBTOTAL`.
- Justificativa: regras ficam nomeadas e fáceis de ajustar.

**4. Replace Conditional with Mapping / Simplify Conditional**
- Problema: `if/elif` de impostos e `or` encadeado no frete.
- Alteração: dicionário `TAX_RATES` com `DEFAULT_TAX_RATE`, e `state in SOUTHEAST_STATES`.
- Justificativa: menos ramificações e fácil adicionar estados.

**5. Guard clauses (retorno antecipado)**
- Problema: `else: if ...` aninhado no desconto.
- Alteração: `if` sequenciais com `return`.
- Justificativa: menos aninhamento, leitura linear.

**6. Otimização de algoritmo**
- Problema: busca de duplicados `O(n²)`.
- Alteração: `Counter` (uma passada, `O(n)`), preservando a ordem da primeira aparição.
- Justificativa: menos comparações com o mesmo resultado.

**7. Rename Variable**
- `total1`/`subtotal`, `desconto`, `frete`, `imposto`, `taxa`, `pontos` viraram nomes em inglês descritivos (`discount`, `shipping`, `tax`, `points`).

## TESTES ADICIONADOS

De 4 para 64 testes (`tests/test_checkout.py` e `tests/test_checkout_units.py`):

- desconto de cliente VIP (abaixo e a partir de 1000), funcionário, regular (limite de 800) e tipo desconhecido;
- cupons `PROMO10`, `PROMO20` (limite de 500), `VIP50`, cupom inválido e cupom em minúsculas (comportamento atual);
- teto de 25% de desconto;
- itens com quantidade 0 ou negativa;
- frete grátis, frete por região, frete expresso e item sem peso;
- imposto por estado (parametrizado) e sobre o valor com desconto;
- pontos de VIP e cliente regular;
- produtos duplicados (nenhum, ordem, repetido várias vezes);
- histórico `ORDERS_PROCESSED` e impressão do resumo;
- testes unitários de cada função extraída.

Os testes de comportamento (`test_checkout.py`) também passam no código original, o que comprova que o comportamento foi preservado. Além disso, foi feita uma comparação aleatória entre o código antigo e o novo (200 mil pedidos) com resultados e saída impressa idênticos.

## MÉTRICAS ANTES E DEPOIS

| Indicador | Antes | Depois |
|---|---|---|
| Testes passando | 4 de 4 | 64 de 64 |
| Cobertura | 83% | 100% |
| Complexidade da função principal | E (34) | A (1) |
| Complexidade média | E (34.0) | A (3.09) |
| Manutenibilidade | A (51.69) | A (48.17) |
| Problemas do Ruff | 4 | 0 |

Detalhes em `METRICS.md`.

## DECISÕES TÉCNICAS

- Mantido o nome do módulo e a assinatura de `process_order`, para não quebrar testes externos.
- Nenhuma regra de negócio foi alterada. Peculiaridades do legado foram preservadas (cupom é sensível a maiúsculas, peso conta itens com quantidade negativa, `ORDERS_PROCESSED` continua global).
- Somas feitas com laço `for` em vez de `sum()`, porque o `sum()` do Python mais novo soma floats de forma diferente e mudaria os valores impressos.
- Adicionado `pytest.ini` com `pythonpath = src` para rodar os testes da raiz.

## USO DE INTELIGÊNCIA ARTIFICIAL

Ferramenta utilizada: Claude (Anthropic).
Finalidade: apoio na refatoração, criação de testes e documentação.
Exemplo de sugestão recebida: trocar os laços de soma por `sum()`.
A sugestão foi aceita, modificada ou rejeitada? Modificada: voltou-se ao laço `for` após a comparação aleatória mostrar diferença nos floats impressos.
Como a equipe validou a solução? Testes originais e novos passando, cobertura, métricas do Radon/Ruff e comparação com o código legado.

> Ajustem este trecho conforme o uso real de IA pela equipe.

## MELHORIAS FUTURAS

- Validar entradas (ticket 1: `qty <= 0` gerar `ValueError`) quando o professor liberar.
- Cupons sem diferenciar maiúsculas/minúsculas (ticket 2), quando liberado.
- Separar `print` e `ORDERS_PROCESSED` da lógica de cálculo (I/O e estado global).
- Usar `Decimal` para valores monetários.
- Dividir o módulo em arquivos menores (descontos, frete, impostos).
