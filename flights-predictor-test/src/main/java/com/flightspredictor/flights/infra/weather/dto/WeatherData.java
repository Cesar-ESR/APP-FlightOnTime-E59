package com.flightspredictor.flights.infra.weather.dto;

import java.time.LocalDateTime;

/**
 * DTO interno que representa los datos meteorológicos procesados para uso en la aplicación
 * Este DTO abstrae los detalles de la API externa y proporciona una interfaz limpia
 */
public record WeatherData(
        String cityName,                    // Nombre de la ciudad consultada
        Double latitude,                    // Coordenada de latitud
        Double longitude,                   // Coordenada de longitud
        LocalDateTime measurementTime,      // Momento de la medición convertido a LocalDateTime
        Double temperatureCelsius,          // Temperatura en grados Celsius
        Long humidityPercentage,            // Humedad relativa en porcentaje (0-100)
        Double windSpeedKmh,                // Velocidad del viento en kilómetros por hora
        Double pressure,                   // Presión atmosférica en hPa
        String country                      // País donde se encuentra la ciudad
) {
    
    /**
     * Método de conveniencia para obtener una descripción textual del clima
     * @return String con resumen de las condiciones meteorológicas
     */
    public String getWeatherSummary() {
        return String.format("Temperatura: %.1f°C, Humedad: %d%%, Viento: %.1f km/h", 
                           temperatureCelsius, humidityPercentage, windSpeedKmh);
    }
    
    /**
     * Método para determinar si las condiciones son favorables para vuelos
     * @return true si las condiciones son buenas, false si hay condiciones adversas
     */
    public boolean isFavorableForFlights() {
        // Condiciones básicas: temperatura entre -40 y 50° C, viento menor a 50 km/h
        return temperatureCelsius >= -40.0 && temperatureCelsius <= 50.0 && windSpeedKmh < 50.0;
    }
}
