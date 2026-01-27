package com.flightspredictor.flights.domain.prediction.stats;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/stats")
public class PredictionStatsController {

    private final PredictionStatsService predictionStatsService;

    public PredictionStatsController(PredictionStatsService predictionStatsService) {
        this.predictionStatsService = predictionStatsService;
    }

    @GetMapping
    public ResponseEntity<PredictionStatsResponse> getStats() {
        return ResponseEntity.ok(predictionStatsService.getStats());
    }
}
