package com.flightspredictor.flights.infra.weather.client;

import com.flightspredictor.flights.infra.weather.config.WeatherConfig;
import com.flightspredictor.flights.infra.weather.dto.external.LocationResponse;
import com.flightspredictor.flights.infra.weather.dto.external.WeatherResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import java.time.Duration;

/**
 * Cliente HTTP para realizar llamadas a las API meteorológicas de Open-Meteo
 * Encapsula toda la lógica de comunicación HTTP y manejo de errores
 */
@Component
public class WeatherApiClient {
    
    private final WebClient webClient;
    
    /**
     * Constructor que inyecta el WebClient configurado específicamente para weather
     */
    public WeatherApiClient(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.build();
    }
    
    /**
     * Obtiene las coordenadas geográficas de una ciudad usando la API de geocodificación
     * 
     * @param cityName nombre de la ciudad a buscar
     * @return LocationResponse con los datos de ubicación o null si no se encuentra
     * @throws RuntimeException sí hay error en la comunicación con la API
     */
    public LocationResponse getLocationData(String cityName) {
        try {
            // Construye la URL usando la configuración centralizada
            String url = WeatherConfig.buildGeocodingUrl(cityName);
            
            // Realiza la llamada HTTP GET de forma reactiva
            return webClient.get()
                    .uri(url)                                           // URL de la API de geocodificación
                    .retrieve()                                         // Ejecuta la petición
                    .bodyToMono(LocationResponse.class)                 // Convierte respuesta a DTO
                    .timeout(Duration.ofSeconds(WeatherConfig.CONNECTION_TIMEOUT_SECONDS)) // Timeout
                    .block();                                           // Convierte de reactivo a síncrono
                    
        } catch (WebClientResponseException e) {
            // Manejo específico de errores HTTP (4xx, 5xx)
            throw new RuntimeException("Error al obtener datos de ubicación para: " + cityName + 
                                     ". Código de error: " + e.getStatusCode(), e);
        } catch (Exception e) {
            // Manejo de otros errores (timeout, conexión, etc.)
            throw new RuntimeException("Error de conexión al obtener ubicación de: " + cityName, e);
        }
    }
    
    /**
     * Obtiene los datos meteorológicos actuales para unas coordenadas específicas
     * 
     * @param latitude latitud de la ubicación
     * @param longitude longitud de la ubicación
     * @return WeatherResponse con los datos meteorológicos actuales
     * @throws RuntimeException sí hay error en la comunicación con la API
     */
    public WeatherResponse getWeatherData(double latitude, double longitude) {
        try {
            // Construye la URL usando la configuración centralizada
            String url = WeatherConfig.buildWeatherUrl(latitude, longitude);
            
            // Realiza la llamada HTTP GET de forma reactiva
            return webClient.get()
                    .uri(url)                                           // URL de la API meteorológica
                    .retrieve()                                         // Ejecuta la petición
                    .bodyToMono(WeatherResponse.class)                  // Convierte respuesta a DTO
                    .timeout(Duration.ofSeconds(WeatherConfig.READ_TIMEOUT_SECONDS)) // Timeout más largo para datos meteorológicos
                    .block();                                           // Convierte de reactivo a síncrono
                    
        } catch (WebClientResponseException e) {
            // Manejo específico de errores HTTP
            throw new RuntimeException("Error al obtener datos meteorológicos para coordenadas: " + 
                                     latitude + ", " + longitude + ". Código de error: " + e.getStatusCode(), e);
        } catch (Exception e) {
            // Manejo de otros errores
            throw new RuntimeException("Error de conexión al obtener datos meteorológicos para: " + 
                                     latitude + ", " + longitude, e);
        }
    }
}