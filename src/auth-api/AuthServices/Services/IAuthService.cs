using AuthServices.DTOs;

namespace AuthServices.Services
{
    public interface IAuthService
    {
        Task<string> RegisterAsync(RegisterRequest request);
        Task<LoginResponse> LoginAsync(LoginRequest request);
    }
}
