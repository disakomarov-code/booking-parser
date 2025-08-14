package com.bookingparser;

import com.bookingparser.model.BookingRaw;
import com.bookingparser.normalize.NormalizerUtil;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.*;

public class NormalizeTest {
	@Test
	void testParseDateVariants() {
		assertEquals(LocalDate.of(2024,1,12), NormalizerUtil.parseDate("2024-01-12"));
		assertEquals(LocalDate.of(2024,1,12), NormalizerUtil.parseDate("12 Jan 2024"));
		assertEquals(LocalDate.of(2024,1,12), NormalizerUtil.parseDate("Jan 12, 2024"));
	}

	@Test
	void testParsePriceUsAndEu() {
		var p1 = NormalizerUtil.parsePrice("$1,234.56");
		assertEquals(1234.56, p1.value.doubleValue(), 0.001);
		assertEquals("USD", p1.currency);

		var p2 = NormalizerUtil.parsePrice("€ 1.234,56");
		assertEquals(1234.56, p2.value.doubleValue(), 0.001);
		assertEquals("EUR", p2.currency);

		var p3 = NormalizerUtil.parsePrice("Total: 999 CHF");
		assertEquals(999.0, p3.value.doubleValue(), 0.001);
		assertEquals("CHF", p3.currency);
	}

	@Test
	void testNormalizeBookingBasic() {
		BookingRaw raw = new BookingRaw(
			"Nice Hotel",
			"123 St, Paris, France",
			null,
			null,
			"2024-05-10",
			"2024-05-12",
			"Total EUR 250.00"
		);
		var norm = NormalizerUtil.normalize(raw);
		assertEquals("Paris", norm.getCity());
		assertEquals("France", norm.getCountry());
		assertEquals("2024-05-10", norm.getStartDate().toString());
		assertEquals("2024-05-12", norm.getEndDate().toString());
		assertEquals(250.0, norm.getTotalPrice().getValue().doubleValue(), 0.001);
		assertEquals("EUR", norm.getTotalPrice().getCurrency());
	}
}