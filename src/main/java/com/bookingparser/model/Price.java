package com.bookingparser.model;

import java.math.BigDecimal;
import java.util.Objects;

public class Price {
	private final BigDecimal value;
	private final String currency; // nullable

	public Price(BigDecimal value, String currency) {
		this.value = value;
		this.currency = currency;
	}

	public BigDecimal getValue() {
		return value;
	}

	public String getCurrency() {
		return currency;
	}

	@Override
	public String toString() {
		if (currency == null || currency.isBlank()) {
			return value.toPlainString();
		}
		return value.toPlainString() + " " + currency;
	}

	@Override
	public boolean equals(Object o) {
		if (this == o) return true;
		if (!(o instanceof Price)) return false;
		Price price = (Price) o;
		return Objects.equals(value, price.value) && Objects.equals(currency, price.currency);
	}

	@Override
	public int hashCode() {
		return Objects.hash(value, currency);
	}
}