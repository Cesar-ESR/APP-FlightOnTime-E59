package com.flightspredictor.flights.domain.prediction.dto;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class ModelPredictionRequestJsonTest {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    void serializesUsingDsFieldNames() throws Exception {
        ModelPredictionRequest request = new ModelPredictionRequest(
                2000,
                1,
                1,
                6,
                23,
                0,
                1380,
                "AA",
                "JFK",
                "LAX",
                1440.0,
                10.5,
                5.0,
                0.2,
                1.1,
                2.2,
                40.7,
                -73.9
        );

        JsonNode json = objectMapper.readTree(objectMapper.writeValueAsBytes(request));

        assertThat(json.get("year").asInt()).isEqualTo(2000);
        assertThat(json.get("month").asInt()).isEqualTo(1);
        assertThat(json.get("day_of_month").asInt()).isEqualTo(1);
        assertThat(json.get("day_of_week").asInt()).isEqualTo(6);
        assertThat(json.get("dep_hour").asInt()).isEqualTo(23);
        assertThat(json.get("dep_minute").asInt()).isEqualTo(0);
        assertThat(json.get("sched_minute_of_day").asInt()).isEqualTo(1380);
        assertThat(json.get("op_unique_carrier").asText()).isEqualTo("AA");
        assertThat(json.get("origin").asText()).isEqualTo("JFK");
        assertThat(json.get("dest").asText()).isEqualTo("LAX");
        assertThat(json.get("distance").asDouble()).isEqualTo(1440.0);
        assertThat(json.get("temp").asDouble()).isEqualTo(10.5);
        assertThat(json.get("wind_spd").asDouble()).isEqualTo(5.0);
        assertThat(json.get("precip_1h").asDouble()).isEqualTo(0.2);
        assertThat(json.get("climate_severity_idx").asDouble()).isEqualTo(1.1);
        assertThat(json.get("dist_met_km").asDouble()).isEqualTo(2.2);
        assertThat(json.get("latitude").asDouble()).isEqualTo(40.7);
        assertThat(json.get("longitude").asDouble()).isEqualTo(-73.9);
    }
}
