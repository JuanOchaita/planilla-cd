import pytest
from planilla.calculo import (
    valor_hora,
    pago_horas_extra,
    salario_ordinario,
    bonificacion_incentivo,
    descuento_igss,
    isr_anual,
    descuento_isr,
    descuento_prestamo,
    liquidar,
    VALOR_BONIFICACION,
    TASA_IGSS,
    HORAS_JORNADA_MES,
    RECARGO_HORA_EXTRA,
    MAX_HORAS_EXTRA,
    DIAS_MES,
    DEDUCCION_ISR_ANUAL,
    TRAMO_ISR,
    TASA_ISR_TRAMO_1,
    TASA_ISR_TRAMO_2,
    ISR_ACUMULADO_TRAMO_1,
    FRACCION_INEMBARGABLE,
)


def test_valor_hora():
    assert valor_hora(HORAS_JORNADA_MES * 10) == pytest.approx(10.0)
    assert valor_hora(HORAS_JORNADA_MES * 20) == pytest.approx(20.0)
    assert valor_hora(HORAS_JORNADA_MES) == pytest.approx(1.0)


def test_pago_horas_extra():
    salario_base = HORAS_JORNADA_MES * 10
    assert pago_horas_extra(salario_base, 0) == pytest.approx(0.0)
    assert pago_horas_extra(salario_base, 24) == pytest.approx(10 * RECARGO_HORA_EXTRA * 24)
    assert pago_horas_extra(salario_base, MAX_HORAS_EXTRA) == pytest.approx(10 * RECARGO_HORA_EXTRA * MAX_HORAS_EXTRA)


def test_salario_ordinario():
    salario_base = HORAS_JORNADA_MES * 10
    assert salario_ordinario(salario_base, 0) == pytest.approx(salario_base)
    assert salario_ordinario(salario_base, 24) == pytest.approx(salario_base + 10 * RECARGO_HORA_EXTRA * 24)
    assert salario_ordinario(salario_base, MAX_HORAS_EXTRA) == pytest.approx(salario_base + 10 * RECARGO_HORA_EXTRA * MAX_HORAS_EXTRA)


def test_bonificacion_incentivo():
    assert bonificacion_incentivo(0) == pytest.approx(0.0)
    assert bonificacion_incentivo(DIAS_MES / 2) == pytest.approx(VALOR_BONIFICACION / 2)
    assert bonificacion_incentivo(DIAS_MES) == pytest.approx(VALOR_BONIFICACION)


def test_descuento_igss():
    assert descuento_igss(3120, True) == pytest.approx(3120 * TASA_IGSS)
    assert descuento_igss(3120, False) == pytest.approx(0.0)


def test_isr_anual():
    assert isr_anual(DEDUCCION_ISR_ANUAL) == pytest.approx(0.0)
    assert isr_anual(DEDUCCION_ISR_ANUAL - 1) == pytest.approx(0.0)
    assert isr_anual(DEDUCCION_ISR_ANUAL + 1) == pytest.approx(TASA_ISR_TRAMO_1 * 1)
    assert isr_anual(DEDUCCION_ISR_ANUAL + TRAMO_ISR) == pytest.approx(TASA_ISR_TRAMO_1 * TRAMO_ISR)
    assert isr_anual(DEDUCCION_ISR_ANUAL + TRAMO_ISR + 1) == pytest.approx(ISR_ACUMULADO_TRAMO_1 + TASA_ISR_TRAMO_2 * 1)
    assert isr_anual(DEDUCCION_ISR_ANUAL + TRAMO_ISR + 100000) == pytest.approx(ISR_ACUMULADO_TRAMO_1 + TASA_ISR_TRAMO_2 * 100000)


def test_descuento_isr():
    assert descuento_isr(DEDUCCION_ISR_ANUAL / 12) == pytest.approx(0.0)
    assert descuento_isr(10000) == pytest.approx(isr_anual(10000 * 12) / 12)
    assert descuento_isr(30000) == pytest.approx(isr_anual(30000 * 12) / 12)


def test_descuento_prestamo():
    assert descuento_prestamo(3000, 3000, 500) == pytest.approx(500.0)
    assert descuento_prestamo(1000, 3000, 500) == pytest.approx(1000 - FRACCION_INEMBARGABLE * 3000)
    assert descuento_prestamo(3000, 3000, 0) == pytest.approx(0.0)

def test_liquidar_afiliado_sin_prestamo():
    salario_base = 4800
    resultado = liquidar(
        salario_base=salario_base,
        horas_extra=0,
        dias_trabajados=DIAS_MES,
        afiliado_igss=True,
        cuota_prestamo=0.0,
    )
    ordinario = salario_ordinario(salario_base, 0)
    esperado = ordinario + VALOR_BONIFICACION - descuento_igss(ordinario, True) - descuento_isr(salario_base)
    assert resultado.liquido == pytest.approx(esperado)


def test_liquidar_no_afiliado():
    salario_base = 4800
    resultado = liquidar(
        salario_base=salario_base,
        horas_extra=0,
        dias_trabajados=DIAS_MES,
        afiliado_igss=False,
        cuota_prestamo=0.0,
    )
    ordinario = salario_ordinario(salario_base, 0)
    esperado = ordinario + VALOR_BONIFICACION - descuento_isr(salario_base)
    assert resultado.liquido == pytest.approx(esperado)


def test_liquidar_prestamo_limitado_por_piso():
    salario_base = 4800
    resultado = liquidar(
        salario_base=salario_base,
        horas_extra=0,
        dias_trabajados=DIAS_MES,
        afiliado_igss=True,
        cuota_prestamo=5000,
    )
    ordinario = salario_ordinario(salario_base, 0)
    liquido_antes = ordinario + VALOR_BONIFICACION - descuento_igss(ordinario, True) - descuento_isr(salario_base)
    prestamo_aplicado = min(5000, liquido_antes - FRACCION_INEMBARGABLE * ordinario)
    esperado = liquido_antes - prestamo_aplicado
    assert resultado.liquido == pytest.approx(esperado)
    assert resultado.liquido == pytest.approx(FRACCION_INEMBARGABLE * ordinario)