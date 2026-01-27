package com.flightspredictor.flights.domain.prediction.mapper;

import com.flightspredictor.flights.domain.prediction.dto.ModelPredictionRequest;
import com.flightspredictor.flights.domain.prediction.dto.PredictionRequest;
import org.junit.jupiter.api.Test;

import java.time.OffsetDateTime;
import java.time.ZoneOffset;

import static org.assertj.core.api.Assertions.assertThat;

class RequestMapperTest {

    @Test
    void mapToModelRequestBuildsExpectedPayload() {
        RequestMapper mapper = new RequestMapper();
        OffsetDateTime flightTime = OffsetDateTime.of(2000, 1, 1, 23, 0, 0, 0, ZoneOffset.UTC);
        PredictionRequest request = new PredictionRequest(
                flightTime,
                "AA",
                "JFK",
                "LAX"
        );

        ModelPredictionRequest result = mapper.mapToModelRequest(request, 1440.0);

        assertThat(result.year()).isEqualTo(2000);
        assertThat(result.month()).isEqualTo(1);
        assertThat(result.dayOfMonth()).isEqualTo(1);
        assertThat(result.dayOfWeek()).isEqualTo(flightTime.getDayOfWeek().getValue());
        assertThat(result.depHour()).isEqualTo(23);
        assertThat(result.depMinute()).isEqualTo(0);
        assertThat(result.schedMinuteOfDay()).isEqualTo(1380);
        assertThat(result.opUniqueCarrier()).isEqualTo("AA");
        assertThat(result.origin()).isEqualTo("JFK");
        assertThat(result.dest()).isEqualTo("LAX");
        assertThat(result.distance()).isEqualTo(1440.0);
        assertThat(result.temp()).isEqualTo(0.0);
        assertThat(result.windSpd()).isEqualTo(0.0);
        assertThat(result.precip1h()).isEqualTo(0.0);
        assertThat(result.climateSeverityIdx()).isEqualTo(0.0);
        assertThat(result.distMetKm()).isEqualTo(1440.0);
        assertThat(result.latitude()).isEqualTo(0.0);
        assertThat(result.longitude()).isEqualTo(0.0);
    }
}
