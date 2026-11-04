// Apenas melhorias na interface; preços oficiais são sempre calculados no servidor.
(function () {
  const inputs = document.querySelectorAll('input[name="opcao_entrega"]');
  const address = document.querySelector('#address-field');
  const total = document.querySelector('#order-total');
  const shipping = document.querySelector('#shipping-amount');
  const addressInput = document.querySelector('#endereco');
  function asCurrency(cents) { return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cents / 100); }
  function refresh() {
    const choice = document.querySelector('input[name="opcao_entrega"]:checked');
    if (!choice) return;
    const delivery = choice.dataset.type === 'entrega';
    if (address) address.hidden = !delivery;
    if (addressInput) addressInput.required = delivery;
    const cost = Number(choice.dataset.shipping || '0');
    if (shipping) shipping.textContent = asCurrency(cost);
    if (total) total.textContent = asCurrency(Number(total.dataset.subtotal || '0') + cost);
  }
  inputs.forEach(input => input.addEventListener('change', refresh));
  refresh();
})();
