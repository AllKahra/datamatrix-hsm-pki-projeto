# Limitações

- A assinatura valida o conteúdo digital, não o medicamento físico.
- A cópia integral de um payload válido pode continuar passando na verificação.
- O SoftHSM não oferece as proteções físicas de um HSM de produção.
- A PoC não implementa revogação por CRL ou OCSP.
- O registro opcional de leituras é exploratório e não comprova clonagem.
- O formato do payload é customizado e exige governança para interoperabilidade.
- A integração usa o engine PKCS#11 do OpenSSL; providers devem ser avaliados em futuras versões.
