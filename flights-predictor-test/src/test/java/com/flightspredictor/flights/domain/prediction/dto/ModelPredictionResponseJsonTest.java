package com.flightspredictor.flights.domain.prediction.dto;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.flightspredictor.flights.domain.prediction.ENUM.Prevision;
import com.flightspredictor.flights.domain.prediction.ENUM.Status;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class ModelPredictionResponseJsonTest {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    void serializesUsingApiFieldNames() throws Exception {
        ModelPredictionResponse response = new ModelPredictionResponse(
                Prevision.ON_TIME,
                0.75,
                Status.MEDIUM
        );

        JsonNode json = objectMapper.readTree(objectMapper.writeValueAsBytes(response));

        assertThat(json.get("prediction").asText()).isEqualTo("ON TIME");
        assertThat(json.get("probability").asDouble()).isEqualTo(0.75);
        assertThat(json.get("threshold").asText()).isEqualTo("MEDIUM");
    }
}
