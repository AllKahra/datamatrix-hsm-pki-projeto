# Metodologia

1. Instalar as dependências com `setup.sh`.
2. Criar tokens separados para CA e fabricante.
3. Gerar chaves RSA dentro do SoftHSM.
4. Emitir o certificado raiz e o certificado do fabricante.
5. Gerar GTIN, lote, validade e serial demonstrativos.
6. Assinar o payload base via PKCS#11.
7. Gerar e decodificar o DataMatrix.
8. Testar um cenário íntegro e um cenário alterado.
