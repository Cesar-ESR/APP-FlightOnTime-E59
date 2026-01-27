package com.flightspredictor.flights.domain.prediction.mapper;

import com.flightspredictor.flights.domain.prediction.dto.ModelPredictionRequest;
import com.flightspredictor.flights.domain.prediction.dto.PredictionRequest;
import org.springframework.stereotype.Component;

import java.time.OffsetDateTime;

@Component
public class RequestMapper {
    /**
     * Metodo para mapear los datos que ingresa el usuario hacia el dto que recibe el modelo
     */
    public ModelPredictionRequest mapToModelRequest(PredictionRequest dto, double distance) {
        OffsetDateTime flightDateTime = dto.flightDateTime();

        int schedMinuteOfDay = (flightDateTime.getHour() * 60) + flightDateTime.getMinute();

        return new ModelPredictionRequest(
                flightDateTime.getYear(),
                flightDateTime.getMonthValue(),
                flightDateTime.getDayOfMonth(),
                flightDateTime.getDayOfWeek().getValue(),
                flightDateTime.getHour(),
                flightDateTime.getMinute(),
                schedMinuteOfDay,
                dto.opUniqueCarrier(),
                dto.origin(),
                dto.dest(),
                distance,
                0.0,
                0.0,
                0.0,
                0.0,
                distance,
                0.0,
                0.0
        );
    }
}
