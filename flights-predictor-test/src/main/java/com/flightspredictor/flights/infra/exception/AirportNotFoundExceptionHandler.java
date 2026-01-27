package com.flightspredictor.flights.infra.exception;

import java.util.Map;

import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;

@ControllerAdvice
@Order(Ordered.HIGHEST_PRECEDENCE)
public class AirportNotFoundExceptionHandler {

    @ExceptionHandler(NullPointerException.class)
    public ResponseEntity<Object> handlerAirportNotFound(NullPointerException ex) {
        if (isAirportMappingNullPointer(ex)) {
            return new ResponseEntity<>(
                    Map.of(
                            "Estado", HttpStatus.NOT_FOUND.value(),
                            "Error", "AEROPUERTO NO ENCONTRADO",
                            "Mensaje", "El código IATA no existe o no está disponible."
                    ),
                    HttpStatus.NOT_FOUND
            );
        }

        return new ResponseEntity<>(
                Map.of(
                        "Estado", HttpStatus.INTERNAL_SERVER_ERROR.value(),
                        "Error", "INTERNAL ERROR",
                        "Mensaje", "Error inesperado"
                ),
                HttpStatus.INTERNAL_SERVER_ERROR
        );
    }

    private boolean isAirportMappingNullPointer(NullPointerException ex) {
        for (StackTraceElement element : ex.getStackTrace()) {
            String className = element.getClassName();
            if (className.startsWith("com.flightspredictor.flights.domain.airports")) {
                return true;
            }
        }
        return false;
    }
}
