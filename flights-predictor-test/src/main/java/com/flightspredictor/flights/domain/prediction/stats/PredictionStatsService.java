package com.flightspredictor.flights.domain.prediction.stats;

import com.flightspredictor.flights.domain.prediction.ENUM.Prevision;
import com.flightspredictor.flights.domain.prediction.ENUM.Status;
import com.flightspredictor.flights.domain.prediction.entity.Prediction;
import com.flightspredictor.flights.domain.prediction.repository.PredictionRepository;
import java.util.DoubleSummaryStatistics;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.springframework.stereotype.Service;

@Service
public class PredictionStatsService {

    private final PredictionRepository predictionRepository;

    public PredictionStatsService(PredictionRepository predictionRepository) {
        this.predictionRepository = predictionRepository;
    }

    public PredictionStatsResponse getStats() {
        List<Prediction> predictions = predictionRepository.findAll();

        Map<Status, Long> byStatus = predictions.stream()
                .collect(Collectors.groupingBy(Prediction::getStatus, Collectors.counting()));

        Map<Prevision, Long> byPrevision = predictions.stream()
                .collect(Collectors.groupingBy(Prediction::getPrevision, Collectors.counting()));

        DoubleSummaryStatistics probabilityStats = predictions.stream()
                .map(Prediction::getProbability)
                .filter(value -> value != null)
                .mapToDouble(Double::doubleValue)
                .summaryStatistics();

        Double averageProbability = probabilityStats.getCount() > 0
                ? probabilityStats.getAverage()
                : null;

        return new PredictionStatsResponse(
                predictions.size(),
                byStatus,
                byPrevision,
                averageProbability
        );
    }
}
