# 🧪 Laboratório Educacional de SQL Injection e Consultas Parametrizadas

Este laboratório é um ambiente de testes autônomo, local e seguro desenvolvido em Python com SQLite em memória. Ele faz parte do projeto **DIO Agent Security**.

Ele demonstra de forma prática e automatizada:
1. Como falhas de injeção de SQL (**CWE-89 / OWASP A05:2025 / A03:2021**) ocorrem devido à interpolação direta de parâmetros não confiáveis.
2. Como **Prepared Statements** (consultas parametrizadas) mitigam a vulnerabilidade de forma definitiva.
3. Como consultas parametrizadas evitam falhas com entradas legítimas que possuem apóstrofos (ex.: `D'Angelo`, `Sant'Ana`), eliminando erros de sintaxe SQL do banco (`sqlite3.OperationalError`) sem qualquer relação com `SyntaxError` do Python.
4. Como aplicar **paginação defensiva** (validação de `page` e teto rígido para `limit`) para mitigar exaustão de recursos e DoS (**CWE-400**).

---

## 📁 Estrutura do Laboratório

```
lab/
├── README.md       # Este guia com instruções de execução e análise
├── app.py          # Implementação das funções vulneráveis e das versões corrigidas
└── test_lab.py     # Suíte de testes automatizados unitários comprovando o comportamento
```

---

## 🚀 Como Executar

O laboratório utiliza exclusivamente a biblioteca padrão do Python (`sqlite3` e `unittest`). Não é necessária a instalação de dependências externas ou conexão com a internet.

Execute os testes com o comando:

```bash
python3 -m unittest lab/test_lab.py -v
```

---

## 🔬 O que os Testes Automatizados Comprovam

| Teste | Objetivo | Resultado Observado |
| :--- | :--- | :--- |
| `test_legitimate_authentication_success` | Verifica que credenciais corretas autenticam tanto na versão vulnerável quanto na segura. | **PASS (OK)** |
| `test_legitimate_authentication_failure_wrong_password` | Verifica que senhas erradas são rejeitadas em ambas as implementações. | **PASS (OK)** |
| `test_sqli_auth_bypass_succeeds_in_vulnerable` | Submete payload de comentário (`admin' --`) na versão vulnerável. | **PASS (OK)**: Acesso concedido sem senha (comprova vulnerabilidade). |
| `test_sqli_auth_bypass_fails_in_secure` | Submete o mesmo payload (`admin' --`) na versão com Prepared Statement. | **PASS (OK)**: Acesso negado (`None`), input tratado como dado literal. |
| `test_sqli_boolean_or_bypass_fails_in_secure` | Testa injeção booleana (`' OR '1'='1' --`). | **PASS (OK)**: Versão vulnerável é contornada; versão parametrizada bloqueia. |
| `test_sqli_union_data_leak_in_vulnerable` | Executa injeção `UNION SELECT` para extrair registros da tabela `users` pela busca de produtos. | **PASS (OK)**: Confidencialidade violada na versão vulnerável. |
| `test_sqli_union_data_leak_prevented_in_secure` | Executa o mesmo `UNION SELECT` na versão parametrizada. | **PASS (OK)**: Nenhum dado vazado, query trata o texto como busca `LIKE`. |
| `test_legitimate_input_with_apostrophe_fails_in_vulnerable` | Insere usuário com nome legítimo contendo apóstrofo (`d'angelo`). | **PASS (OK)**: Concatenação quebra com `sqlite3.OperationalError` (erro de sintaxe SQL da engine, e não `SyntaxError` do Python). |
| `test_legitimate_input_with_apostrophe_succeeds_in_secure` | Insere o mesmo nome (`d'angelo`) na versão parametrizada. | **PASS (OK)**: Inserção bem-sucedida, sem erros de sintaxe SQL ou quebra. |
