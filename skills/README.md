# Skills do DIO Agent

## O que é uma skill

Uma **skill** é um guia passo a passo que ensina o agente a executar uma tarefa específica bem feita. Em vez de deixar o agente improvisar, a skill dá um processo claro a seguir.

Cada skill fica em uma pasta com um arquivo `SKILL.md`. Esse formato segue o padrão aberto de skills para agentes, funcionando de maneira consistente em diferentes harnesses (Google Antigravity, Claude Code, Hermes, Cursor, etc.).

## Como o agente usa as skills

O estudante não precisa "chamar" ou invocar a skill manualmente. Basta conversar de forma natural. O agente identifica a necessidade no contexto da conversa e aplica a skill certa por trás dos panos.

Por exemplo:
- Se o estudante diz *"não sei por onde começar"*, o agente usa a skill de plano de estudos.
- Se o estudante pergunta *"esse código tem SQL injection?"* ou compartilha um trecho para revisão de segurança, o agente aplica a skill de análise de vulnerabilidades.

## Skills disponíveis

| Skill | Para que serve | Exemplo de pedido do estudante |
|-------|----------------|--------------------------------|
| [study-plan](study-plan/SKILL.md) | Montar um plano de estudos organizado e conectado à DIO | "Quero ser dev back-end, por onde começo?" |
| [unblock-challenge](unblock-challenge/SKILL.md) | Destravar um desafio com dicas graduais, sem resposta pronta | "Travei nesse desafio, me ajuda?" |
| [explain-concept](explain-concept/SKILL.md) | Explicar um conceito técnico com analogias simples | "Não entendi o que é uma API." |
| [web-search](web-search/SKILL.md) | Fundamentar respostas com busca atual e fontes citadas | "Qual a versão estável do Node hoje?" |
| [portfolio-review](portfolio-review/SKILL.md) | Revisar portfólio e GitHub com foco em processos seletivos | "Pode avaliar o README e o código do meu projeto?" |
| [vulnerability-analysis](vulnerability-analysis/SKILL.md) | Analisar vulnerabilidades, classificar riscos e validar correções | "Meu endpoint de login está vulnerável a SQL Injection?" |

## Como criar uma nova skill

1. Crie uma pasta dentro de `skills/` com um nome curto em inglês (ex: `skills/vulnerability-analysis`).
2. Adicione um arquivo `SKILL.md` com o cabeçalho YAML frontmatter e o passo a passo detalhado.
3. Adicione a documentação e exemplos em `README.md` dentro da pasta da skill.
4. Registre a nova skill na tabela de `AGENTS.md` para o agente saber exatamente quando ativá-la.
