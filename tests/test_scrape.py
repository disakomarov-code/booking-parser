import os
import sys

# Ensure src is on path when running without installation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from booking_parser.scrape import extract_bookings_from_html


SAMPLE_HTML = """
<div class="card">
  <h2>Hotel Sunshine</h2>
  <div class="addr">Lisbon, Portugal</div>
  <div class="checkin">Check-in: 2023-09-01</div>
  <div class="checkout">Check-out: 2023-09-05</div>
  <div class="total">Total: € 450,00</div>
</div>
<div class="card">
  <h2>Mountain View Inn</h2>
  <div class="addr">Zermatt, Switzerland</div>
  <div class="checkin">Check-in: Sep 10, 2022</div>
  <div class="checkout">Check-out: Sep 12, 2022</div>
  <div class="total">Total: CHF 780</div>
</div>
"""


def test_extract_bookings_from_html():
    raws = extract_bookings_from_html(SAMPLE_HTML)
    assert len(raws) == 2
    assert raws[0].hotel_name == "Hotel Sunshine"
    assert "Lisbon" in raws[0].address_text
    assert "€" in raws[0].total_price_text