package com.flightspredictor.flights.domain.airports.exceptions;

public class AirportNotFoundException extends RuntimeException {
    public AirportNotFoundException(String message) {
        super(message);
    }
}
