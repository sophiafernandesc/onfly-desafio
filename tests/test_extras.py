"""Testes adicionais: cenários que os testes fornecidos não cobrem."""

import pytest
from helpers import PROJECT_ROOT, run_cli

from onfly_report.cli import main

RATES_PATH = PROJECT_ROOT / "data" / "taxas_cambio.csv"


def test_reads_all_reservations_beyond_200_rows(tmp_path):
    """O CLI deve ler o arquivo inteiro, sem limite fixo de linhas."""
    rows = [{"reservation_id": f"R-{i}"} for i in range(1, 251)]

    report = run_cli(tmp_path, rows)

    assert report["summary"]["total_reservations"] == 250
    assert report["summary"]["confirmed_reservations"] == 250
    assert report["summary"]["total_room_nights"] == 250
    assert report["summary"]["total_amount_brl"] == "25000.00"


def test_top_hotels_tie_is_broken_by_hotel_id_ascending(tmp_path):
    """Hotéis com o mesmo total são ordenados por hotel_id crescente."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H03", "hotel_name": "Hotel C", "amount": "500.00"},
            {"reservation_id": "R-2", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "500.00"},
            {"reservation_id": "R-3", "hotel_id": "H02", "hotel_name": "Hotel B", "amount": "900.00"},
        ],
    )

    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H02", "H01", "H03"]


def test_nights_across_year_boundary_with_multiple_rooms(tmp_path):
    """Virada de ano: 31/12 a 02/01 são 2 noites; com 2 quartos, 4 room nights."""
    report = run_cli(
        tmp_path,
        [{"checkin_date": "2024-12-31", "checkout_date": "2025-01-02", "rooms": "2"}],
    )

    assert report["summary"]["total_room_nights"] == 4
    assert report["by_month"][0]["month"] == "2024-12"


def test_money_is_rounded_half_up_only_on_serialization(tmp_path):
    """Soma exata e arredondamento half-up só no final."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "amount": "0.004"},
            {"reservation_id": "R-2", "amount": "0.001"},
        ],
    )

    # 0.004 + 0.001 = 0.005 -> "0.01"
    assert report["summary"]["total_amount_brl"] == "0.01"


def test_report_without_confirmed_reservations(tmp_path):
    """Sem CONFIRMED: totais zerados, média "0.00" e listas vazias."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "status": "CANCELLED"},
            {"reservation_id": "R-2", "status": "NO_SHOW"},
        ],
    )

    assert report["summary"]["total_reservations"] == 2
    assert report["summary"]["total_room_nights"] == 0
    assert report["summary"]["total_amount_brl"] == "0.00"
    assert report["summary"]["average_nightly_rate_brl"] == "0.00"
    assert report["by_month"] == []
    assert report["top_hotels"] == []


def test_invalid_top_exits_with_code_2():
    """--top menor que 1 é argumento inválido: código de saída 2."""
    with pytest.raises(SystemExit) as exit_info:
        main(["--input", str(PROJECT_ROOT / "data" / "reservas_hoteis.csv"), "--rates", str(RATES_PATH), "--top", "0"])

    assert exit_info.value.code == 2


def test_missing_input_file_exits_with_code_2(tmp_path):
    """Arquivo de entrada inexistente: código de saída 2."""
    code = main(
        [
            "--input", str(tmp_path / "nao-existe.csv"),
            "--rates", str(RATES_PATH),
            "--output", str(tmp_path / "report.json"),
        ]
    )

    assert code == 2


def test_currency_without_rate_exits_with_code_2(tmp_path):
    """Moeda sem taxa de câmbio é entrada inválida: código de saída 2."""
    input_path = tmp_path / "reservas.csv"
    input_path.write_text(
        "reservation_id,traveler_name,company_id,hotel_id,hotel_name,city,country,"
        "checkin_date,checkout_date,rooms,status,currency,amount,payment_method,booked_at\n"
        "R-1,Pessoa,EMP-001,H01,Hotel,Cidade,BR,2025-01-10,2025-01-11,1,CONFIRMED,GBP,100.00,PIX,"
        "2025-01-01T10:00:00-03:00\n",
        encoding="utf-8",
    )

    code = main(
        [
            "--input", str(input_path),
            "--rates", str(RATES_PATH),
            "--output", str(tmp_path / "report.json"),
        ]
    )

    assert code == 2