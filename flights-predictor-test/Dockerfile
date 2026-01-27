#MODELO
FROM eclipse-temurin:17.0.17_10-jdk AS build

#CREAR DIRECTORIO
WORKDIR /backend-api

#COPIAR DEPENDENCIAS
COPY pom.xml /backend-api
COPY mvnw /backend-api
COPY .mvn /backend-api/.mvn

#PERMISOS
RUN sed -i 's/\r$//' mvnw
RUN chmod +x mvnw

#DESCARGAR DEPENDECIAS
RUN /backend-api/mvnw dependency:go-offline

#COPIAR CODIGO FUENTE
COPY src /backend-api/src

#CONSTRUIR JAR
RUN ./mvnw clean package -DskipTests

#RUNTIME
FROM eclipse-temurin:17-jre

#
WORKDIR /backend-api

# Copiar el jar generado
COPY --from=build /backend-api/target/*.jar /backend-api/app.jar

#EXPONER PUERTO
EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]

