package com.flightspredictor.flights.domain.prediction.ENUM;

public enum Prevision {
    DELAYED("DELAYED"),
    ON_TIME("ON TIME");

    private final String label;

    Prevision(String label) {
        this.label = label;
    }

    @com.fasterxml.jackson.annotation.JsonValue
    public String getLabel() {
        return label;
    }
}
