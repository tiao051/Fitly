FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src

# Copy project file từ thư mục con
COPY auth_services/auth_services.csproj auth_services/
RUN dotnet restore "auth_services/auth_services.csproj"

# Copy toàn bộ source code
COPY auth_services/ auth_services/
WORKDIR "/src/auth_services"
RUN dotnet build "auth_services.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "auth_services.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "auth_services.dll"]