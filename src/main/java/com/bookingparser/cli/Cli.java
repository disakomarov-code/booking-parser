package com.bookingparser.cli;

import com.bookingparser.export.Exporter;
import com.bookingparser.model.BookingNormalized;
import com.bookingparser.model.BookingRaw;
import com.bookingparser.normalize.NormalizerUtil;

import java.io.IOException;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class Cli {
	private static LocalDate parseDateOpt(String v) {
		if (v == null || v.isBlank()) return null;
		return LocalDate.parse(v);
	}

	private static List<BookingNormalized> filterByDate(List<BookingNormalized> list, LocalDate from, LocalDate to) {
		if (from == null && to == null) return list;
		List<BookingNormalized> out = new ArrayList<>();
		for (BookingNormalized b : list) {
			if (from != null && b.getStartDate().isBefore(from)) continue;
			if (to != null && b.getStartDate().isAfter(to)) continue;
			out.add(b);
		}
		return out;
	}

	public static void main(String[] args) throws IOException {
		String fromArg = null, toArg = null, outArg = "./bookings.csv", emailFallback = null;
		boolean headless = true, noHeadless = false, deleteCache = false, debug = false;
		for (int i = 0; i < args.length; i++) {
			String a = args[i];
			switch (a) {
				case "--from": fromArg = args[++i]; break;
				case "--to": toArg = args[++i]; break;
				case "--out": outArg = args[++i]; break;
				case "--headless": headless = true; break;
				case "--no-headless": noHeadless = true; headless = false; break;
				case "--delete-cache": deleteCache = true; break;
				case "--debug": debug = true; break;
				case "--email-fallback": emailFallback = args[++i]; break;
				case "-h": case "--help":
					System.out.println("Export Booking.com past reservations to CSV\n" +
						"Options:\n" +
						"  --from YYYY-MM-DD\n  --to YYYY-MM-DD\n  --out PATH\n  --headless | --no-headless\n  --delete-cache\n  --debug\n  --email-fallback PATH\n");
					return;
			}
		}

		Path storage = Path.of(".cache/session.json");
		if (deleteCache) {
			java.nio.file.Files.deleteIfExists(storage);
			System.out.println("Cache deleted");
			return;
		}

		String email = System.getenv("BOOKING_EMAIL");
		String password = System.getenv("BOOKING_PASSWORD");

		List<BookingRaw> raws = new ArrayList<>();
		if (emailFallback != null) {
			System.out.println("Email fallback parsing not implemented in this version.");
		} else {
			if (email == null || password == null) {
				System.err.println("BOOKING_EMAIL and BOOKING_PASSWORD must be set.");
				System.exit(2);
			}
			System.out.println("Scraping not implemented in Java version yet; producing empty output.");
			// TODO: implement Playwright-based scraping in Java similar to Python version.
		}

		List<BookingNormalized> normalized = new ArrayList<>();
		for (BookingRaw r : raws) {
			try { normalized.add(NormalizerUtil.normalize(r)); } catch (Exception ignored) {}
		}

		LocalDate from = parseDateOpt(fromArg);
		LocalDate to = parseDateOpt(toArg);
		normalized = filterByDate(normalized, from, to);

		Exporter.writeCsv(normalized, Path.of(outArg));
		System.out.println("Wrote " + normalized.size() + " rows to " + outArg);
	}
}