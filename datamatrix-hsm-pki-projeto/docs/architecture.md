# Arquitetura

A prova de conceito separa o fluxo em dois domínios:

1. **Emissão e assinatura**
   - gera os dados demonstrativos;
   - assina o conteúdo com a chave privada do fabricante no SoftHSM;
   - adiciona KID e assinatura ao payload;
   - gera o DataMatrix.

2. **Leitura e validação**
   - decodifica o DataMatrix;
   - localiza o certificado pelo KID;
   - verifica a assinatura;
   - valida opcionalmente a cadeia até a CA raiz.

```text
Dados → Assinatura no HSM → DataMatrix → Verificação → Válido/Inválido
```
