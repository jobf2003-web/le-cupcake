# Decisões técnicas e questões em aberto

- O projeto anterior definiu o produto como uma loja de cupcakes e apresentou 25 histórias, estimadas no backlog em **320 horas**. Outro trecho do mesmo PDF cita **332 horas**; a divergência deve ser revisada, não corrigida sem justificativa.
- Para o sistema foi adotado **Python/FastAPI** no back-end. A mudança em relação ao planejamento inicial deve constar na documentação acadêmica final.
- **Banco SQLite:** o esquema de 23 tabelas do planejamento foi preservado, acrescentando em `pedidos` as informações de telefone, endereço de entrega e token de consulta. Muitas tabelas representam funcionalidades futuras e permanecem sem uso no MVP.
- O projeto usa fotografias reais de terceiros provenientes do Wikimedia Commons, com autor, fonte e licença em docs/Referencias_Fotograficas_Simplificadas.docx; são fotos ilustrativas de outros cupcakes, não dos produtos da loja fictícia.
- Pagamentos são apenas registros de status `pendente`, sem captura de dados financeiros.
- A aplicação está disponível para demonstração em **https://le-cupcake.onrender.com/** e o código está em **https://github.com/jobf2003-web/le-cupcake**. A hospedagem gratuita pode usar armazenamento efêmero; persistência permanente do banco de dados ainda não está assegurada. Os dois vídeos foram gravados, e seus links de compartilhamento serão acrescentados quando disponibilizados.
- O documento acadêmico em `Documentacao_ABNT.docx` foi produzido antes da versão 0.2 e deve ser atualizado para refletir as funcionalidades e os 30 testes técnicos da aplicação.
