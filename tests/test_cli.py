from planilla.calculo import liquidar, resumen
from planilla.cli import parse_args, main, USO


def test_parse_args():
    assert parse_args(["salario_base=4000"]) == {"salario_base": 4000.0}
    assert parse_args(["salario_base=4000", "horas_extra=8"]) == {
        "salario_base": 4000.0,
        "horas_extra": 8.0,
    }
    assert parse_args(["afiliado_igss=si"]) == {"afiliado_igss": "si"}
    assert parse_args(["afiliado_igss=no"]) == {"afiliado_igss": "no"}
    assert parse_args(["sin_signo_igual"]) == {}
    assert parse_args([]) == {}


def test_main_sin_salario_base(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["planilla"])
    codigo = main()
    salida = capsys.readouterr().out
    assert codigo == 1
    assert USO in salida


def test_main_con_salario_base(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["planilla", "salario_base=4800"])
    codigo = main()
    salida = capsys.readouterr().out
    esperado = liquidar(
        salario_base=4800.0,
        horas_extra=0,
        dias_trabajados=30,
        afiliado_igss=True,
        cuota_prestamo=0.0,
    )
    assert codigo == 0
    assert salida == resumen(esperado) + "\n"


def test_main_con_todos_los_argumentos(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        [
            "planilla",
            "salario_base=4000",
            "horas_extra=8",
            "dias_trabajados=30",
            "cuota_prestamo=500",
            "afiliado_igss=si",
        ],
    )
    codigo = main()
    salida = capsys.readouterr().out
    esperado = liquidar(
        salario_base=4000.0,
        horas_extra=8.0,
        dias_trabajados=30.0,
        afiliado_igss=True,
        cuota_prestamo=500.0,
    )
    assert codigo == 0
    assert salida == resumen(esperado) + "\n"


def test_main_no_afiliado(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["planilla", "salario_base=4000", "afiliado_igss=no"],
    )
    codigo = main()
    salida = capsys.readouterr().out
    esperado = liquidar(
        salario_base=4000.0,
        horas_extra=0,
        dias_trabajados=30,
        afiliado_igss=False,
        cuota_prestamo=0.0,
    )
    assert codigo == 0
    assert salida == resumen(esperado) + "\n"