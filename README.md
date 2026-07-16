# Validação criptográfica de dados de medicamentos

Prova de conceito que combina **PKI**, **SoftHSM**, **PKCS#11**, **assinatura digital** e **DataMatrix** para verificar se dados associados a um medicamento demonstrativo permaneceram íntegros após a emissão.

> **Escopo:** o projeto valida o conteúdo digital assinado. Ele não comprova sozinho a autenticidade física do medicamento e não substitui sistemas regulatórios de rastreabilidade.

## Resultado demonstrado

| Cenário | Resultado |
|---|---|
| Payload original | `VÁLIDO` |
| Lote alterado sem nova assinatura | `INVÁLIDO` |

## Fluxo

```text
Dados do medicamento
        ↓
Assinatura com chave privada no SoftHSM
        ↓
Payload + KID + assinatura em DataMatrix
        ↓
Leitura, validação do certificado e verificação da assinatura
        ↓
VÁLIDO ou INVÁLIDO
```

## Tecnologias

- Kali Linux;
- Python 3;
- OpenSSL;
- SoftHSM2;
- OpenSC / `pkcs11-tool`;
- PKCS#11;
- Pillow e pylibdmtx.

## Estrutura

```text
.
├── config/pki/       # Extensões dos certificados
├── docs/             # Arquitetura, metodologia, formato e limites
├── examples/         # Dados fictícios de referência
├── scripts/          # Geração, assinatura, DataMatrix e verificação
├── tests/            # Validação rápida do ambiente
├── .env.example      # Configuração demonstrativa sem segredos reais
├── setup.sh          # Instala dependências e cria a .venv
├── build_lab.sh      # Reconstrói tokens, PKI e artefatos
├── run_demo.sh       # Executa os cenários válido e alterado
└── Makefile           # Atalhos de execução
```

A pasta `output/` é criada localmente e não é versionada.

## Execução rápida no Kali Linux

```bash
git clone https://github.com/SEU-USUARIO/pki-hsm-datamatrix-pharma.git
cd pki-hsm-datamatrix-pharma

./setup.sh --clean
./run_demo.sh
```

Ou, usando o Makefile:

```bash
make setup
make demo
```

## Comandos úteis

```bash
make check   # valida sintaxe, estrutura e dependências
make build   # reconstrói apenas o laboratório
make clean   # remove artefatos gerados
```

## Documentação

- [Arquitetura](docs/architecture.md)
- [Metodologia](docs/methodology.md)
- [Formato do payload](docs/payload-format.md)
- [Modelo de ameaça](docs/threat-model.md)
- [Limitações](docs/limitations.md)

## Limites principais

- a assinatura valida os dados digitais, não o produto físico;
- uma cópia integral de um payload válido pode continuar passando na verificação;
- o SoftHSM simula a interface de um HSM, mas não oferece proteção física equivalente;
- o registro opcional de eventos não comprova clonagem sozinho;
- a PoC não implementa CRL, OCSP ou integração oficial com o SNCM.

## Segurança

Os PINs do `.env.example` são apenas demonstrativos. A pasta `output/`, a `.env`, os tokens, as chaves, os certificados gerados, os payloads e as imagens DataMatrix permanecem fora do Git por meio do `.gitignore`.

Consulte também [SECURITY.md](SECURITY.md).

## Autoria

Projeto autoral desenvolvido por **Anna Beatriz Gallo**, conectando conhecimentos de Segurança Cibernética ao contexto farmacêutico.
