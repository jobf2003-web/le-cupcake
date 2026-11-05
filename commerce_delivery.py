"""Regras de entrega/retirada locais da Le Cupcake 0.2.

Frete por FAIXA DE CEP definida pelo administrador, sem API de transportadora,
e agenda demonstrativa. Validado sempre novamente dentro da transação do pedido.
"""
from __future__ import annotations

import re
from datetime import date, timedelta
import sqlite3


def cep_normalizado(value: str) -> str:
    digits = re.sub(r'\D', '', str(value or ''))
    if len(digits) != 8 or not re.fullmatch(r'[\d.\s-]*', str(value or '')):
        raise ValueError('Informe um CEP válido com oito dígitos.')
    return digits


def frete_por_regiao(db: sqlite3.Connection, metodo: sqlite3.Row, cep: str) -> tuple[int, int | None]:
    """Retorna frete e ID da região. Sem regiões, mantém taxa fixa demonstrativa legada."""
    if metodo['tipo'] == 'retirada':
        return 0, None
    count = db.execute('SELECT COUNT(*) FROM regioes_entrega WHERE ativa=1').fetchone()[0]
    if count == 0:
        return int(metodo['custo_base_centavos']), None
    parsed = cep_normalizado(cep)
    regiao = db.execute('''SELECT id,taxa_adicional_centavos FROM regioes_entrega
        WHERE ativa=1 AND cep_inicio<=? AND cep_fim>=? ORDER BY id LIMIT 1''', (parsed, parsed)).fetchone()
    if not regiao:
        raise ValueError('CEP fora das regiões de entrega cadastradas. Escolha retirada ou outro endereço.')
    return int(metodo['custo_base_centavos']) + int(regiao['taxa_adicional_centavos']), regiao['id']


def validar_agenda(db: sqlite3.Connection, metodo_id: int, data_str: str, janela_id: int) -> tuple[str | None, int | None]:
    janelas = db.execute('SELECT COUNT(*) FROM janelas_entrega WHERE opcao_entrega_id=?', (metodo_id,)).fetchone()[0]
    if not janelas:
        if data_str or janela_id:
            raise ValueError('A modalidade selecionada ainda não possui horários de agendamento.')
        return None, None
    if not data_str or not janela_id:
        raise ValueError('Escolha a data e o horário de entrega ou retirada.')
    try:
        data = date.fromisoformat(data_str)
    except ValueError:
        raise ValueError('Data de agendamento inválida.') from None
    if data < date.today() or data > date.today() + timedelta(days=15):
        raise ValueError('Agendamento disponível de hoje até 15 dias adiante.')
    bloqueio = db.execute('''SELECT 1 FROM agenda_bloqueios WHERE opcao_entrega_id=? AND data=?''',
                         (metodo_id, data.isoformat())).fetchone()
    if bloqueio:
        raise ValueError('Não há atendimento na data selecionada.')
    janela = db.execute('''SELECT capacidade FROM janelas_entrega WHERE id=? AND opcao_entrega_id=?''',
                        (janela_id, metodo_id)).fetchone()
    if not janela or janela['capacidade'] <= 0:
        raise ValueError('Horário indisponível para a modalidade selecionada.')
    ocupacao = db.execute('''SELECT COUNT(*) FROM pedidos WHERE janela_entrega_id=? AND agendado_para=?
        AND status!='cancelado' ''', (janela_id, data.isoformat())).fetchone()[0]
    if ocupacao >= int(janela['capacidade']):
        raise ValueError('O horário selecionado esgotou sua capacidade.')
    return data.isoformat(), janela_id
