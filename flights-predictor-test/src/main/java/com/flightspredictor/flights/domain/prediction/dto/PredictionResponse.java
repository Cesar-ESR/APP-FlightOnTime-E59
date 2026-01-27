package com.flightspredictor.flights.domain.prediction.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public record PredictionResponse(
        @JsonProperty("prevision")
        String prevision,

        @JsonProperty("probabilidad")
        Double probabilidad,

        @JsonProperty("confianza")
        String confianza
) {
}
