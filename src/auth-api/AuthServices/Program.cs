using AuthServices.Data;
using AuthServices.Messaging;
using AuthServices.Repositories;
using AuthServices.Services;
using DotNetEnv;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using System.Security.Claims;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

// Load .env file for local development (not in Docker)
if (!builder.Environment.IsProduction())
{
    Console.WriteLine("Loading .env file for local development...");
    DotNetEnv.Env.Load(); // automatically find .env file in root directory
}

// Utility function to get environment variable or throw clear error
string GetEnv(string key)
{
    var value = Environment.GetEnvironmentVariable(key);
    if (string.IsNullOrEmpty(value))
    {
        throw new Exception($"ENV '{key}' is null. Check your .env file or docker-compose config.");
    }
    return value;
}

// Get JWT information from environment variables
var jwtKey = GetEnv("JWT__KEY");
var jwtIssuer = GetEnv("JWT__ISSUER");
var jwtAudience = GetEnv("JWT__AUDIENCE");

// Database connection (PostgreSQL)
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("Default")));

// Register services
builder.Services.AddSingleton<IRabbitMQPublisher, RabbitMQPublisher>();
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IAuthService, AuthService>();

// JWT Authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            RoleClaimType = ClaimTypes.Role,
            NameClaimType = ClaimTypes.NameIdentifier,

            ValidIssuer = jwtIssuer,
            ValidAudience = jwtAudience,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey))
        };
    });

// Authorization
builder.Services.AddAuthorization();

// Swagger + API
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Swagger in development environment
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// Middleware
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();
app.Run();
