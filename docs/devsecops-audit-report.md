# 📋 Padrão de Relatório de Auditoria DevSecOps

Este documento define o formato oficial do **Relatório Padronizado de Auditoria DevSecOps**, a melhoria exclusiva desenvolvida para o **DIO Agent Security**.

Ele foi desenhado para conectar desenvolvimento de software, segurança de aplicações (AppSec) e esteiras DevSecOps, servindo como modelo de entrega técnica para o Desafio de Projeto da DIO e composição de portfólio no GitHub.

---

## 1. Exemplo Preenchido de Referência: Análise de Autenticação SQLi

Abaixo apresentamos um relatório real e completo baseado no laboratório local (`lab/app.py`).

```markdown
# 🛡️ Relatório de Auditoria DevSecOps: Módulo de Autenticação do Portal de Alunos

**Data da Análise:** 2026-10-20

**Auditor / Mentor:** DIO Agent Security

**Escopo / Componente Analisado:** `lab/app.py` (função `authenticate_vulnerable`)

**Ambiente:** Homologação / Laboratório de Testes

---

### 1. Resumo Executivo
Foi identificada uma vulnerabilidade grave no mecanismo de autenticação de usuários, onde os parâmetros de entrada são concatenados diretamente no comando SQL sem parametrização. Essa falha permite que um atacante contorne a autenticação sem conhecer a senha ou extraia credenciais armazenadas, quebrando a integridade e confidencialidade do sistema. A mitigação definitiva foi aplicada com Prepared Statements e comprovada por testes unitários locais.

---

### 2. Identificação da Vulnerabilidade e Evidências
- **Vulnerabilidade:** Injeção de SQL em Parâmetro de Autenticação (SQL Injection Bypass)
- **Mapeamento de Padrões:**
  - **CWE:** CWE-89 (Improper Neutralization of Special Elements used in an SQL Command)
  - **OWASP Top 10:** A05:2025 – Injection (referência histórica: A03:2021 – Injection)
  - **MITRE ATT&CK:** T1190 (Exploit Public-Facing Application - aplicável se exposto publicamente na internet). *Nota de Rigor:* T1078 (Valid Accounts) não se aplica ao bypass lógico da checagem SQL, sendo aplicável apenas se credenciais válidas forem extraídas e posteriormente reutilizadas.
- **Trecho de Código Afetado:**
  ```python
  # lab/app.py: authenticate_vulnerable
  query = f"SELECT id, username, role, email FROM users WHERE username = '{username}' AND password_hash = '{password_hash}'"
  cursor.execute(query)
  ```
- **Mecanismo da Falha:** A interpolação com f-string permite que entradas contendo apóstrofos e operadores lógicos (ex: `admin' --`) fechem antecipadamente o delimitador de string do SQL e comentem o restante da cláusula `WHERE`, forçando a consulta a retornar o primeiro usuário sem verificar o hash da senha.

---

### 3. Avaliação de Risco e Classificação
- **Fraqueza Técnica vs. Risco Contextual:** A presença de concatenação direta é uma vulnerabilidade intrínseca de código (CWE-89). A severidade de risco foi ponderada considerando o ambiente de teste versus um ambiente produtivo.
- **Probabilidade:** Alta — O endpoint de login é publicamente acessível e a exploração não requer privilégios ou autenticação prévia.
- **Impacto:** Alto — Permite acesso irrestrito com perfil `ADMIN`, comprometendo a confidencialidade das contas e integridade dos dados da aplicação.
- **Severidade Final:** **Crítica** (no pior cenário de exposição pública direta) / **Média** (em ambiente de laboratório isolado com dados de teste).
- **Vetor Base CVSS v3.1 (Avaliação Hipotética de Pior Cenário):** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N` (Score 9.1 - Crítico).
  - *Premissas do cálculo hipotético:* Considera a hipótese de um serviço em produção diretamente exposto à internet, sem WAF e com dados sensíveis no banco. Em um cenário de laboratório local isolado ou intranet com dados sintéticos de teste, o risco real de negócio é reduzido para Médio/Baixo.

---

### 4. Plano de Correção e Código Seguro
- **Correção Recomendada (Prepared Statement):**
  ```python
  # lab/app.py: authenticate_secure
  query = "SELECT id, username, role, email FROM users WHERE username = ? AND password_hash = ?"
  cursor.execute(query, (username, password_hash))
  ```
- **Boas Práticas Complementares:**
  - Utilização de algoritmo de derivação segura com salt (Argon2id ou PBKDF2) para comparação de senhas em vez de comparação direta na cláusula SQL.
  - Implementação de limitação de tentativas (*rate limiting*) para mitigar ataques de força bruta.
  - Paginação segura em consultas de listagem com validação de limites para prevenir exaustão de recursos (CWE-400).
  - Usuário de conexão da aplicação com privilégios mínimos no banco de dados (sem privilégios DDL como `DROP` ou `ALTER`).

---

### 5. Validação Técnica e Evidências de Teste
A correção foi submetida à suíte de testes automatizados (`lab/test_lab.py`), alcançando 100% de sucesso:
- **Resultados Observados (Testes Efetivamente Executados):**
  - `test_sqli_auth_bypass_succeeds_in_vulnerable`: Comprovou bypass na versão vulnerável com `admin' --`.
  - `test_sqli_auth_bypass_fails_in_secure`: Comprovou que a consulta parametrizada rejeitou o payload (`retorno: None`).
  - `test_legitimate_input_with_apostrophe_fails_in_vulnerable`: Comprovou que `d'angelo` causa erro de sintaxe SQL capturado como `sqlite3.OperationalError` (e não `SyntaxError` de Python).
  - `test_legitimate_input_with_apostrophe_succeeds_in_secure`: Usuários legítimos com apóstrofo foram cadastrados e autenticados com sucesso.
