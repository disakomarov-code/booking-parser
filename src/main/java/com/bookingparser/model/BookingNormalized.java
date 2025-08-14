package com.bookingparser.model;

import java.time.LocalDate;

public class BookingNormalized {
	private final String city;
	private final String country;
	private final String hotelName;
	private final LocalDate startDate;
	private final LocalDate endDate;
	private final Price totalPrice;

	public BookingNormalized(String city, String country, String hotelName,
	                        LocalDate startDate, LocalDate endDate, Price totalPrice) {
		this.city = city;
		this.country = country;
		this.hotelName = hotelName;
		this.startDate = startDate;
		this.endDate = endDate;
		this.totalPrice = totalPrice;
	}

	public String getCity() { return city; }
	public String getCountry() { return country; }
	public String getHotelName() { return hotelName; }
	public LocalDate getStartDate() { return startDate; }
	public LocalDate getEndDate() { return endDate; }
	public Price getTotalPrice() { return totalPrice; }

	public String[] toCsvRow() {
		return new String[] {
			city,
			country,
			hotelName,
			startDate.toString(),
			endDate.toString(),
			totalPrice.toString()
		};
	}
}