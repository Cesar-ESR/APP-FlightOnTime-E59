package com.flightspredictor.flights.infra.weather.dto.external;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public record WeatherApiResponse(
        Location location,
        Current current
) {
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Location(
            String name,
            String country,
            @JsonProperty("lat") Double latitude,
            @JsonProperty("lon") Double longitude,
            @JsonProperty("localtime") String localtime
    ) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Current(
            @JsonProperty("temp_c") Double temperatureCelsius,
            @JsonProperty("humidity") Integer humidityPercentage,
            @JsonProperty("wind_kph") Double windSpeedKmh,
            @JsonProperty("pressure_mb") Double pressureMb,
            @JsonProperty("last_updated") String lastUpdated
    ) {}
}
