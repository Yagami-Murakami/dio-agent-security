"""
Testes Automatizados do Laboratório de SQL Injection e Consultas Parametrizadas
DIO Agent Security - Validação e Comprovação de Segurança
"""

import unittest
import sqlite3
from lab.app import (
    get_connection,
    authenticate_vulnerable,
    authenticate_secure,
    search_products_vulnerable,
    search_products_secure,
    register_user_vulnerable,
    register_user_secure
)


class TestSQLInjectionLab(unittest.TestCase):

    def setUp(self):
        """Inicializa um banco de dados SQLite isolado em memória antes de cada teste."""
        self.conn = get_connection()

    def tearDown(self):
        """Fecha a conexão do banco de dados em memória."""
        self.conn.close()

    # --------------------------------------------------------------------------
    # 1. TESTES DE COMPORTAMENTO LEGÍTIMO (Linha de Base Funcional)
    # --------------------------------------------------------------------------

    def test_legitimate_authentication_success(self):
        """Garante que credenciais válidas funcionam tanto na versão vulnerável quanto na segura."""
        user_vuln = authenticate_vulnerable(
            self.conn, "admin", "pbkdf2:sha256:admin_secret_hash_9981"
        )
        user_sec = authenticate_secure(
            self.conn, "admin", "pbkdf2:sha256:admin_secret_hash_9981"
        )

        self.assertIsNotNone(user_vuln)
        self.assertIsNotNone(user_sec)
        self.assertEqual(user_vuln["username"], "admin")
        self.assertEqual(user_sec["username"], "admin")
        self.assertEqual(user_sec["role"], "ADMIN")

    def test_legitimate_authentication_failure_wrong_password(self):
        """Garante que senhas incorretas são rejeitadas em ambas as versões."""
        self.assertIsNone(authenticate_vulnerable(self.conn, "admin", "senha_errada"))
        self.assertIsNone(authenticate_secure(self.conn, "admin", "senha_errada"))

    # --------------------------------------------------------------------------
    # 2. TESTES DE AUTENTICAÇÃO: BYPASS VIA SQL INJECTION
    # --------------------------------------------------------------------------

    def test_sqli_auth_bypass_succeeds_in_vulnerable(self):
        """
        Comprova a vulnerabilidade CWE-89:
        A injeção de 'admin' --' comenta a checagem de senha e faz o bypass no código vulnerável.
        """
        sqli_payload = "admin' --"
        bypassed_user = authenticate_vulnerable(self.conn, sqli_payload, "senha_qualquer")

        # No código vulnerável, o bypass TEM SUCESSO (falha crítica de autenticação)
        self.assertIsNotNone(bypassed_user)
        self.assertEqual(bypassed_user["username"], "admin")

    def test_sqli_auth_bypass_fails_in_secure(self):
        """
        Comprova a eficácia da mitigação defensiva:
        O Prepared Statement trata 'admin\' --' como o valor literal do username,
        portanto a injeção falha completamente e o acesso é negado.
        """
        sqli_payload = "admin' --"
        user = authenticate_secure(self.conn, sqli_payload, "senha_qualquer")

        # No código seguro, o retorno DEVE SER None
        self.assertIsNone(user)

    def test_sqli_boolean_or_bypass_fails_in_secure(self):
        """
        Testa o padrão clássico ' OR '1'='1' --.
        Garante que a versão parametrizada não avalia a expressão booleana injetada.
        """
        sqli_payload = "' OR '1'='1' --"
        user_vuln = authenticate_vulnerable(self.conn, sqli_payload, "qualquer")
        user_sec = authenticate_secure(self.conn, sqli_payload, "qualquer")

        # Vulnerável aceita o primeiro registro da tabela (admin) devido à injeção booleana
        self.assertIsNotNone(user_vuln)
        self.assertEqual(user_vuln["username"], "admin")

        # Seguro rejeita categoricamente, pois busca o username literal "' OR '1'='1' --"
        self.assertIsNone(user_sec)

    # --------------------------------------------------------------------------
    # 3. TESTES DE BUSCA: VAZAMENTO DE DADOS VIA UNION INJECTION
    # --------------------------------------------------------------------------

    def test_sqli_union_data_leak_in_vulnerable(self):
        """
        Comprova extração não autorizada de dados (quebra de Confidencialidade):
        Na busca vulnerável, um payload UNION SELECT extrai hashes da tabela de usuários.
        """
        union_payload = "xxx' UNION SELECT id, username, password_hash, 0.0 FROM users --"
        results = search_products_vulnerable(self.conn, union_payload)

        # Verifica se os usuários do sistema foram expostos dentro do resultado de produtos
        leaked_usernames = [r["name"] for r in results]
        self.assertIn("admin", leaked_usernames)
        self.assertIn("mariasilva", leaked_usernames)

    def test_sqli_union_data_leak_prevented_in_secure(self):
        """
        Comprova que na busca com query parametrizada o UNION SELECT não é executado,
        sendo interpretado apenas como texto da busca LIKE.
        """
        union_payload = "xxx' UNION SELECT id, username, password_hash, 0.0 FROM users --"
        results = search_products_secure(self.conn, union_payload)

        # Nenhum produto possui esse nome literal, resultado deve ser vazio
        self.assertEqual(len(results), 0)

    # --------------------------------------------------------------------------
    # 4. TESTES DE REGRESSÃO: CARACTERES ESPECIAIS LEGÍTIMOS
    # --------------------------------------------------------------------------

    def test_legitimate_input_with_apostrophe_fails_in_vulnerable(self):
        """
        Mostra que a concatenação de strings quebra funcionalidades legítimas:
        Nomes como 'D'Angelo' causam má-formação na sintaxe SQL interpretada pelo SQLite (sqlite3.OperationalError),
        e NÃO um SyntaxError do Python (já que a sintaxe do interpretador Python está 100% correta).
        """
        with self.assertRaises(sqlite3.OperationalError):
            register_user_vulnerable(
                self.conn, "d'angelo", "hash123", "USER", "dangelo@lab.dio.me"
            )

    def test_legitimate_input_with_apostrophe_succeeds_in_secure(self):
        """
        Mostra que Prepared Statements preservam a integridade e suportam
        caracteres especiais legítimos de forma totalmente transparente e segura.
        """
        success = register_user_secure(
            self.conn, "d'angelo", "hash123", "USER", "dangelo@lab.dio.me"
        )
        self.assertTrue(success)

        # Confirma que o usuário foi gravado e pode ser autenticado
        user = authenticate_secure(self.conn, "d'angelo", "hash123")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "d'angelo")


if __name__ == "__main__":
    unittest.main()
