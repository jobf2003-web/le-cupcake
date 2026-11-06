// Apenas melhorias na interface; preços oficiais são sempre calculados no servidor.
(function () {
  const inputs = document.querySelectorAll('input[name="opcao_entrega"]');
  const address = document.querySelector('#address-field');
  const total = document.querySelector('#order-total');
  const shipping = document.querySelector('#shipping-amount');
  const addressInput = document.querySelector('#endereco');
  const deliveryGuidance = document.querySelector('#delivery-guidance');
  const cepField = document.querySelector('#cep-field');
  const cepInput = document.querySelector('#cep');
  const quoteError = document.querySelector('#shipping-error');
  const scheduleField = document.querySelector('#schedule-fields');
  const scheduleDate = document.querySelector('#data-agendada');
  const scheduleWindow = document.querySelector('#janela-entrega');
  let quoteSeq = 0;
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
    if (cepField) cepField.hidden = !delivery;
    if (cepInput) {
      cepInput.disabled = !delivery;
      cepInput.required = delivery && cepInput.dataset.regionRequired === '1';
    }
    if (scheduleField && scheduleWindow) {
      const matched = Array.from(scheduleWindow.querySelectorAll('option[data-option]'))
        .filter(option => option.dataset.option === choice.value);
      const hasSchedule = matched.length > 0;
      scheduleField.hidden = !hasSchedule;
      if (scheduleDate) { scheduleDate.disabled = !hasSchedule; scheduleDate.required = hasSchedule; }
      scheduleWindow.disabled = !hasSchedule;
      scheduleWindow.required = hasSchedule;
      scheduleWindow.querySelectorAll('option[data-option]').forEach(option => {
        option.hidden = option.dataset.option !== choice.value;
        option.disabled = option.dataset.option !== choice.value;
      });
      if (scheduleWindow.selectedOptions.length && scheduleWindow.selectedOptions[0].disabled)
        scheduleWindow.value = '';
    }
    const requestId = ++quoteSeq;
    const baseCost = delivery ? Number(choice.dataset.shipping || '0') : 0;
    if (shipping) shipping.textContent = asCurrency(baseCost);
    if (total) total.textContent = asCurrency(Number(total.dataset.subtotal || '0') + baseCost);
    if (quoteError) quoteError.textContent = '';
    if (delivery && cepInput && cepInput.dataset.regionRequired === '1' && cepInput.value.replace(/\D/g, '').length !== 8) {
      if (quoteError) quoteError.textContent = 'Informe o CEP para calcular o frete pela região.';
      return;
    }
    const params = new URLSearchParams({ opcao_entrega: choice.value, cep: cepInput ? cepInput.value : '' });
    fetch('/api/frete?' + params.toString()).then(async response => {
      const payload = await response.json();
      if (requestId !== quoteSeq) return;
      if (!response.ok) throw new Error(payload.detail || 'Não foi possível calcular o frete.');
      const fee = payload.frete_centavos;
      if (shipping) shipping.textContent = asCurrency(fee);
      if (total) total.textContent = asCurrency(Number(total.dataset.subtotal || '0') + fee);
    }).catch(error => { if (requestId === quoteSeq && quoteError) quoteError.textContent = error.message; });
  }
  inputs.forEach(input => input.addEventListener('change', refresh));
  if (cepInput) cepInput.addEventListener('input', function () { clearTimeout(cepInput._debounce); cepInput._debounce = setTimeout(refresh, 350); });
  if (scheduleDate) {
    const today = new Date();
    const localDate = day => { const x = new Date(today.getFullYear(),today.getMonth(),today.getDate()+day); return x.getFullYear()+'-'+String(x.getMonth()+1).padStart(2,'0')+'-'+String(x.getDate()).padStart(2,'0'); };
    scheduleDate.min = localDate(0); scheduleDate.max = localDate(15);
  }
  refresh();

  // Em um formulário com erro, apresenta as orientações antes do reenvio.
  const checkoutErrors = document.querySelector('#checkout-errors');
  if (checkoutErrors) checkoutErrors.focus();

  // As fotos são mantidas intactas. Somente quando a origem externa falha,
  // exibe-se uma identificação textual no mesmo espaço da imagem.
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

  // US-14: o preço visual é estimativo; o servidor recalcula cada componente e estoque.
  const comboBuilder = document.querySelector('#combo-builder');
  if (comboBuilder) {
    const fields = comboBuilder.querySelectorAll('.combo-quantity');
    function updateComboTotal() {
      let qty=0, cents=0;
      fields.forEach(input => { const q=Math.max(0,Number(input.value)||0);qty+=q;cents+=q*Number(input.dataset.price||0); });
      const value=comboBuilder.querySelector('#combo-total');
      const count=comboBuilder.querySelector('#combo-count');
      if (value) value.textContent=asCurrency(cents);
      if (count) count.textContent=String(qty);
    }
    fields.forEach(input=>input.addEventListener('input',updateComboTotal));
    updateComboTotal();
  }

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

  // US-06/19: consulta de estado sem expor informações pessoais no endpoint.
  const orderTracking = document.querySelector('#pedido-acompanhamento');
  if (orderTracking) {
    const token = orderTracking.dataset.orderToken;
    const statusTarget = document.querySelector('#pedido-status-atual');
    const etaTarget = document.querySelector('#pedido-previsao');
    const timeline = document.querySelector('#pedido-eventos');
    const freshness = document.querySelector('#pedido-atualizacao');
    async function refreshOrder() {
      if (document.hidden) return;
      try {
        const response = await fetch('/api/pedido/' + encodeURIComponent(token) + '/status', { cache:'no-store' });
        if (!response.ok) throw new Error('Falha na atualização');
        const data = await response.json();
        if (statusTarget) statusTarget.textContent = data.status_nome;
        if (etaTarget) etaTarget.textContent = data.previsao_entrega_em || 'Ainda não informada';
        if (timeline) {
          timeline.replaceChildren();
          for (const event of data.eventos) {
            const li = document.createElement('li');
            li.textContent = event.data + ' — ' + event.status;
            timeline.appendChild(li);
          }
        }
        if (freshness) freshness.textContent = 'Consulta atualizada dentro do site. O envio por e-mail/SMS não está habilitado.';
      } catch (error) {
        if (freshness) freshness.textContent = 'Não foi possível atualizar o pedido. Tente novamente mais tarde.';
      }
    }
    refreshOrder();
    const tick = setInterval(refreshOrder, 15000);
    window.addEventListener('pagehide', function () { clearInterval(tick); }, { once:true });
  }

  // US-18: alternância acessível entre unidades e valor bruto nos gráficos locais.
  const chart = document.querySelector('#report-bars');
  if (chart) {
    const units = document.querySelector('#report-show-units');
    const amount = document.querySelector('#report-show-value');
    function asMoney(value) { return asCurrency(value); }
    function showMetric(type) {
      chart.querySelectorAll('.report-bar-row').forEach(function (row) {
        const value = Number(type === 'units' ? row.dataset.units : row.dataset.amount);
        const max = Number(type === 'units' ? row.dataset.maxUnits : row.dataset.maxAmount);
        const fill = row.querySelector('.report-bar-fill');
        const label = row.querySelector('.report-bar-value');
        if (fill) fill.style.width = max ? (value * 100 / max) + '%' : '0%';
        if (label) label.textContent = type === 'units' ? value + ' un.' : asMoney(value);
      });
      if (units) { units.setAttribute('aria-pressed', String(type==='units')); units.classList.toggle('btn-primary',type==='units'); units.classList.toggle('btn-outline',type!=='units'); }
      if (amount) { amount.setAttribute('aria-pressed', String(type==='amount')); amount.classList.toggle('btn-primary',type==='amount'); amount.classList.toggle('btn-outline',type!=='amount'); }
    }
    if (units) units.addEventListener('click',function(){showMetric('units');});
    if (amount) amount.addEventListener('click',function(){showMetric('amount');});
  }
})();
