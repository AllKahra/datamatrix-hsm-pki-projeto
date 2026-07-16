# Limitações

- A assinatura valida o conteúdo digital, não o medicamento físico.
- A cópia integral de um payload válido pode continuar passando na verificação.
- O SoftHSM não oferece as mesmas proteções físicas de um HSM de produção.
- A PoC não implementa revogação por CRL ou OCSP.
- O registro opcional de leituras é apenas exploratório e não comprova clonagem.
- A arquitetura usa o engine PKCS#11 do OpenSSL; providers devem ser avaliados em uma evolução futura.
