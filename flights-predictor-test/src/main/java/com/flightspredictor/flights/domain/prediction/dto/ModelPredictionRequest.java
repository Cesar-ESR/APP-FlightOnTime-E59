package com.flightspredictor.flights.domain.prediction.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public record ModelPredictionRequest(

        @JsonProperty("year")
        Integer year,

        @JsonProperty("month")
        Integer month,

        @JsonProperty("day_of_month")
        Integer dayOfMonth,

        @JsonProperty("day_of_week")
        Integer dayOfWeek,

        @JsonProperty("dep_hour")
        Integer depHour,

        @JsonProperty("dep_minute")
        Integer depMinute,

        @JsonProperty("sched_minute_of_day")
        Integer schedMinuteOfDay,

        @JsonProperty("op_unique_carrier")
        String opUniqueCarrier,

        @JsonProperty("origin")
        String origin,

        @JsonProperty("dest")
        String dest,

        @JsonProperty("distance")
        Double distance,

        @JsonProperty("temp")
        Double temp,

        @JsonProperty("wind_spd")
        Double windSpd,

        @JsonProperty("precip_1h")
        Double precip1h,

        @JsonProperty("climate_severity_idx")
        Double climateSeverityIdx,

        @JsonProperty("dist_met_km")
        Double distMetKm,

        @JsonProperty("latitude")
        Double latitude,

        @JsonProperty("longitude")
        Double longitude
) {}
