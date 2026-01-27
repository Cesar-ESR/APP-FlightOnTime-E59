package com.flightspredictor.flights.domain.airports.client;

import com.flightspredictor.flights.domain.airports.domain.AirportResponse;
import com.flightspredictor.flights.domain.airports.exceptions.ExternalApiException;
import com.flightspredictor.flights.domain.airports.util.AirportUrlBuilder;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpHeaders;


@Component
@RequiredArgsConstructor
public class AirportApiClient {

    private final RestTemplate restTemplate;

    @Value("${api.market.key:}")
    private String apiKey;

    public AirportResponse airportResponse (String iata) {

        String url = AirportUrlBuilder.buildAirportUrl(iata);

        HttpHeaders headers = new HttpHeaders();
        headers.set("x-api-market-key", apiKey);
        HttpEntity<Void> entity = new HttpEntity<>(headers);

        try {
            return restTemplate.exchange(url, HttpMethod.GET, entity, AirportResponse.class).getBody();
        } catch (RestClientException ex) {
            throw new ExternalApiException("Error al consultar la API de aeropuertos.", ex);
        }
    }
}
