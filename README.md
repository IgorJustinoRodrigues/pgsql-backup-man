# pgsql-backup-manual

Script em Python para gerar backups manuais de bancos de dados PostgreSQL **sem usar `pg_dump`**, com suporte a exportação:
- Dos dados em formato SQL (`INSERT INTO`)
- Da estrutura (`CREATE TABLE`)
- De todas as tabelas ou apenas tabelas selecionadas via argumento

## ✨ Recursos

- Backup completo do banco de dados (estrutura + dados)
- Seleção opcional de tabelas específicas
- Totalmente compatível com diferentes tipos de dados: JSON, BOOLEAN, TEXT, TIMESTAMP, etc.
- Exporta dois arquivos `.sql`: um com os dados e outro com os `CREATE TABLE`

## 🛠️ Pré-requisitos

- Python 3.7+
- Biblioteca `psycopg2`:
```bash
pip install psycopg2
```

## 🚀 Como usar

### Executar backup completo:

```bash
python bkp_manual_pgsql.py --host localhost --port 5432 --database seu_banco --user seu_usuario --password sua_senha
```

### Executar backup apenas de tabelas específicas:

```bash
python bkp_manual_pgsql.py --host localhost --port 5432 --database seu_banco --user seu_usuario --password sua_senha --tabelas tabela1 tabela2 tabela3
```

## 📦 Saída

Será criada uma pasta `backups/` com dois arquivos:

- `backup_inserts_<nome_banco>_<data>.sql` – Contém os dados em `INSERT INTO`
- `backup_ddl_<nome_banco>_<data>.sql` – Contém os `CREATE TABLE` de cada tabela

## 🔐 Segurança

Evite versionar arquivos `.sql` contendo dados sensíveis.

## 🧠 Sugestão de uso

Pode ser usado em automações de backup, integração com cron ou GitHub Actions para versionamento interno.

---

Desenvolvido por Igor Justino Rodrigues

