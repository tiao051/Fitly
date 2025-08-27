using AuthServices.Controllers;
using AuthServices.DTOs;
using AuthServices.Services;
using Microsoft.AspNetCore.Mvc;
using Moq;
using Xunit;

namespace AuthServices.Tests.Controllers
{
    public class AuthControllerTests
    {
        private readonly Mock<IAuthService> _mockAuthService;
        private readonly AuthController _controller;

        public AuthControllerTests()
        {
            _mockAuthService = new Mock<IAuthService>();
            _controller = new AuthController(_mockAuthService.Object);
        }

        [Fact]
        public async Task Register_ValidRequest_ReturnsOkWithSuccessMessage()
        {
            // Arrange
            var request = new RegisterRequest
            {
                Email = "test@example.com",
                Password = "password123",
                ConfirmPassword = "password123",
                Role = "User"
            };

            _mockAuthService.Setup(x => x.RegisterAsync(request))
                           .ReturnsAsync("User registered successfully");

            // Act
            var result = await _controller.Register(request);

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var response = okResult.Value;
            
            // Check anonymous object properties
            var messageProperty = response?.GetType().GetProperty("message");
            Assert.NotNull(messageProperty);
            var messageValue = messageProperty.GetValue(response)?.ToString();
            Assert.Equal("User registered successfully", messageValue);
            
            _mockAuthService.Verify(x => x.RegisterAsync(request), Times.Once);
        }

        [Fact]
        public async Task Register_ServiceThrowsException_ReturnsBadRequest()
        {
            // Arrange
            var request = new RegisterRequest
            {
                Email = "test@example.com",
                Password = "password123",
                ConfirmPassword = "different-password",
                Role = "User"
            };

            _mockAuthService.Setup(x => x.RegisterAsync(request))
                           .ThrowsAsync(new Exception("Passwords do not match."));

            // Act
            var result = await _controller.Register(request);

            // Assert
            var badRequestResult = Assert.IsType<BadRequestObjectResult>(result);
            var response = badRequestResult.Value;
            
            // Check anonymous object properties  
            var errorProperty = response?.GetType().GetProperty("error");
            Assert.NotNull(errorProperty);
            var errorValue = errorProperty.GetValue(response)?.ToString();
            Assert.Equal("Passwords do not match.", errorValue);
        }

        [Fact]
        public async Task Login_ValidCredentials_ReturnsOkWithToken()
        {
            // Arrange
            var request = new LoginRequest
            {
                Email = "test@example.com",
                Password = "password123"
            };

            var loginResponse = new LoginResponse
            {
                Token = "valid-jwt-token",
                Email = "test@example.com",
                Role = "User"
            };

            _mockAuthService.Setup(x => x.LoginAsync(request))
                           .ReturnsAsync(loginResponse);

            // Act
            var result = await _controller.Login(request);

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var response = Assert.IsType<LoginResponse>(okResult.Value);
            Assert.Equal(loginResponse.Token, response.Token);
            Assert.Equal(loginResponse.Email, response.Email);
            Assert.Equal(loginResponse.Role, response.Role);
            _mockAuthService.Verify(x => x.LoginAsync(request), Times.Once);
        }

        [Fact]
        public async Task Login_InvalidCredentials_ReturnsUnauthorized()
        {
            // Arrange
            var request = new LoginRequest
            {
                Email = "test@example.com",
                Password = "wrong-password"
            };

            _mockAuthService.Setup(x => x.LoginAsync(request))
                           .ThrowsAsync(new Exception("Invalid email or password."));

            // Act
            var result = await _controller.Login(request);

            // Assert
            var unauthorizedResult = Assert.IsType<UnauthorizedObjectResult>(result);
            var response = unauthorizedResult.Value;
            
            // Check anonymous object properties
            var errorProperty = response?.GetType().GetProperty("error");
            Assert.NotNull(errorProperty);
            var errorValue = errorProperty.GetValue(response)?.ToString();
            Assert.Equal("Invalid email or password.", errorValue);
        }

        [Fact]
        public async Task Login_ServiceThrowsGeneralException_ReturnsUnauthorized()
        {
            // Arrange
            var request = new LoginRequest
            {
                Email = "test@example.com",
                Password = "password123"
            };

            _mockAuthService.Setup(x => x.LoginAsync(request))
                           .ThrowsAsync(new Exception("Database connection failed"));

            // Act
            var result = await _controller.Login(request);

            // Assert
            var unauthorizedResult = Assert.IsType<UnauthorizedObjectResult>(result);
            var response = unauthorizedResult.Value;
            
            // Check anonymous object properties
            var errorProperty = response?.GetType().GetProperty("error");
            Assert.NotNull(errorProperty);
            var errorValue = errorProperty.GetValue(response)?.ToString();
            Assert.Equal("Database connection failed", errorValue);
        }
    }
}
