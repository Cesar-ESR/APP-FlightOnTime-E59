package com.flightspredictor.flights.infra.weather.client;

import com.flightspredictor.flights.infra.weather.config.WeatherConfig;
import com.flightspredictor.flights.infra.weather.dto.external.WeatherApiResponse;
import java.time.Duration;
import java.util.Locale;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.util.UriComponentsBuilder;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

@Component
public class WeatherFallbackClient {

    private final WebClient webClient;
    private final String apiKey;
    private final String baseUrl;

    public WeatherFallbackClient(
            WebClient.Builder webClientBuilder,
            @Value("${weather.api.key:}") String apiKey,
            @Value("${weather.api.base-url:https://api.weatherapi.com/v1/current.json}") String baseUrl
    ) {
        this.webClient = webClientBuilder.build();
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
    }

    public WeatherApiResponse getWeatherForCity(String cityName) {
        ensureApiKey();

        try {
            String uri = UriComponentsBuilder.fromHttpUrl(baseUrl)
                    .queryParam("key", apiKey)
                    .queryParam("q", cityName)
                    .queryParam("aqi", "no")
                    .toUriString();

            return webClient.get()
                    .uri(uri)
                    .retrieve()
                    .bodyToMono(WeatherApiResponse.class)
                    .timeout(Duration.ofSeconds(WeatherConfig.READ_TIMEOUT_SECONDS))
                    .block();
        } catch (WebClientResponseException e) {
            throw new RuntimeException("Error al obtener datos meteorológicos (fallback) para: " + cityName, e);
        } catch (Exception e) {
            throw new RuntimeException("Error de conexión con proveedor fallback para: " + cityName, e);
        }
    }

    public WeatherApiResponse getWeatherForCoordinates(double latitude, double longitude) {
        ensureApiKey();

        String query = String.format(Locale.US, "%.6f,%.6f", latitude, longitude);

        try {
            String uri = UriComponentsBuilder.fromHttpUrl(baseUrl)
                    .queryParam("key", apiKey)
                    .queryParam("q", query)
                    .queryParam("aqi", "no")
                    .toUriString();

            return webClient.get()
                    .uri(uri)
                    .retrieve()
                    .bodyToMono(WeatherApiResponse.class)
                    .timeout(Duration.ofSeconds(WeatherConfig.READ_TIMEOUT_SECONDS))
                    .block();
        } catch (WebClientResponseException e) {
            throw new RuntimeException("Error al obtener datos meteorológicos (fallback) para coordenadas: " +
                    latitude + ", " + longitude, e);
        } catch (Exception e) {
            throw new RuntimeException("Error de conexión con proveedor fallback para coordenadas: " +
                    latitude + ", " + longitude, e);
        }
    }

    private void ensureApiKey() {
        if (apiKey == null || apiKey.isBlank()) {
            throw new IllegalStateException("weather.api.key no está configurada para el proveedor fallback.");
        }
    }
}
