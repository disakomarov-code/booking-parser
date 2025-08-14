package com.bookingparser.normalize;

import com.bookingparser.model.BookingNormalized;
import com.bookingparser.model.BookingRaw;
import com.bookingparser.model.Price;

import java.math.BigDecimal;
import java.text.Normalizer;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class NormalizerUtil {
	private static final Map<String, String> SYMBOL_TO_CODE = new LinkedHashMap<>();
	static {
		SYMBOL_TO_CODE.put("$", "USD");
		SYMBOL_TO_CODE.put("€", "EUR");
		SYMBOL_TO_CODE.put("£", "GBP");
		SYMBOL_TO_CODE.put("CHF", "CHF");
		SYMBOL_TO_CODE.put("C$", "CAD");
		SYMBOL_TO_CODE.put("CA$", "CAD");
		SYMBOL_TO_CODE.put("A$", "AUD");
		SYMBOL_TO_CODE.put("AU$", "AUD");
		SYMBOL_TO_CODE.put("₺", "TRY");
		SYMBOL_TO_CODE.put("₽", "RUB");
		SYMBOL_TO_CODE.put("zł", "PLN");
		SYMBOL_TO_CODE.put("R$", "BRL");
		SYMBOL_TO_CODE.put("₹", "INR");
		SYMBOL_TO_CODE.put("¥", "JPY");
		SYMBOL_TO_CODE.put("₩", "KRW");
	}

	private static final Pattern PRICE_NUMERIC = Pattern.compile("(?<!\\d)(?:\\d{1,3}(?:[.,]\\d{3})+|\\d+)(?:[.,]\\d{2})?(?!\\d)");

	private static final List<DateTimeFormatter> DATE_FORMATS = Arrays.asList(
		DateTimeFormatter.ISO_LOCAL_DATE,
		DateTimeFormatter.ofPattern("d MMM uuuu"),
		DateTimeFormatter.ofPattern("MMM d, uuuu"),
		DateTimeFormatter.ofPattern("d MMMM uuuu"),
		DateTimeFormatter.ofPattern("MMM d uuuu")
	);

	public static LocalDate parseDate(String text) {
		String cleaned = text.trim();
		for (DateTimeFormatter fmt : DATE_FORMATS) {
			try { return LocalDate.parse(cleaned, fmt); } catch (DateTimeParseException ignored) {}
		}
		// try to extract a yyyy-mm-dd inside the string
		Matcher m = Pattern.compile("(\\d{4}-\\d{2}-\\d{2})").matcher(cleaned);
		if (m.find()) {
			return LocalDate.parse(m.group(1));
		}
		throw new IllegalArgumentException("Unable to parse date: " + text);
	}

	public static class ParsedPrice {
		public final BigDecimal value;
		public final String currency;
		public ParsedPrice(BigDecimal v, String c) { this.value = v; this.currency = c; }
	}

	private static String normalizeNumeric(String raw) {
		if (raw.contains(",") && raw.contains(".")) {
			int lastComma = raw.lastIndexOf(',');
			int lastDot = raw.lastIndexOf('.');
			if (lastComma > lastDot) {
				return raw.replace(".", "").replace(',', '.');
			} else {
				return raw.replace(",", "");
			}
		} else if (raw.contains(",")) {
			String[] parts = raw.split(",");
			if (parts[parts.length - 1].length() == 3 && Arrays.stream(parts).allMatch(p -> p.chars().allMatch(Character::isDigit))) {
				return String.join("", parts);
			} else {
				return raw.replace(',', '.');
			}
		} else {
			return raw;
		}
	}

	public static ParsedPrice parsePrice(String text) {
		String cleaned = text == null ? "" : text.trim();
		String currency = null;
		Matcher code = Pattern.compile("\\b([A-Z]{3})\\b").matcher(cleaned);
		if (code.find()) currency = code.group(1);
		for (Map.Entry<String,String> e : SYMBOL_TO_CODE.entrySet()) {
			if (cleaned.contains(e.getKey())) { if (currency == null) currency = e.getValue(); break; }
		}
		Matcher num = PRICE_NUMERIC.matcher(cleaned);
		if (!num.find()) throw new IllegalArgumentException("Unable to extract numeric price from: " + text);
		String normalized = normalizeNumeric(num.group(0));
		BigDecimal value = new BigDecimal(normalized);
		return new ParsedPrice(value, currency);
	}

	public static String[] extractCityCountry(String addressText, String explicitCity, String explicitCountry) {
		if (explicitCity != null && !explicitCity.isBlank() && explicitCountry != null && !explicitCountry.isBlank()) {
			return new String[] { explicitCity.trim(), explicitCountry.trim() };
		}
		String addr = addressText == null ? "" : addressText.trim();
		if (addr.isEmpty()) {
			return new String[] { explicitCity == null ? "" : explicitCity.trim(), explicitCountry == null ? "" : explicitCountry.trim() };
		}
		String[] parts = Arrays.stream(addr.split(",")).map(String::trim).filter(s -> !s.isEmpty()).toArray(String[]::new);
		if (parts.length >= 2) {
			return new String[] { parts[parts.length - 2], parts[parts.length - 1] };
		}
		if (parts.length == 1) return new String[] { parts[0], "" };
		return new String[] { explicitCity == null ? "" : explicitCity.trim(), explicitCountry == null ? "" : explicitCountry.trim() };
	}

	public static BookingNormalized normalize(BookingRaw raw) {
		LocalDate start = parseDate(raw.getStartDateText());
		LocalDate end = parseDate(raw.getEndDateText());
		ParsedPrice pp = parsePrice(raw.getTotalPriceText());
		String[] cc = extractCityCountry(raw.getAddressText(), raw.getCityText(), raw.getCountryText());
		return new BookingNormalized(cc[0], cc[1], raw.getHotelName().trim(), start, end, new Price(pp.value, pp.currency));
	}
}