- **Resultados Esperados:**
  - Neutralização estrutural de injeções lógicas e suporte nativo a caracteres especiais legítimos.
- **Testes Não Executados:**
  - Testes de estresse de concorrência massiva e varreduras dinâmicas DAST com ferramentas externas (fora do escopo deste laboratório local em memória).

---

### 6. Risco Residual
- **Estado Pós-Mitigação:** Baixo no escopo do módulo de autenticação. A consulta foi 100% parametrizada, eliminando a injeção SQL no endpoint. *(Não se atribui CVSS 0.0 de forma automática ou simplista ao sistema, pois a segurança global depende dos demais módulos e controles de acesso).*
- **Recomendações para a Esteira DevSecOps:**
  - Adicionar linter de segurança SAST (como `bandit` para Python ou `semgrep`) no pipeline CI/CD para bloquear futuros commits com queries concatenadas.
  - Conduzir testes periódicos de dependências (SCA) para bibliotecas de banco de dados.
```

---

## 2. Template em Branco (Para Uso em Novos Projetos)

```markdown
# 🛡️ Relatório de Auditoria DevSecOps: [Nome da Aplicação ou Componente]

**Data da Análise:** YYYY-MM-DD

**Auditor / Mentor:** DIO Agent Security

**Escopo / Componente Analisado:** [Arquivo, Rota ou Serviço]

**Ambiente:** [Laboratório Local / Homologação / Produção]

---

### 1. Resumo Executivo
[Breve resumo em 2-3 frases explicando o que foi encontrado, o risco real para o ambiente e o objetivo da remediação.]

---

### 2. Identificação da Vulnerabilidade e Evidências
- **Vulnerabilidade:** [Nome da vulnerabilidade]
- **Mapeamento de Padrões:**
  - **CWE:** [Ex: CWE-XXX]
  - **OWASP Top 10:** [Ex: AXX:2025 (ou AXX:2021) - Categoria]
  - **MITRE ATT&CK:** [Ex: TXXXX - Técnica (especificar se requer exposição externa ou condições prévias)]
- **Trecho de Código Afetado:**
  \`\`\`[linguagem]
  // Evidência do código vulnerável
  \`\`\`
- **Mecanismo da Falha:** [Explicação técnica do mecanismo de exploração]

---

### 3. Avaliação de Risco e Classificação
- **Fraqueza Técnica vs. Risco Contextual:** [Diferenciação clara entre a fraqueza formal de código e o risco no ambiente analisado]
- **Probabilidade:** [Alta / Média / Baixa] — *Justificativa contextual.*
- **Impacto:** [Alto / Médio / Baixo] — *Análise na Tríade CIA.*
- **Severidade Final:** [Crítica / Alta / Média / Baixa / Informativa]
- **Vetor Base / Estimativa CVSS:** [Vetor CVSS justificado explicitando se é hipótese de pior cenário e quais as premissas de exposição. Sem scores fictícios]

---

### 4. Plano de Correção e Código Seguro
- **Correção Recomendada (Prepared Statements e Paginação Segura):**
  \`\`\`[linguagem]
  // Código seguro corrigido
  \`\`\`
- **Boas Práticas Complementares:**
  - [Prática defensiva 1]
  - [Prática defensiva 2]
  - [Validação de limite e página para contenção de recursos / DoS]

---

### 5. Validação Técnica e Evidências de Teste
- **Resultados Observados (Testes Efetivamente Executados):**
  - [Descrever os testes executados com evidências e saídas reais]
- **Resultados Esperados:**
  - [Comportamentos teoricamente previstos pela correção]
- **Testes Não Executados:**
  - [Cenários pendentes ou que dependem de infraestrutura adicional]

---

### 6. Risco Residual
- **Estado Pós-Mitigação:** [Nível de risco residual qualitativo fundamentado pós-correção. NUNCA atribuir CVSS 0.0 de forma automática]
- **Recomendações para a Esteira DevSecOps:** [Próximos passos e automações]
```
