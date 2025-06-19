using auth_services.DTOs;
using auth_services.Models;
using auth_services.Repositories;
using auth_services.Messaging;

namespace auth_services.Services
{
    public class AuthService : IAuthService
    {
        private readonly IUserRepository _repo;
        private readonly IRabbitMQPublisher _publisher;

        public AuthService(IUserRepository repo, IRabbitMQPublisher publisher)
        {
            _repo = repo;
            _publisher = publisher;
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
    }
}