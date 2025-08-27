using AuthServices.DTOs;
using AuthServices.Models;
using AuthServices.Repositories;
using AuthServices.Services;
using AuthServices.Messaging;
using Microsoft.Extensions.Configuration;
using Moq;
using Xunit;

namespace AuthServices.Tests.Services
{
    public class AuthServiceTests
    {
        private readonly Mock<IUserRepository> _mockUserRepository;
        private readonly Mock<IRabbitMQPublisher> _mockRabbitMQPublisher;
        private readonly Mock<IConfiguration> _mockConfiguration;
        private readonly AuthService _authService;

        public AuthServiceTests()
        {
            _mockUserRepository = new Mock<IUserRepository>();
            _mockRabbitMQPublisher = new Mock<IRabbitMQPublisher>();
            _mockConfiguration = new Mock<IConfiguration>();
            _authService = new AuthService(_mockUserRepository.Object, _mockRabbitMQPublisher.Object, _mockConfiguration.Object);
        }

        [Fact]
        public async Task RegisterAsync_ValidRequest_ReturnsSuccessMessage()
        {
            // Arrange
            var request = new RegisterRequest
            {
                Email = "newuser@example.com",
                Password = "password123",
                ConfirmPassword = "password123",
                Role = "User"
            };

            _mockUserRepository.Setup(x => x.GetByEmailAsync(request.Email))
                              .ReturnsAsync((User?)null); // Email doesn't exist

            _mockUserRepository.Setup(x => x.AddAsync(It.IsAny<User>()))
                              .Returns(Task.CompletedTask);

            // Act
            var result = await _authService.RegisterAsync(request);

            // Assert
            Assert.Equal("User registered successfully", result);
            _mockUserRepository.Verify(x => x.GetByEmailAsync(request.Email), Times.Once);
            _mockUserRepository.Verify(x => x.AddAsync(It.IsAny<User>()), Times.Once);
        }

        [Fact]
        public async Task RegisterAsync_PasswordsDoNotMatch_ThrowsException()
        {
            // Arrange
            var request = new RegisterRequest
            {
                Email = "user@example.com",
                Password = "password123",
                ConfirmPassword = "different-password",
                Role = "User"
            };

            // Act & Assert
            var exception = await Assert.ThrowsAsync<Exception>(() => _authService.RegisterAsync(request));
            Assert.Equal("Passwords do not match.", exception.Message);
        }

        [Fact]
        public async Task RegisterAsync_EmailAlreadyExists_ThrowsException()
        {
            // Arrange
            var request = new RegisterRequest
            {
                Email = "existing@example.com",
                Password = "password123",
                ConfirmPassword = "password123",
                Role = "User"
            };

            var existingUser = new User
            {
                UserId = Guid.NewGuid(),
                Email = "existing@example.com",
                PasswordHash = "hashed-password",
                Role = "User"
            };

            _mockUserRepository.Setup(x => x.GetByEmailAsync(request.Email))
                              .ReturnsAsync(existingUser);

            // Act & Assert
            var exception = await Assert.ThrowsAsync<Exception>(() => _authService.RegisterAsync(request));
            Assert.Equal("Email already registered.", exception.Message);
            _mockUserRepository.Verify(x => x.GetByEmailAsync(request.Email), Times.Once);
            _mockUserRepository.Verify(x => x.AddAsync(It.IsAny<User>()), Times.Never);
        }

        [Fact]
        public async Task LoginAsync_ValidCredentials_ReturnsLoginResponse()
        {
            // Arrange
            Environment.SetEnvironmentVariable("JWT__KEY", "this-is-a-very-secure-key-with-minimum-32-characters-long");
            Environment.SetEnvironmentVariable("JWT__ISSUER", "test-issuer");
            Environment.SetEnvironmentVariable("JWT__AUDIENCE", "test-audience");
            Environment.SetEnvironmentVariable("JWT__EXPIRESINMINUTES", "60");

            var request = new LoginRequest
            {
                Email = "user@example.com",
                Password = "password123"
            };

            var user = new User
            {
                UserId = Guid.NewGuid(),
                Email = "user@example.com",
                PasswordHash = BCrypt.Net.BCrypt.HashPassword("password123"),
                Role = "User"
            };

            _mockUserRepository.Setup(x => x.GetByEmailAsync(request.Email))
                              .ReturnsAsync(user);

            // Act
            var result = await _authService.LoginAsync(request);

            // Assert
            Assert.NotNull(result);
            Assert.Equal(user.Email, result.Email);
            Assert.Equal(user.Role, result.Role);
            Assert.NotNull(result.Token);
            Assert.NotEmpty(result.Token);
            _mockUserRepository.Verify(x => x.GetByEmailAsync(request.Email), Times.Once);
        }

        [Fact]
        public async Task LoginAsync_UserNotFound_ThrowsException()
        {
            // Arrange
            var request = new LoginRequest
            {
                Email = "nonexistent@example.com",
                Password = "password123"
            };

            _mockUserRepository.Setup(x => x.GetByEmailAsync(request.Email))
                              .ReturnsAsync((User?)null);

            // Act & Assert
            var exception = await Assert.ThrowsAsync<Exception>(() => _authService.LoginAsync(request));
            Assert.Equal("Invalid email or password.", exception.Message);
        }

        [Fact]
        public async Task LoginAsync_InvalidPassword_ThrowsException()
        {
            // Arrange
            var request = new LoginRequest
            {
                Email = "user@example.com",
                Password = "wrong-password"
            };

            var user = new User
            {
                UserId = Guid.NewGuid(),
                Email = "user@example.com",
                PasswordHash = BCrypt.Net.BCrypt.HashPassword("correct-password"),
                Role = "User"
            };

            _mockUserRepository.Setup(x => x.GetByEmailAsync(request.Email))
                              .ReturnsAsync(user);

            // Act & Assert
            var exception = await Assert.ThrowsAsync<Exception>(() => _authService.LoginAsync(request));
            Assert.Equal("Invalid email or password.", exception.Message);
        }
    }
}
