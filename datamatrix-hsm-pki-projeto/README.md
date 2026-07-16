# PKI + HSM + DataMatrix para dados de medicamentos

Prova de conceito que aplica assinatura digital, PKI e SoftHSM à validação de dados associados a medicamentos.

## O que o projeto demonstra

- geração de dados demonstrativos de medicamento;
- assinatura do payload com chave privada protegida no SoftHSM;
- transporte dos dados e da assinatura em DataMatrix;
- verificação da assinatura e da cadeia de confiança;
- detecção de alteração do conteúdo assinado.

## O que o projeto não afirma

- não comprova a autenticidade física do medicamento;
- não impede a cópia integral de um DataMatrix válido;
- não substitui o SNCM ou sistemas regulatórios;
- não entrega rastreabilidade completa sem backend e regras de negócio.

## Estrutura

```text
.
├── config/           # Configurações estáticas da PKI
├── docs/             # Arquitetura, metodologia e limitações
├── examples/         # Entradas demonstrativas seguras
├── scripts/          # Fluxo principal em Python
├── tests/            # Verificações rápidas
├── output/           # Artefatos gerados localmente e ignorados pelo Git
├── setup.sh          # Instala dependências e cria o ambiente
├── rebuild_lab.sh    # Reconstrói HSM, PKI, dados e DataMatrix
├── run_demo.sh       # Executa os cenários válido e alterado
└── env.sh            # Carrega variáveis locais
```

## Início rápido

```bash
git clone https://github.com/AllKahra/poc-pharma-gs1-hsm.git
cd poc-pharma-gs1-hsm

bash setup.sh --clean
source .venv/bin/activate
source env.sh
bash run_demo.sh
```

## Resultado esperado

Cenário original:

```text
[RESULTADO] VÁLIDO
```

Cenário com lote alterado sem nova assinatura:

```text
[RESULTADO] INVÁLIDO
Motivo: assinatura inválida ou conteúdo alterado.
```

## Scripts principais

| Script | Função |
|---|---|
| `generate_data.py` | Gera GTIN, lote, validade e serial demonstrativos |
| `sign_payload.py` | Assina o conteúdo via PKCS#11 e monta o payload |
| `generate_datamatrix.py` | Gera e valida a imagem DataMatrix |
| `verify_datamatrix.py` | Verifica assinatura, certificado e cadeia |

## Documentação

- [Arquitetura](docs/architecture.md)
- [Metodologia](docs/methodology.md)
- [Formato do payload](docs/payload-format.md)
- [Modelo de ameaça](docs/threat-model.md)
- [Limitações](docs/limitations.md)

## Aviso de segurança

Os PINs padrão são exclusivamente demonstrativos. Tokens, chaves, certificados gerados, payloads e imagens ficam em `output/` e não devem ser versionados.
