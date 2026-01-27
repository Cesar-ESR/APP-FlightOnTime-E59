package com.flightspredictor.flights.domain.prediction.service;

import com.flightspredictor.flights.domain.airports.entity.Airport;
import com.flightspredictor.flights.domain.prediction.ENUM.Prevision;
import com.flightspredictor.flights.domain.prediction.ENUM.Status;
import com.flightspredictor.flights.domain.prediction.client.PredictionApiClient;
import com.flightspredictor.flights.domain.prediction.dto.ModelPredictionRequest;
import com.flightspredictor.flights.domain.prediction.dto.ModelPredictionResponse;
import com.flightspredictor.flights.domain.prediction.dto.PredictionRequest;
import com.flightspredictor.flights.domain.prediction.dto.PredictionResponse;
import com.flightspredictor.flights.domain.prediction.entity.Prediction;
import com.flightspredictor.flights.domain.prediction.entity.Request;
import com.flightspredictor.flights.domain.prediction.mapper.PredictionMapper;
import com.flightspredictor.flights.domain.prediction.mapper.RequestMapper;
import com.flightspredictor.flights.domain.prediction.repository.RequestRepository;
import com.flightspredictor.flights.domain.prediction.util.GeoUtils;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyDouble;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class PredictionServiceTest {

    @Mock
    private AirportLookupService airportLookupService;

    @Mock
    private PredictionApiClient predictionClient;

    @Mock
    private PredictionMapper predictionMapper;

    @Mock
    private RequestMapper requestMapper;

    @Mock
    private RequestRepository requestRepository;

    @InjectMocks
    private PredictionService predictionService;

    @Captor
    private ArgumentCaptor<Request> requestCaptor;

    @Test
    void returnsExistingPredictionWithoutCallingModel() {
        PredictionRequest request = buildRequest();
        Airport origin = buildAirport("JFK", -73.0, 40.0);
        Airport dest = buildAirport("LAX", -118.0, 33.9);
        ModelPredictionResponse expected = new ModelPredictionResponse(
                Prevision.ON_TIME,
                0.2,
                Status.LOW
        );
        Request storedRequest = new Request(request, 0.0);
        Prediction prediction = new Prediction(expected, storedRequest);
        storedRequest.setPrediction(prediction);

        when(airportLookupService.getAirport("JFK")).thenReturn(Optional.of(origin));
        when(airportLookupService.getAirport("LAX")).thenReturn(Optional.of(dest));
        when(requestRepository.findByFlightDateTimeAndOpUniqueCarrierAndOriginAndDestAndDistance(
                eq(request.flightDateTime()),
                eq(request.opUniqueCarrier()),
                eq(request.origin()),
                eq(request.dest()),
                anyDouble()
        )).thenReturn(Optional.of(storedRequest));

        ModelPredictionResponse result = predictionService.predict(request);

        assertThat(result).isEqualTo(expected);
        verify(predictionClient, never()).predict(any());
        verify(requestRepository, never()).save(any());
        verify(requestMapper, never()).mapToModelRequest(any(), anyDouble());
        verify(predictionMapper, never()).mapToModelResponse(any());
    }

    @Test
    void callsModelAndPersistsNewPrediction() {
        PredictionRequest request = buildRequest();
        Airport origin = buildAirport("JFK", -73.0, 40.0);
        Airport dest = buildAirport("LAX", -118.0, 33.9);
        ModelPredictionRequest modelRequest = new ModelPredictionRequest(
                2030,
                1,
                1,
                3,
                10,
                15,
                615,
                "AA",
                "JFK",
                "LAX",
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0
        );
        PredictionResponse modelResponse = new PredictionResponse("Retrasado", 0.9, "Alta");
        ModelPredictionResponse mappedResponse = new ModelPredictionResponse(
                Prevision.DELAYED,
                0.9,
                Status.HIGH
        );

        when(airportLookupService.getAirport("JFK")).thenReturn(Optional.of(origin));
        when(airportLookupService.getAirport("LAX")).thenReturn(Optional.of(dest));
        when(requestRepository.findByFlightDateTimeAndOpUniqueCarrierAndOriginAndDestAndDistance(
                eq(request.flightDateTime()),
                eq(request.opUniqueCarrier()),
                eq(request.origin()),
                eq(request.dest()),
                anyDouble()
        )).thenReturn(Optional.empty());
        when(requestMapper.mapToModelRequest(eq(request), anyDouble())).thenReturn(modelRequest);
        when(predictionClient.predict(modelRequest)).thenReturn(modelResponse);
        when(predictionMapper.mapToModelResponse(modelResponse)).thenReturn(mappedResponse);

        ModelPredictionResponse result = predictionService.predict(request);

        assertThat(result).isEqualTo(mappedResponse);
        verify(requestRepository).save(requestCaptor.capture());

        double expectedDistance = GeoUtils.calculateDistance(
                origin.getLongitude(),
                origin.getLongitude(),
                dest.getLatitude(),
                dest.getLatitude()
        );

        assertThat(requestCaptor.getValue().getDistance()).isEqualTo(expectedDistance);
    }

    private PredictionRequest buildRequest() {
        return new PredictionRequest(
                OffsetDateTime.of(2030, 1, 1, 10, 15, 30, 0, ZoneOffset.UTC),
                "AA",
                "JFK",
                "LAX"
        );
    }

    private Airport buildAirport(String iata, double longitude, double latitude) {
        return new Airport(
                1L,
                iata,
                "Airport " + iata,
                "US",
                "City",
                longitude,
                latitude,
                0.0,
                "UTC",
                "https://maps.example.com/" + iata
        );
    }
}
