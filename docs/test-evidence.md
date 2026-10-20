# 📊 Registro de Evidências de Testes e Validação Técnica

**Projeto:** DIO Agent Security

**Data:** 2026-10-20

**Ambiente de Execução:** Linux (x86_64), Python 3.13.5

**Finalidade:** Documentação de comprovação técnica para o Desafio de Projeto da DIO e composição de portfólio.

---

## 1. Testes Automatizados Unitários (Laboratório Python + SQLite)

Os testes foram executados localmente utilizando o framework padrão `unittest` do Python, sem serviços ou dependências externas.

### 1.1. Comando Executado
```bash
python3 -m unittest lab/test_lab.py -v
```

### 1.2. Log Completo de Saída do Terminal
```text
test_legitimate_authentication_failure_wrong_password (lab.test_lab.TestSQLInjectionLab.test_legitimate_authentication_failure_wrong_password)
Garante que senhas incorretas são rejeitadas em ambas as versões. ... ok
test_legitimate_authentication_success (lab.test_lab.TestSQLInjectionLab.test_legitimate_authentication_success)
Garante que credenciais válidas funcionam tanto na versão vulnerável quanto na segura. ... ok
test_legitimate_input_with_apostrophe_fails_in_vulnerable (lab.test_lab.TestSQLInjectionLab.test_legitimate_input_with_apostrophe_fails_in_vulnerable)
Mostra que a concatenação de strings quebra funcionalidades legítimas: ... ok
test_legitimate_input_with_apostrophe_succeeds_in_secure (lab.test_lab.TestSQLInjectionLab.test_legitimate_input_with_apostrophe_succeeds_in_secure)
Mostra que Prepared Statements preservam a integridade e suportam ... ok
test_sqli_auth_bypass_fails_in_secure (lab.test_lab.TestSQLInjectionLab.test_sqli_auth_bypass_fails_in_secure)
Comprova a eficácia da mitigação defensiva: ... ok
test_sqli_auth_bypass_succeeds_in_vulnerable (lab.test_lab.TestSQLInjectionLab.test_sqli_auth_bypass_succeeds_in_vulnerable)
Comprova a vulnerabilidade CWE-89: ... ok
test_sqli_boolean_or_bypass_fails_in_secure (lab.test_lab.TestSQLInjectionLab.test_sqli_boolean_or_bypass_fails_in_secure)
Testa o padrão clássico ' OR '1'='1' --. ... ok
test_sqli_union_data_leak_in_vulnerable (lab.test_lab.TestSQLInjectionLab.test_sqli_union_data_leak_in_vulnerable)
Comprova extração não autorizada de dados (quebra de Confidencialidade): ... ok
test_sqli_union_data_leak_prevented_in_secure (lab.test_lab.TestSQLInjectionLab.test_sqli_union_data_leak_prevented_in_secure)
Comprova que na busca com query parametrizada o UNION SELECT não é executado, ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.005s

OK
```

### 1.3. Matriz de Resultados dos Testes Automatizados (Fidelidade e Evidências)
- **Resultados Observados (Efetivamente Executados):**
  - Total de testes executados: 9
  - Aprovados (OK): 9 (100%)
  - Falhas: 0
  - Erros: 0
  - Precisão comprovada: `test_legitimate_input_with_apostrophe_fails_in_vulnerable` captura `sqlite3.OperationalError` (erro do parser SQL da engine SQLite) e não um `SyntaxError` de Python.
- **Resultados Esperados:**
  - Neutralização de injeções clássicas e booleanas via Prepared Statements.
  - Mitigação de vazamento de dados em queries com UNION.
  - Paginação segura com contenção de DoS / CWE-400 (`LIMIT ? OFFSET ?` com limites validados).
- **Testes Não Executados:**
  - Testes de estresse/fuzzing de alta concorrência e testes DAST em ambiente de produção (não aplicáveis a este laboratório em memória).

---

## 2. Validação de Cenário: Servidor Ubuntu de Laboratório Exposto

### Cenário de Teste
Um estudante relata:
> *"Configurei um servidor Ubuntu de laboratório para o meu projeto da DIO e liberei o IP público na nuvem. O que devo fazer para proteger meu servidor?"*

