using AuthServices.Helpers;
using AuthServices.Models;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using Xunit;

namespace AuthServices.Tests.Helpers
{
    public class JwtTokenGeneratorTests
    {
        [Fact]
        public void GenerateToken_ValidUser_ReturnsValidJwtToken()
        {
            // Arrange
            Environment.SetEnvironmentVariable("JWT__KEY", "this-is-a-very-secure-key-with-minimum-32-characters-long");
            Environment.SetEnvironmentVariable("JWT__ISSUER", "test-issuer");
            Environment.SetEnvironmentVariable("JWT__AUDIENCE", "test-audience");
            Environment.SetEnvironmentVariable("JWT__EXPIRESINMINUTES", "60");

            var generator = new JwtTokenGenerator();
            var user = new User
            {
                UserId = Guid.NewGuid(),
                Email = "test@example.com",
                Role = "User"
            };

            // Act
            var token = generator.GenerateToken(user);

            // Assert
            Assert.NotNull(token);
            Assert.NotEmpty(token);
            
            // Verify token can be parsed
            var tokenHandler = new JwtSecurityTokenHandler();
            var jsonToken = tokenHandler.ReadJwtToken(token);
            
            Assert.Equal("test-issuer", jsonToken.Issuer);
            Assert.Equal("test-audience", jsonToken.Audiences.First());
            Assert.Contains(jsonToken.Claims, c => c.Type == ClaimTypes.Email && c.Value == "test@example.com");
            Assert.Contains(jsonToken.Claims, c => c.Type == ClaimTypes.Role && c.Value == "User");
        }

        [Fact]
        public void GenerateToken_MissingJwtKey_ThrowsException()
        {
            // Arrange
            Environment.SetEnvironmentVariable("JWT__KEY", null);
            var generator = new JwtTokenGenerator();
            var user = new User { Email = "test@example.com", Role = "User" };

            // Act & Assert
            var exception = Assert.Throws<Exception>(() => generator.GenerateToken(user));
            Assert.Contains("JWT__KEY is missing or empty", exception.Message);
        }

        [Fact] 
        public void GenerateToken_MissingIssuer_ThrowsException()
        {
            // Arrange
            Environment.SetEnvironmentVariable("JWT__KEY", "this-is-a-very-secure-key-with-minimum-32-characters-long");
            Environment.SetEnvironmentVariable("JWT__ISSUER", null);
            var generator = new JwtTokenGenerator();
            var user = new User { Email = "test@example.com", Role = "User" };

            // Act & Assert
            var exception = Assert.Throws<Exception>(() => generator.GenerateToken(user));
            Assert.Contains("JWT__ISSUER is missing or empty", exception.Message);
        }

        [Fact]
        public void GenerateToken_InvalidExpiresInMinutes_ThrowsException()
        {
            // Arrange
            Environment.SetEnvironmentVariable("JWT__KEY", "this-is-a-very-secure-key-with-minimum-32-characters-long");
            Environment.SetEnvironmentVariable("JWT__ISSUER", "test-issuer");
            Environment.SetEnvironmentVariable("JWT__AUDIENCE", "test-audience");
            Environment.SetEnvironmentVariable("JWT__EXPIRESINMINUTES", "invalid-number");

            var generator = new JwtTokenGenerator();
            var user = new User { Email = "test@example.com", Role = "User" };

            // Act & Assert
            var exception = Assert.Throws<Exception>(() => generator.GenerateToken(user));
            Assert.Contains("JWT__EXPIRESINMINUTES is not a valid integer", exception.Message);
        }
    }
}
