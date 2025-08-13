package com.bookingparser.model;

public class BookingRaw {
	private final String hotelName;
	private final String addressText; // nullable
	private final String cityText;    // nullable
	private final String countryText; // nullable
	private final String startDateText;
	private final String endDateText;
	private final String totalPriceText;

	public BookingRaw(String hotelName, String addressText, String cityText, String countryText,
	                 String startDateText, String endDateText, String totalPriceText) {
		this.hotelName = hotelName;
		this.addressText = addressText;
		this.cityText = cityText;
		this.countryText = countryText;
		this.startDateText = startDateText;
		this.endDateText = endDateText;
		this.totalPriceText = totalPriceText;
	}

	public String getHotelName() { return hotelName; }
	public String getAddressText() { return addressText; }
	public String getCityText() { return cityText; }
	public String getCountryText() { return countryText; }
	public String getStartDateText() { return startDateText; }
	public String getEndDateText() { return endDateText; }
	public String getTotalPriceText() { return totalPriceText; }
}