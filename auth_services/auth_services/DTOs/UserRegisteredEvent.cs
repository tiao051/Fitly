namespace auth_services.DTOs
{
    public class UserRegisteredEvent
    {
        public Guid UserId { get; set; }
        public string Email { get; set; } = null!;
        public string Role { get; set; } = "User";
    }   
}
