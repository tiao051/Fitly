# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy csproj and restore
COPY ["body_analysis_backend.csproj", "./"]
RUN dotnet restore "./body_analysis_backend.csproj"

# Copy entire source and build
COPY . .
RUN dotnet publish "./body_analysis_backend.csproj" -c Release -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 80
ENTRYPOINT ["dotnet", "body_analysis_backend.dll"]
