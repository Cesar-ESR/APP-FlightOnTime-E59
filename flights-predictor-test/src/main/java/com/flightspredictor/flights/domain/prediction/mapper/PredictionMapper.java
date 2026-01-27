package com.flightspredictor.flights.domain.prediction.mapper;

import com.flightspredictor.flights.domain.prediction.ENUM.Prevision;
import com.flightspredictor.flights.domain.prediction.ENUM.Status;
import com.flightspredictor.flights.domain.prediction.dto.ModelPredictionResponse;
import com.flightspredictor.flights.domain.prediction.dto.PredictionResponse;
import org.springframework.stereotype.Component;

@Component
public class PredictionMapper {

    public ModelPredictionResponse mapToModelResponse(PredictionResponse response) {

        Prevision prevision = setPrevision(response.prevision());
        Status status = setStatus(response.confianza());

        return new ModelPredictionResponse(
                prevision,
                response.probabilidad(),
                status
        );
    }

    private Prevision setPrevision(String prevision) {
        if ("Retrasado".equalsIgnoreCase(prevision) || "Delayed".equalsIgnoreCase(prevision)) {
            return Prevision.DELAYED;
        }
        return Prevision.ON_TIME;
    }

    private Status setStatus(String confianza) {
        if ("Baja".equalsIgnoreCase(confianza)) {
            return Status.LOW;
        }
        if ("Media".equalsIgnoreCase(confianza)) {
            return Status.MEDIUM;
        }
        if ("Alta".equalsIgnoreCase(confianza)) {
            return Status.HIGH;
        }
        return Status.MEDIUM;
    }
}
