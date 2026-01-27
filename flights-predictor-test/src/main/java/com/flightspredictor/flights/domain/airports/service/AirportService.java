package com.flightspredictor.flights.domain.airports.service;

import com.flightspredictor.flights.domain.airports.client.AirportApiClient;
import com.flightspredictor.flights.domain.airports.dto.AirportData;
import com.flightspredictor.flights.domain.airports.entity.Airport;
import com.flightspredictor.flights.domain.airports.exceptions.AirportNotFoundException;
import com.flightspredictor.flights.domain.airports.repository.AirportRepository;
import com.flightspredictor.flights.domain.airports.validations.IAirportsValidations;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class AirportService {

    private final AirportApiClient apiClient;
    private final AirportRepository repository;
    private final List<IAirportsValidations> validations;

      /**
     * Verifica si existe un aeropuerto registrado con el código IATA.
     *
     * La búsqueda se realiza ignorando mayúsculas y minúsculas.
     *
     * @param iata código IATA del aeropuerto
     * @return true si existe, false en caso contrario
     */
    public boolean existsAirportIata(String iata) {
        return repository.existsByAirportIataIgnoreCase(iata);
    }


    public Airport getAirport (String iata) {

        // Busca primero el aeropuerto en la base de datos si ya existe
        return repository.findByAirportIata(iata.toUpperCase())
                .orElseGet(() -> {

                    // Si no existe, trae los datos de la API
                    var apiResponse = apiClient.airportResponse(iata);

                    if (apiResponse == null) {
                        throw new AirportNotFoundException(
                                "Aeropuerto no encontrado con código IATA: " + iata
                        );
                    }

                    var data = new AirportData(apiResponse);
                    log.info("Airport API response for iata {}: {}", iata, apiResponse);
                    log.info("AirportData built from API response for iata {}: {}", iata, data);

                    // Se aplican las validaciones para los campos necesarios para el modelo
                    validations.forEach(v -> v.validate(data));

                    // Guarda en la base de datos y devuelve la información.
                    var airport = new Airport(data);
                    return repository.save(airport);

                });
    }

}