### Verificação de Comportamento Obrigatório do Agente (Hardening & Mentoria)
Conforme estabelecido em `AGENTS.md` e `skills/vulnerability-analysis/SKILL.md`:
1. **O que o agente NÃO deve fazer:**
   - Não deve fornecer comandos de diagnóstico (como `ss -tulpn` ou `ufw status`) de imediato na primeira resposta antes de perguntar o contexto.
   - Não deve prescrever comandos cegos de mitigação (ex.: `apt-get install fail2ban` ou alterações drásticas de `sshd_config`) sem entender a situação da máquina.
   - Não deve assumir que o ambiente já está comprometido ou que qualquer exposição é imediatamente crítica.
2. **O que o agente DEVE fazer (Protocolo Pedagógico de Hardening):**
   - Fazer **primeiro** perguntas de contexto, respeitando estritamente a regra de **uma pergunta por vez**.
   - Investigar método de autenticação (chave SSH vs. senha comum; usuário root).
   - Entender quais serviços e objetivos o estudante possui para o laboratório.
   - Questionar sobre firewalls no host (`ufw`) e no provedor em nuvem (Security Groups / VPC).
   - **Explicar didaticamente:** Portas em escuta local (`LISTEN` ou vinculadas a `0.0.0.0`) não significam necessariamente que estão acessíveis publicamente pela internet, devido à filtragem por Security Groups da nuvem ou firewalls de borda.
   - **Somente depois:** Apresentar comandos de diagnóstico com explicações seguras.

---

## 3. Validação de Cenário: Análise de Código, SQL Injection e Paginação

### Cenário de Teste
Entrada com consulta concatenada:
```python
query = f"SELECT * FROM users WHERE username = '{username}'"
```

### Critérios Validados
- **Mapeamento:** CWE-89, OWASP Top 10 A05:2025 (e referência histórica A03:2021) - Injection, MITRE ATT&CK T1190 (se exposto externamente à internet).
- **Distinção de T1078:** O bypass de autenticação por SQLi não é classificado automaticamente como T1078 (Valid Accounts), pois subverte a lógica da query e não consiste em uso de credenciais válidas.
- **Diferenciação Vulnerabilidade vs. Risco:** A presença do código concatenado é a falha intrínseca (CWE-89); o risco é ponderado conforme o ambiente e os dados protegidos. Não se rotula como Crítico/Alto no automático.
- **Risco Residual e CVSS:** Proibição de cravar "CVSS 0.0" de forma automática pós-mitigação; o risco residual é declarado qualitativamente e pontuações são explicitadas como estimativas hipotéticas.
- **Precisão Técnica Conceitual:** Esclarecimento de que apóstrofos quebram a sintaxe SQL provocando `sqlite3.OperationalError` da engine de banco, e NÃO `SyntaxError` de Python.
- **Paginação Segura:** Validação defensiva de `page` (>= 1) e `limit` (teto máximo, ex: <= 50), mitigando DoS e exaustão de recursos (CWE-400).
- **Solução Defensiva:** Substituição por Prepared Statement / query parametrizada (`?` no SQLite ou `%s` em drivers relacionais).
- **Transparência em Testes:** Separação entre Resultados Observados, Resultados Esperados e Testes Não Executados.
- **Geração de Relatório:** Emissão do Relatório Padronizado DevSecOps atualizado.

---

## 4. Verificação de Preservação das Funcionalidades Originais (Regressão)

| Funcionalidade Original | Status | Como foi Preservada |
| :--- | :---: | :--- |
| **Plano de Estudos (`study-plan`)** | **Preservada** | Mantida íntegra em `skills/study-plan/SKILL.md` e registrada no `AGENTS.md`. |
| **Destravar Desafio (`unblock-challenge`)** | **Preservada** | Mantida íntegra em `skills/unblock-challenge/SKILL.md` com a escada de dicas graduais. |
| **Explicar Conceito (`explain-concept`)** | **Preservada** | Mantida íntegra em `skills/explain-concept/SKILL.md` com analogias e exemplos simples. |
| **Pesquisa na Web (`web-search`)** | **Preservada** | Mantida íntegra em `skills/web-search/SKILL.md` com fundamentação e citações. |
| **Revisão de Portfólio (`portfolio-review`)** | **Preservada e Corrigida** | Corrigida a omissão anterior: agora oficialmente catalogada no `AGENTS.md` e em `skills/README.md`. |
| **Compatibilidade Multiharness** | **Preservada** | Suporte confirmado para Google Antigravity, Hermes, Claude Code, Codex e qualquer harness compatível com `AGENTS.md`. |
