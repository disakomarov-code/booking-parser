package com.bookingparser.export;

import com.bookingparser.model.BookingNormalized;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

import java.io.IOException;
import java.io.Writer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class Exporter {
	public static final String[] HEADER = new String[] {
		"City","Country","Hotel name","Start date","End date","Total price of booking"
	};

	public static Path writeCsv(List<BookingNormalized> bookings, Path output) throws IOException {
		Files.createDirectories(output.getParent());
		try (Writer w = Files.newBufferedWriter(output);
		     CSVPrinter printer = new CSVPrinter(w, CSVFormat.DEFAULT.builder().setHeader(HEADER).build())) {
			for (BookingNormalized b : bookings) {
				printer.printRecord((Object[]) b.toCsvRow());
			}
		}
		return output;
	}
}