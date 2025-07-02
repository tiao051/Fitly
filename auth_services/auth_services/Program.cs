using auth_services.Data;
using auth_services.Messaging;
using auth_services.Repositories;
using auth_services.Services;
using DotNetEnv;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using System.Security.Claims;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

// ✅ Load .env chỉ khi chạy local (không phải Docker)
if (!builder.Environment.IsProduction())
{
    Console.WriteLine("🧪 Loading .env file for local development...");
    DotNetEnv.Env.Load(); // tự động tìm file .env ở thư mục gốc
}

// ✅ Hàm tiện ích để lấy biến môi trường hoặc lỗi rõ ràng
string GetEnv(string key)
{
    var value = Environment.GetEnvironmentVariable(key);
    if (string.IsNullOrEmpty(value))
    {
        throw new Exception($"❌ ENV '{key}' is null. Check your .env file or docker-compose config.");
    }
    return value;
}

// ✅ Lấy thông tin JWT từ biến môi trường
var jwtKey = GetEnv("JWT__KEY");
var jwtIssuer = GetEnv("JWT__ISSUER");
var jwtAudience = GetEnv("JWT__AUDIENCE");

// ✅ Kết nối DB (PostgreSQL)
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("Default")));

// ✅ Đăng ký các services
builder.Services.AddSingleton<IRabbitMQPublisher, RabbitMQPublisher>();
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IAuthService, AuthService>();

// ✅ JWT Authentication
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

// ✅ Authorization
builder.Services.AddAuthorization();

// ✅ Swagger + API
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// ✅ Swagger trong môi trường dev
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// ✅ Middleware
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();
app.Run();
