# Formato do payload

Formato demonstrativo:

```text
(01)GTIN(17)EXP(10)LOT<GS>(21)SERIAL<GS>(92)KID<GS>(91)SIGNATURE
```

Conteúdo coberto pela assinatura:

```text
(01)GTIN(17)EXP(10)LOT<GS>(21)SERIAL
```

Regras principais:

- GTIN: 14 dígitos;
- validade: `YYMMDD`;
- lote e serial: tamanho variável;
- `<GS>`: ASCII 29;
- KID: identificador derivado do certificado;
- assinatura: Base64url.

Este formato é customizado para a PoC e não representa uma implementação oficial do GS1 DataMatrix ou do SNCM.
