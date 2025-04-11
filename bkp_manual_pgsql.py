# Importações necessárias
import psycopg2  # Conexão com banco de dados PostgreSQL
import os        # Manipulação de arquivos e diretórios
import json      # Serialização de JSON
import argparse  # Parser de argumentos via terminal
from datetime import datetime, date, timedelta  # Manipulação de datas
from decimal import Decimal  # Suporte a campos numéricos com precisão

# Função para formatar corretamente os valores dos campos em comandos SQL
def formatar_valor(valor):
    if valor is None:
        return 'NULL'
    if isinstance(valor, datetime):  # Data e hora
        return f"'{valor.isoformat(sep=' ')}'"
    if isinstance(valor, date):  # Apenas data
        return f"'{valor.isoformat()}'"
    if isinstance(valor, bool):  # Booleano
        return "'1'" if valor else "'0'"
    if isinstance(valor, (int, float, Decimal)):  # Números
        return str(valor)
    if isinstance(valor, (dict, list)):  # JSON
        json_str = json.dumps(valor).replace("'", "''")
        return f"'{json_str}'"
    if isinstance(valor, bytes):  # Campos binários (bytea)
        return "'\\x" + valor.hex() + "'"
    if isinstance(valor, timedelta):  # Intervalos de tempo
        return f"'{str(valor)}'"
    if isinstance(valor, str):  # Texto
        return "'" + valor.replace("'", "''") + "'"
    return "'" + str(valor).replace("'", "''") + "'"

# Função principal que gera os arquivos de backup
def gerar_backup(args):
    BACKUP_DIR = 'backups'
    os.makedirs(BACKUP_DIR, exist_ok=True)  # Cria a pasta se não existir
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Data/hora atual

    # Caminhos dos arquivos de saída
    insert_path = os.path.join(BACKUP_DIR, f'backup_inserts_{args.database}_{timestamp}.sql')
    ddl_path = os.path.join(BACKUP_DIR, f'backup_ddl_{args.database}_{timestamp}.sql')

    # Conexão com o banco de dados
    conn = psycopg2.connect(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password
    )
    cursor = conn.cursor()

    # Se o usuário informar tabelas específicas, usa apenas elas
    if args.tabelas:
        tabelas = args.tabelas
    else:
        # Caso contrário, busca todas as tabelas do schema público
        cursor.execute("""
            SELECT tablename FROM pg_tables WHERE schemaname='public';
        """)
        tabelas = [row[0] for row in cursor.fetchall()]

    # Abre os dois arquivos de saída
    with open(insert_path, 'w', encoding='utf-8') as f_insert, open(ddl_path, 'w', encoding='utf-8') as f_ddl:
        f_insert.write(f"-- Backup de INSERTs gerado em {datetime.now()}\nBEGIN;\n\n")
        f_ddl.write(f"-- Backup de estrutura (DDL) gerado em {datetime.now()}\n\n")

        for tabela in tabelas:
            # Gera o DDL da tabela (estrutura)
            cursor.execute("""
                SELECT column_name, data_type, character_maximum_length, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
            """, (tabela,))
            colunas = cursor.fetchall()

            ddl_linhas = []
            for nome_coluna, tipo, tamanho, nulavel in colunas:
                tipo_formatado = tipo.upper()
                if tipo in ['character varying', 'varchar', 'char'] and tamanho:
                    tipo_formatado = f"{tipo.upper()}({tamanho})"
                linha = f'    "{nome_coluna}" {tipo_formatado}'
                if nulavel == 'NO':
                    linha += ' NOT NULL'
                ddl_linhas.append(linha)

            ddl = f'CREATE TABLE "{tabela}" (\n' + ',\n'.join(ddl_linhas) + '\n);\n'
            f_ddl.write(ddl + '\n')

            # Gera os dados da tabela como comandos INSERT
            cursor.execute(f'SELECT * FROM "{tabela}"')
            registros = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]

            for linha in registros:
                valores = [formatar_valor(v) for v in linha]
                insert_sql = f'INSERT INTO "{tabela}" ({", ".join(colunas)}) VALUES ({", ".join(valores)});\n'
                f_insert.write(insert_sql)

            f_insert.write('\n')

        f_insert.write("COMMIT;\n")

    # Fecha conexão com o banco
    cursor.close()
    conn.close()
    print(f"✅ Arquivo de INSERTs salvo em: {insert_path}")
    print(f"✅ Arquivo de DDL salvo em:     {ddl_path}")

# Define os argumentos que podem ser passados via terminal
def main():
    parser = argparse.ArgumentParser(description="Backup manual do PostgreSQL com INSERTs e CREATEs")
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', default='5432')
    parser.add_argument('--database', required=True)
    parser.add_argument('--user', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--tabelas', nargs='*', help='Lista de tabelas específicas (opcional)')
    args = parser.parse_args()
    gerar_backup(args)

# Ponto de entrada do script
if __name__ == '__main__':
    main()
