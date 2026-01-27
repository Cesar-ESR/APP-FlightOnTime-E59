package com.flightspredictor.flights.domain.prediction.stats;

import com.flightspredictor.flights.domain.prediction.ENUM.Prevision;
import com.flightspredictor.flights.domain.prediction.ENUM.Status;
import java.util.Map;

public record PredictionStatsResponse(
        long totalPredictions,
        Map<Status, Long> byStatus,
        Map<Prevision, Long> byPrevision,
        Double averageProbability
) {
}
