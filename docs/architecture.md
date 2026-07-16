# Arquitetura

A prova de conceito separa emissão e validação.

## Emissão

1. O fabricante demonstrativo gera GTIN, lote, validade e serial.
2. A chave privada do fabricante permanece no SoftHSM.
3. O payload base é assinado por meio da interface PKCS#11.
4. O KID e a assinatura são acrescentados ao payload.
5. O conteúdo final é codificado em DataMatrix.

## Validação

1. O verificador decodifica o DataMatrix.
2. O KID localiza o certificado correspondente.
3. A assinatura é verificada com a chave pública.
4. A cadeia pode ser validada até a CA raiz local.
5. O resultado é apresentado como `VÁLIDO` ou `INVÁLIDO`.

```text
Fabricante → SoftHSM/PKI → DataMatrix → Verificador → Resultado
```
