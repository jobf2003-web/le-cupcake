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
  function setupPhotoFallbacks(root) {
    root.querySelectorAll(photoSelector).forEach(function (photo) {
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
  }
  setupPhotoFallbacks(document);

  // US-02: filtros combinados e busca dinâmica, sem recarga; GET permanece como fallback sem JS.
  const form = document.querySelector('#catalogo-filtro');
  const results = document.querySelector('#catalogo-resultados');
  const chips = document.querySelector('#catalogo-categorias');
  const status = document.querySelector('#catalogo-status');
  const counter = document.querySelector('#catalogo-contagem');
  const clear = document.querySelector('#catalogo-limpar');
  if (form && results && chips) {
    const search = form.querySelector('input[name="busca"]');
    const hiddenCategory = form.querySelector('input[name="categoria"]');
    let category = hiddenCategory.value || '';
    let pending = null;
    let debounce;
    async function updateCatalog() {
      if (pending) pending.abort();
      const current = new AbortController();
      pending = current;
      const params = new URLSearchParams();
      const query = search.value.trim().slice(0, 80);
      if (query) params.set('busca', query);
      if (category) params.set('categoria', category);
      const queryString = params.toString();
      const url = '/catalogo/resultados' + (queryString ? '?' + queryString : '');
      const fallback = '/' + (queryString ? '?' + queryString : '') + '#cardapio';
      results.setAttribute('aria-busy', 'true');
      if (status) status.textContent = 'Atualizando resultados...';
      try {
        const response = await fetch(url, { signal: current.signal, headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        if (!response.ok) throw new Error('Falha ao consultar o catálogo');
        const html = await response.text();
        if (current.signal.aborted) return;
        results.innerHTML = html;
        const number = Number(response.headers.get('X-Total-Results') || '0');
        if (counter) counter.textContent = number + ' sabor(es) encontrado(s)';
        if (status) status.textContent = number + ' sabor(es) encontrado(s).';
        hiddenCategory.value = category;
        chips.querySelectorAll('a.chip').forEach(function (chip) {
          const targetCategory = new URL(chip.href, location.origin).searchParams.get('categoria') || '';
          chip.classList.toggle('active', targetCategory === category);
        });
        if (clear) clear.hidden = !query && !category;
        history.replaceState(null, '', fallback);
        setupPhotoFallbacks(results);
      } catch (error) {
        if (error.name !== 'AbortError') location.assign(fallback);
      } finally {
        if (pending === current) {
          pending = null;
          results.setAttribute('aria-busy', 'false');
        }
      }
    }
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      clearTimeout(debounce);
      updateCatalog();
    });
    search.addEventListener('input', function () {
      clearTimeout(debounce);
      debounce = setTimeout(updateCatalog, 280);
    });
    chips.addEventListener('click', function (event) {
      const chip = event.target.closest('a.chip');
      if (!chip) return;
      event.preventDefault();
      category = new URL(chip.href, location.origin).searchParams.get('categoria') || '';
      clearTimeout(debounce);
      updateCatalog();
    });
    if (clear) clear.addEventListener('click', function (event) {
      event.preventDefault();
      category = '';
      search.value = '';
      clearTimeout(debounce);
      updateCatalog();
    });
  }
})();
