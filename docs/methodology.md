# Metodologia

1. Instalação das dependências em Kali Linux.
2. Criação de tokens separados para a CA e o fabricante.
3. Geração de pares de chaves RSA de 2048 bits dentro do SoftHSM.
4. Emissão de uma CA raiz e de um certificado de fabricante.
5. Geração de dados fictícios de medicamento.
6. Assinatura digital do payload base por PKCS#11.
7. Geração e decodificação do DataMatrix.
8. Verificação do cenário íntegro.
9. Alteração controlada do lote sem nova assinatura.
10. Verificação do cenário alterado.
