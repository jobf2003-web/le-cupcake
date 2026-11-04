// Apenas melhorias na interface; preços oficiais são sempre calculados no servidor.
(function () {
  const inputs = document.querySelectorAll('input[name="opcao_entrega"]');
  const address = document.querySelector('#address-field');
  const total = document.querySelector('#order-total');
  const shipping = document.querySelector('#shipping-amount');
  const addressInput = document.querySelector('#endereco');
  const deliveryGuidance = document.querySelector('#delivery-guidance');
  function asCurrency(cents) { return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cents / 100); }
  function refresh() {
    const choice = document.querySelector('input[name="opcao_entrega"]:checked');
    if (!choice) return;
    const delivery = choice.dataset.type === 'entrega';
    if (address) address.hidden = !delivery;
    if (addressInput) {
      addressInput.required = delivery;
      addressInput.disabled = !delivery;
      addressInput.setAttribute('aria-required', String(delivery));
    }
    if (deliveryGuidance) deliveryGuidance.textContent = delivery
      ? 'Entrega selecionada. Preencha o endereço completo para concluir o pedido.'
      : 'Retirada selecionada. Não é necessário informar endereço.';
    const cost = Number(choice.dataset.shipping || '0');
    if (shipping) shipping.textContent = asCurrency(cost);
    if (total) total.textContent = asCurrency(Number(total.dataset.subtotal || '0') + cost);
  }
  inputs.forEach(input => input.addEventListener('change', refresh));
  refresh();
  const checkoutErrors = document.querySelector('#checkout-errors');
  if (checkoutErrors) checkoutErrors.focus();

  // Mantém as fotografias originais quando disponíveis.
  // Se a origem externa falhar, informa a indisponibilidade no mesmo espaço.
  const photoSelector = 'img.hero-photo, img.product-photo, img.detail-photo, img.cart-photo, img.admin-thumb, img.recommendation-photo';
  document.querySelectorAll(photoSelector).forEach(function (photo) {
    function showFallback() {
      if (!photo.isConnected) return;
      const fallback = document.createElement('span');
      fallback.className = photo.classList.contains('admin-thumb') ? 'photo-fallback photo-fallback-small' : 'photo-fallback';
      fallback.setAttribute('role', 'img');
      fallback.setAttribute('aria-label', photo.alt ? photo.alt + '. Fotografia indisponível.' : 'Fotografia indisponível.');
      fallback.textContent = 'Fotografia indisponível';
      photo.replaceWith(fallback);
    }
    photo.addEventListener('error', showFallback, { once: true });
    if (photo.complete && photo.naturalWidth === 0) showFallback();
  });
})();
