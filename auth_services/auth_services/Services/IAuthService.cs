using auth_services.DTOs;

namespace auth_services.Services
{
    public interface IAuthService
    {
        Task<string> RegisterAsync(RegisterRequest request);
    }
}
