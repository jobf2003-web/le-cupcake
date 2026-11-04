# Decisões técnicas e questões em aberto

- O projeto anterior definiu o produto como uma loja de cupcakes e apresentou 25 histórias, estimadas no backlog em **320 horas**. Outro trecho do mesmo PDF cita **332 horas**; a divergência deve ser revisada, não corrigida sem justificativa.
- Para este MVP foi adotado **Python/FastAPI** no back-end, em lugar de Flask anteriormente sugerido em conversa, por permitir testes de execução neste ambiente. Ambos são soluções em Python para aplicações web; a mudança deve constar na documentação acadêmica final.
- **Banco SQLite:** o esquema de 23 tabelas do planejamento foi preservado, acrescentando em `pedidos` as informações de telefone, endereço de entrega e token de consulta. Muitas tabelas representam funcionalidades futuras e permanecem sem uso no MVP.
- O projeto usa fotografias reais de terceiros provenientes do Wikimedia Commons, com autor, fonte e licença em docs/Referencias_Fotograficas_Simplificadas.docx; são fotos ilustrativas de outros cupcakes, não dos produtos da loja fictícia.
- Pagamentos são apenas registros de status `pendente`, sem captura de dados financeiros.
- A aplicação pode funcionar localmente, mas **não está hospedada**, nem contém URL pública de produção. GitHub, hospedagem com persistência, vídeos e cinco testes de aceitação reais precisam ser concluídos.
- O documento acadêmico em `Documentacao_ABNT.docx` foi produzido antes desta implementação e precisa de uma revisão final para descrever exatamente o que foi implementado e testado.
