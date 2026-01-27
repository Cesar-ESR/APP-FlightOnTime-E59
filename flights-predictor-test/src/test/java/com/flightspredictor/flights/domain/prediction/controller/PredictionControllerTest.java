package com.flightspredictor.flights.domain.prediction.controller;

import com.flightspredictor.flights.domain.prediction.ENUM.Prevision;
import com.flightspredictor.flights.domain.prediction.ENUM.Status;
import com.flightspredictor.flights.domain.prediction.dto.ModelPredictionResponse;
import com.flightspredictor.flights.domain.prediction.service.PredictionService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(PredictionController.class)
class PredictionControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private PredictionService predictionService;

    @Test
    void predictReturnsModelResponse() throws Exception {
        ModelPredictionResponse response = new ModelPredictionResponse(
                Prevision.ON_TIME,
                0.88,
                Status.LOW
        );

        given(predictionService.predict(any())).willReturn(response);

        String payload = """
                {
                  "fl_date": "2030-01-01T10:15:30Z",
                  "op_unique_carrier": "AA",
                  "origin": "JFK",
                  "dest": "LAX"
                }
                """;

        mockMvc.perform(post("/predict")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.prediction").value("ON TIME"))
                .andExpect(jsonPath("$.probability").value(0.88))
                .andExpect(jsonPath("$.threshold").value("LOW"));
    }

    @Test
    void predictRejectsInvalidCarrierCode() throws Exception {
        String payload = """
                {
                  "fl_date": "2030-01-01T10:15:30Z",
                  "op_unique_carrier": "A",
                  "origin": "JFK",
                  "dest": "LAX"
                }
                """;

        mockMvc.perform(post("/predict")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isBadRequest());
    }

    @Test
    void predictRejectsInvalidOriginFormat() throws Exception {
        String payload = """
                {
                  "fl_date": "2030-01-01T10:15:30Z",
                  "op_unique_carrier": "AA",
                  "origin": "JFK1",
                  "dest": "LAX"
                }
                """;

        mockMvc.perform(post("/predict")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isBadRequest());
    }

    @Test
    void predictRejectsPastFlightDate() throws Exception {
        String payload = """
                {
                  "fl_date": "2000-01-01T10:15:30Z",
                  "op_unique_carrier": "AA",
                  "origin": "JFK",
                  "dest": "LAX"
                }
                """;

        mockMvc.perform(post("/predict")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isBadRequest());
    }
}
