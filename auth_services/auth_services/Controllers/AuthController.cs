using auth_services.DTOs;
using auth_services.Services;
using Microsoft.AspNetCore.Mvc;

namespace auth_services.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class AuthController : ControllerBase
    {
        private readonly IAuthService _authService;
        public AuthController(IAuthService authService) => _authService = authService;

        [HttpPost("register")]
        public async Task<IActionResult> Register([FromBody] RegisterRequest req)
        {
            Console.WriteLine("test123");
            try
            {
                var msg = await _authService.RegisterAsync(req);
                return Ok(new { message = msg });
            }
            catch (Exception ex)
            {
                return BadRequest(new { error = ex.Message });
            }
        }
        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] LoginRequest req)
        {
            Console.WriteLine("Login test");
            try
            {
                var result = await _authService.LoginAsync(req);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return Unauthorized(new { error = ex.Message });
            }
        }

    }
}
