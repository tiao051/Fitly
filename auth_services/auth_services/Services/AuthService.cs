using auth_services.DTOs;
using auth_services.Models;
using auth_services.Repositories;
using auth_services.Messaging;
using auth_services.Helpers;

namespace auth_services.Services
{
    public class AuthService : IAuthService
    {
        private readonly IUserRepository _repo;
        private readonly IRabbitMQPublisher _publisher;
        private readonly IConfiguration _config;

        public AuthService(IUserRepository repo, IRabbitMQPublisher publisher, IConfiguration config)
        {
            _repo = repo;
            _publisher = publisher;
            _config = config;
        }

        public async Task<string> RegisterAsync(RegisterRequest request)
        {
            if (request.Password != request.ConfirmPassword)
                throw new Exception("Passwords do not match.");

            if (await _repo.GetByEmailAsync(request.Email) is not null)
                throw new Exception("Email already registered.");

            var user = new User
            {
                Email = request.Email,
                PasswordHash = BCrypt.Net.BCrypt.HashPassword(request.Password),
                Role = request.Role
            };

            await _repo.AddAsync(user);

            // Publish message to RabbitMQ
            var userRegisteredEvent = new
            {
                UserId = user.UserId,
                Email = user.Email,
                RegisteredAt = DateTime.UtcNow
            };

            await _publisher.PublishAsync(userRegisteredEvent, "user-registered");

            return "User registered successfully";
        }
        public async Task<LoginResponse> LoginAsync(LoginRequest request)
        {
            var user = await _repo.GetByEmailAsync(request.Email);
            if (user == null || !BCrypt.Net.BCrypt.Verify(request.Password, user.PasswordHash))
                throw new Exception("Invalid email or password.");

            var token = new JwtTokenGenerator().GenerateToken(user);

            return new LoginResponse
            {
                Token = token,
                Email = user.Email,
                Role = user.Role
            };
        }
    }
}