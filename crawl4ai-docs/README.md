# Crawl4AI Documentation Crawler

A reusable documentation crawler based on Crawl4AI.

Features:

- Crawl documentation websites
- Start from any URL
- Automatically discover internal links
- Save pages as Markdown
- Import directly into OpenWebUI Knowledge
- Uses Python virtual environment

---

## 1. Create project

```bash
mkdir crawl4ai-docs
cd crawl4ai-docs
```

---

## 2. Create Python virtual environment

```bash
python3 -m venv .venv
```

Activate:

Linux:

```bash
source .venv/bin/activate
```

You will see:

```
(.venv)
```

---

## 3. Install dependencies

```bash
pip install crawl4ai beautifulsoup4
```

Install browser:

```bash
crawl4ai-setup
```

---

## 4. Run crawler

Syntax:

```bash
python crawl.py <START_URL> <OUTPUT_FOLDER>
```

Example HashiCorp Vault:

```bash
python crawl.py \
https://developer.hashicorp.com/vault/docs \
docs/vault
```

Example Kubernetes:

```bash
python crawl.py \
https://kubernetes.io/docs/ \
docs/kubernetes
```

Example WSO2:

```bash
python crawl.py \
https://mi.docs.wso2.com/ \
docs/wso2-mi
```

---

## 5. Output

Example:

```
docs/
└── vault/

    index.md
    about-vault.md
    configuration.md
    auth-methods.md
    secrets-engines.md
```

---

## 6. Import into OpenWebUI

Open:

```
Workspace
  |
  Knowledge
  |
  New Knowledge
```

Create:

```
HashiCorp Vault
```

Add:

```
docs/vault
```

OpenWebUI will create embeddings.

---

## 7. Stop virtual environment

When finished:

```bash
deactivate
```

---

## 8. Start again later

```bash
cd crawl4ai-docs

source .venv/bin/activate
```

Run crawler:

```bash
python crawl.py URL OUTPUT
```

