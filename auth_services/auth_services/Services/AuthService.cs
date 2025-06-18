using auth_services.DTOs;
using auth_services.Models;
using auth_services.Repositories;

namespace auth_services.Services
{

    public class AuthService : IAuthService
    {
        private readonly IUserRepository _repo;
        public AuthService(IUserRepository repo) => _repo = repo;

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
            return "User registered successfully";
        }
    }
}
