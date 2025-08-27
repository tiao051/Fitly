using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.IdentityModel.Tokens;
using auth_services.Models;

namespace auth_services.Helpers
{
    public class JwtTokenGenerator
    {
        public string GenerateToken(User user)
        {
            try
            {
                // Đọc các biến môi trường
                Console.WriteLine("JWT__KEY = " + Environment.GetEnvironmentVariable("JWT__KEY"));
                var key = Environment.GetEnvironmentVariable("JWT__KEY");
                if (string.IsNullOrWhiteSpace(key))
                    throw new Exception("JWT__KEY is missing or empty");

                var issuer = Environment.GetEnvironmentVariable("JWT__ISSUER");
                if (string.IsNullOrWhiteSpace(issuer))
                    throw new Exception("JWT__ISSUER is missing or empty");

                var audience = Environment.GetEnvironmentVariable("JWT__AUDIENCE");
                if (string.IsNullOrWhiteSpace(audience))
                    throw new Exception("JWT__AUDIENCE is missing or empty");

                var expiresRaw = Environment.GetEnvironmentVariable("JWT__EXPIRESINMINUTES");
                if (string.IsNullOrWhiteSpace(expiresRaw))
                    throw new Exception("JWT__EXPIRESINMINUTES is missing or empty");

                if (!int.TryParse(expiresRaw, out var expires))
                    throw new Exception("JWT__EXPIRESINMINUTES is not a valid integer");

                // Tạo claims
                var claims = new[]
                {
                    new Claim(ClaimTypes.NameIdentifier, user.UserId.ToString()),
                    new Claim(ClaimTypes.Email, user.Email),
                    new Claim(ClaimTypes.Role, user.Role)
                };

                // Tạo security key
                var securityKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(key));
                var credentials = new SigningCredentials(securityKey, SecurityAlgorithms.HmacSha256);

                // Tạo JWT
                var token = new JwtSecurityToken(
                    issuer: issuer,
                    audience: audience,
                    claims: claims,
                    expires: DateTime.UtcNow.AddMinutes(expires),
                    signingCredentials: credentials
                );
                var jwt = new JwtSecurityTokenHandler().WriteToken(token);

                Console.WriteLine("Generated JWT Token:");
                Console.WriteLine(jwt);
                return new JwtSecurityTokenHandler().WriteToken(token);
            }
            catch (Exception ex)
            {
                // Ghi log nếu cần
                Console.WriteLine($"JWT Generation Error: {ex.Message}");
                throw new Exception($"Failed to generate JWT: {ex.Message}");
            }
        }
    }
}
