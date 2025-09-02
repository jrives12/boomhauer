package edu.citadel.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * Application config that serves up the configuration
 */
@Configuration
@EnableJpaRepositories(basePackages = "edu.citadel.dal")
@EntityScan("edu.citadel.dal.model")
public class ApplicationConfig {

    @Bean
    public ObjectMapper jacksonJsonObjectMapper() {
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false);
        return objectMapper;
    }

}